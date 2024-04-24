from pathlib import Path

from PySide6.QtGui import QIcon, QAction, QKeySequence
from PySide6.QtWidgets import QMainWindow, QApplication, QMessageBox, QFileDialog

from applicationframework.application import Application
from applicationframework.document import Document
from applicationframework.widgetmanager import WidgetManager

# noinspection PyUnresolvedReferences
from __feature__ import snake_case


class MainWindow(QMainWindow):

    def __init__(self, company_name: str, app_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app_name = app_name

        self.create_actions()
        self.connect_actions()
        self.connect_hotkeys()
        self.create_menu_bar()

        self.widget_manager = WidgetManager(company_name, self.app_name)
        self.widget_manager.register_widget('main_window', self)

        self.app().updated.connect(self.on_update)

        # Default state is an empty document.
        self.app().doc = self.create_document()

    def app(self) -> Application:
        return QApplication.instance()

    @property
    def icons_path(self) -> Path:
        return Path(__file__).parent.joinpath('data', 'icons')

    def get_icon(self, file_name: str, icons_path: Path = None) -> QIcon:
        icons_path = icons_path or self.icons_path
        return QIcon(str(icons_path.joinpath(file_name)))

    def create_document(self, file_path: str = None) -> Document:
        return Document(file_path, None)

    def create_menu_bar(self):
        menu_bar = self.menu_bar()

        # File actions.
        self.file_menu = menu_bar.add_menu('&File')
        self.file_menu.add_action(self.new_action)
        self.file_menu.add_action(self.open_action)
        self.file_menu.add_action(self.save_action)
        self.file_menu.add_action(self.save_as_action)
        self.file_menu.add_separator()
        self.file_menu.add_action(self.exit_action)

        # Edit actions.
        self.edit_menu = menu_bar.add_menu('&Edit')
        self.edit_menu.add_action(self.undo_action)
        self.edit_menu.add_action(self.redo_action)

    def create_actions(self):

        # File actions.
        self.new_action = QAction(self.get_icon('document.png'), '&New', self)
        self.open_action = QAction(self.get_icon('folder-open.png'), '&Open...', self)
        self.save_action = QAction(self.get_icon('disk.png'), '&Save', self)
        self.save_as_action = QAction(self.get_icon('disk.png'), '&Save As...', self)
        self.exit_action = QAction(self.get_icon('door-open-out.png'), '&Exit', self)

        # Edit actions.
        self.undo_action = QAction(self.get_icon('arrow-turn-180-left.png'), '&Undo', self)
        self.redo_action = QAction(self.get_icon('arrow-turn.png'), '&Redo', self)

    def connect_actions(self):

        # File actions.
        self.new_action.triggered.connect(self.on_new)
        self.open_action.triggered.connect(self.on_open)
        self.save_action.triggered.connect(self.on_save)
        self.save_as_action.triggered.connect(self.on_save_as)
        self.exit_action.triggered.connect(self.on_exit)

        # Edit actions.
        self.undo_action.triggered.connect(self.app().action_manager.undo)
        self.redo_action.triggered.connect(self.app().action_manager.redo)

    def connect_hotkeys(self):

        # File actions.
        self.save_action.set_shortcut(QKeySequence('Ctrl+S'))

        # Edit actions.
        self.undo_action.set_shortcut(QKeySequence('Ctrl+Z'))
        self.redo_action.set_shortcut(QKeySequence('Ctrl+Shift+Z'))

    def update_actions(self):

        # Edit actions.
        undo_enabled = bool(self.app().action_manager.undos)
        self.undo_action.set_enabled(undo_enabled)
        redo_enabled = bool(self.app().action_manager.redos)
        self.redo_action.set_enabled(redo_enabled)

    def update_window_title(self):
        title = ''.join([self.app_name, ' - ', self.app().doc.title])
        if self.app().doc.dirty:
            title += ' *'
        self.set_window_title(title)

    def show_event(self, event):
        self.widget_manager.load_settings()

    def close_event(self, event):
        self.widget_manager.save_settings()

    def _check_for_save(self) -> bool:
        if self.app().doc.dirty:
            msg = f'The document "{self.app().doc.title}" was modified after last save.\nSave changes before continuing?'
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
        self.app().doc = self.create_document()
        self.app().doc.refresh()

    def on_open(self, file_path: str = None):
        if not self._check_for_save():
            return
        if file_path is None:
            file_path, file_format = QFileDialog.get_open_file_name()
        if file_path:
            self.app().doc = self.create_document(file_path)
            self.app().doc.load()

    def on_save(self, save_as: bool = False):
        if self.app().doc.file_path is None or save_as:
            file_path, file_format = QFileDialog.get_save_file_name()
            if not file_path:
                return
            self.app().doc.file_path = file_path
        self.app().doc.save()

    def on_save_as(self):
        self.on_save(True)

    def on_update(self, document: Document):
        self.update_window_title()
        self.update_actions()

    def on_exit(self):
        if not self._check_for_save():
            return
        QApplication.quit()
