from enum import Flag

from PySide6.QtCore import Signal
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
