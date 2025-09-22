from enum import Flag
from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from applicationframework.actions import Manager as ActionManager
from applicationframework.document import Document
from applicationframework.preferencesmanager import PreferencesManager


class Application(QApplication):

    updated = Signal(Document, Flag)

    def __init__(self, organization: str, application: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setOrganizationName(organization)
        self.setApplicationName(application)

        self.doc = None
        self.action_manager = ActionManager()
        self.preferences_manager = PreferencesManager()

    @property
    def icons_path(self) -> Path:
        return Path(__file__).parent.joinpath('data', 'icons')

    def get_icon(self, file_name: str, icons_path: Path = None) -> QIcon:
        icons_path = icons_path or self.icons_path
        return QIcon(str(icons_path.joinpath(file_name)))
