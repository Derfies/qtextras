from enum import Flag

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication

from applicationframework.actions import Manager as ActionManager
from applicationframework.document import Document


class Application(QApplication):

    updated = Signal(Document, Flag)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.doc = None
        self.action_manager = ActionManager()
