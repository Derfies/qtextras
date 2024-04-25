from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication

from applicationframework.actions import Manager as ActionManager
from applicationframework.document import Document, UpdateFlag


class Application(QApplication):

    updated = Signal(Document, UpdateFlag)
    selection_updated = Signal(Document, UpdateFlag)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.doc = None
        self.action_manager = ActionManager()
