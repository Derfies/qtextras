from pathlib import Path

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QMainWindow, QApplication, QMessageBox, QFileDialog

from appskeleton.document import Document
from appskeleton.widgetmanager import WidgetManager

# noinspection PyUnresolvedReferences
from __feature__ import snake_case


class MainWindow(QMainWindow):

    def __init__(self, company_name: str, app_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app_name = app_name

        self._create_menu_bar()
        self._create_actions()
        self._connect_actions()
        self._add_actions_to_menu_bar()

        self._widget_manager = WidgetManager(company_name, self.app_name)
        self._widget_manager.register_widget('main_window', self)

        self.app.updated.connect(self.on_update)

        # Default state is an empty document.
        self.app.doc = self.create_document()
        self.app.doc.on_refresh()

    @property
    def app(self) -> QCoreApplication:
        return QApplication.instance()

    @property
    def icons_path(self) -> Path:
        return Path(__file__).parent.joinpath('data', 'icons')

    def get_icon(self, file_name: str, icons_path: Path = None) -> QIcon:
        icons_path = icons_path or self.icons_path
        return QIcon(str(icons_path.joinpath(file_name)))

    def show_event(self, event):
        self._widget_manager.load_settings()

    def close_event(self, event):
        self._widget_manager.save_settings()

    def _create_menu_bar(self):
        menu_bar = self.menu_bar()
        self.file_menu = menu_bar.add_menu('&File')
        self.edit_menu = menu_bar.add_menu('&Edit')

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

    def _connect_actions(self):

        # File actions.
        self.new_action.triggered.connect(self.on_new)
        self.open_action.triggered.connect(self.on_open)
        self.save_action.triggered.connect(self.on_save)
        self.save_as_action.triggered.connect(self.on_save_as)
        self.exit_action.triggered.connect(self.on_exit)

    def _add_actions_to_menu_bar(self):

        # File actions.
        self.file_menu.add_action(self.new_action)
        self.file_menu.add_action(self.open_action)
        self.file_menu.add_action(self.save_action)
        self.file_menu.add_action(self.save_as_action)
        self.file_menu.add_separator()
        self.file_menu.add_action(self.exit_action)

        # Edit actions.
        self.edit_menu.add_action(self.undo_action)
        self.edit_menu.add_action(self.redo_action)

    def _check_for_save(self):
        if self.app.doc.dirty:
            msg = f'The document "{self.app.doc.title}" was modified after last save.\nSave changes before continuing?'
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
        self.app.doc = self.create_document()
        self.app.doc.on_refresh()

    def on_open(self, event, file_path: str = None):
        if not self._check_for_save():
            return
        if file_path is None:
            file_path, file_format = QFileDialog.get_open_file_name()
        if file_path:
            self.app.doc = self.create_document(file_path)
            self.app.doc.load()

    def on_save(self, save_as: bool = False):
        if self.app.doc.file_path is None or save_as:
            file_path, file_format = QFileDialog.get_save_file_name()
            if not file_path:
                return
            self.app.doc.file_path = file_path
        self.app.doc.save()

    def on_save_as(self):
        self.on_save(True)

    def on_update(self):
        title = ''.join([self.app_name, ' - ', self.app.doc.title])
        if self.app.doc.dirty:
            title += ' *'
        self.set_window_title(title)

    def on_exit(self):
        if not self._check_for_save():
            return
        QApplication.quit()

    def create_document(self, file_path: str = None):
        return Document(file_path, None)
