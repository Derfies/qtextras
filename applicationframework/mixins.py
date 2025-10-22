from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication


class HasAppMixin:

    def app(self) -> QCoreApplication:
        return QApplication.instance()
