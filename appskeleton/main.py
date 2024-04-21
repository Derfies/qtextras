import logging
import sys
from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import (
    QAction,
    QIcon,
)
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMessageBox,
)

from appskeleton.document import Document
from appskeleton.widgetmanager import WidgetManager


logger = logging.getLogger(__name__)


DEFAULT_COMPANY_NAME = 'Enron'
DEFAULT_APP_NAME = 'Application Skeleton'


class AppSkeleton(QApplication):

    update = pyqtSignal()


class MainWindow(QMainWindow):

    def __init__(self, company_name: str, app_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app_name = app_name

        self._create_menu_bar()
        self._create_actions()
        self._add_actions_to_menu_bar()
        self._connect_actions()

        self._widget_manager = WidgetManager(company_name, self.app_name)
        self._widget_manager.register_widget('main_window', self)

        QApplication.instance().update.connect(self.on_update)

        # Default state is an empty document.
        self.doc = self.create_document()
        self.doc.on_refresh()

    @property
    def icons_path(self) -> Path:
        return Path(__file__).parent.joinpath('data', 'icons')

    def get_icon(self, file_name: str) -> QIcon:
        return QIcon(str(self.icons_path.joinpath(file_name)))

    def showEvent(self, event):
        self._widget_manager.load_settings()

    def closeEvent(self, event):
        self._widget_manager.save_settings()

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        self.file_menu = menu_bar.addMenu('&File')
        self.edit_menu = menu_bar.addMenu('&Edit')

    def _create_actions(self):

        # File actions.
        self.new_action = QAction(self.get_icon('document.png'), '&New', self)
        self.open_action = QAction(self.get_icon('folder-open.png'), '&Open...', self)
        self.save_action = QAction(self.get_icon('disk.png'), '&Save', self)
        self.save_as_action = QAction(self.get_icon('disk.png'), '&Save As...', self)
        self.exit_action = QAction(self.get_icon('door-open-out.png'), '&Exit', self)

        # Edit actions.
        self.undo_action = QAction(self.get_icon('arrow-turn.png'), '&Undo', self)
        self.redo_action = QAction(self.get_icon('arrow-turn-180-left.png'), '&Redo', self)

    def _add_actions_to_menu_bar(self):

        # File actions.
        self.file_menu.addAction(self.new_action)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_as_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        # Edit actions.
        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.redo_action)

    def _connect_actions(self):
        self.new_action.triggered.connect(self.on_new)
        self.open_action.triggered.connect(self.on_open)
        self.save_action.triggered.connect(self.on_save)
        self.save_as_action.triggered.connect(self.on_save_as)
        self.exit_action.triggered.connect(self.on_exit)

    def _check_for_save(self):
        if self.doc.dirty:
            msg = f'The document "{self.doc.title}" was modified after last save.\nSave changes before continuing?'
            result = QMessageBox.warning(
                self,
                'Save Changes?',
                msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.No,
            )
            if result == QMessageBox.StandardButton.Yes:
                self.on_save()
            elif result == QMessageBox.StandardButton.Cancel:
                return False
        return True

    def on_new(self):
        if not self._check_for_save():
            return
        self.doc = self.create_document()
        self.doc.on_refresh()

    def on_open(self, evt, file_path: str = None):
        if not self._check_for_save():
            return
        if file_path is None:
            file_path, file_format = QFileDialog.getOpenFileName()
        if file_path:
            self.doc = self.create_document(file_path)
            self.doc.load()

    def on_save(self, save_as: bool = False):
        if self.doc.file_path is None or save_as:
            file_path, file_format = QFileDialog.getSaveFileName()
            if not file_path:
                return
            self.doc.file_path = file_path
        self.doc.save()

    def on_save_as(self):
        self.on_save(True)

    def on_update(self):
        title = ''.join([self.app_name, ' - ', self.doc.title])
        if self.doc.dirty:
            title += ' *'
        self.setWindowTitle(title)

    def on_exit(self):
        QApplication.quit()

    def create_document(self, file_path: str = None):
        return Document(file_path, None)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app = AppSkeleton(sys.argv)
    window = MainWindow(DEFAULT_COMPANY_NAME, DEFAULT_APP_NAME)
    window.show()
    sys.exit(app.exec())
