from enum import Flag
from pathlib import Path

from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox

from applicationframework.application import Application
from applicationframework.document import Document
from applicationframework.openrecentmenu import OpenRecentMenu
from applicationframework.widgetmanager import WidgetManager

# noinspection PyUnresolvedReferences
from __feature__ import snake_case


class MainWindow(QMainWindow):

    def __init__(self, company_name: str, app_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app_name = app_name
        self.app().updated.connect(self.update_event)

        # TODO: Move to create_menubar?
        self.open_recent_menu = OpenRecentMenu('&Open Recent', parent=self)
        self.open_recent_menu.set_icon(self.get_icon('folder-open.png'))

        self.create_actions()
        self.connect_actions()
        self.connect_hotkeys()
        self.create_menu_bar()

        self.widget_manager = WidgetManager(company_name, self.app_name)
        self.widget_manager.register_widget('main_window', self)
        self.widget_manager.register_widget('open_recent_menu', self.open_recent_menu)

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
        self.new_action.triggered.connect(self.new_event)
        self.open_action.triggered.connect(self.open_event)
        self.save_action.triggered.connect(self.save_event)
        self.save_as_action.triggered.connect(self.save_as_event)
        self.exit_action.triggered.connect(self.exit_event)

        # Edit actions.
        self.undo_action.triggered.connect(self.app().action_manager.undo)
        self.redo_action.triggered.connect(self.app().action_manager.redo)

    def connect_hotkeys(self):

        # File actions.
        self.save_action.set_shortcut(QKeySequence('Ctrl+S'))

        # Edit actions.
        self.undo_action.set_shortcut(QKeySequence('Ctrl+Z'))
        self.redo_action.set_shortcut(QKeySequence('Ctrl+Shift+Z'))

    def create_menu_bar(self):
        menu_bar = self.menu_bar()

        # File menu.
        self.file_menu = menu_bar.add_menu('&File')
        self.file_menu.add_action(self.new_action)
        self.file_menu.add_action(self.open_action)
        self.file_menu.add_menu(self.open_recent_menu)
        self.file_menu.add_action(self.save_action)
        self.file_menu.add_action(self.save_as_action)
        self.file_menu.add_separator()
        self.file_menu.add_action(self.exit_action)

        # Edit menu.
        self.edit_menu = menu_bar.add_menu('&Edit')
        self.edit_menu.add_action(self.undo_action)
        self.edit_menu.add_action(self.redo_action)

    def create_document(self, file_path: str = None) -> Document:
        raise NotImplementedError

    def update_actions(self):

        # File actions.
        self.open_recent_menu.update_actions()

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

    def check_for_save(self) -> bool:
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
                self.save_event()
            elif result == QMessageBox.StandardButton.Cancel:
                return False
        return True

    def show_event(self, event):
        self.widget_manager.load_settings()

    def close_event(self, event):
        if not self.check_for_save():
            event.ignore()
            return False
        self.widget_manager.save_settings()
        return True

    def new_event(self):
        if not self.check_for_save():
            return False
        self.app().doc = self.create_document()
        self.app().doc.updated(dirty=False)
        return True

    def open_event(self, file_path: str | None | bool = None):

        # TODO: Still don't like this func sig. Magically populates with 'False'
        # when triggered.
        if self.check_for_save():
            if not file_path:
                file_path, file_format = QFileDialog.get_open_file_name()
            if file_path:
                self.open_recent_menu.add_file_path(file_path)
                self.app().doc = self.create_document(file_path)
                self.app().doc.load()
                return True
        return False

    def save_event(self, save_as: bool = False):
        if self.app().doc.file_path is None or save_as:
            file_path, file_format = QFileDialog.get_save_file_name()
            if not file_path:
                return False
            self.app().doc.file_path = file_path
        self.app().doc.save()

        # Don't call doc.updated here as we only really want to update the
        # window title.
        self.update_window_title()

        return True

    def save_as_event(self):
        self.save_event(save_as=True)

    def exit_event(self):
        QApplication.quit()

    def update_event(self, doc: Document, flags: Flag):
        self.update_window_title()
        self.update_actions()
