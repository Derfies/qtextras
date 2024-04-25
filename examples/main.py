import logging
import sys
from dataclasses import dataclass
from enum import Enum

import qdarktheme
from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QColor, QColorConstants
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from applicationframework.actions import SetAttribute
from applicationframework.application import Application
from applicationframework.contentbase import ContentBase
from applicationframework.document import Document
from applicationframework.mainwindow import MainWindow as MainWindowBase
from propertygrid.widget import Widget as PropertyGrid

# noinspection PyUnresolvedReferences
from __feature__ import snake_case


logger = logging.getLogger(__name__)


DEFAULT_COMPANY_NAME = 'Enron'
DEFAULT_APP_NAME = 'Application Framework'


class EnumValues(Enum):

    ONE = '1'
    TWO = '2'
    THREE = '3'


@dataclass
class Content(ContentBase):

    bool_value: bool = True
    int_value: int = 1
    float_value: float = 1.0
    string_value: str = 'one'
    enum_value: EnumValues = EnumValues.ONE
    colour_property: QColor = QColorConstants.White

    def load(self, file_path: str):
        pass

    def save(self, file_path: str):
        pass


class MainWindow(MainWindowBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.refresh_button = QPushButton('Refresh')
        self.refresh_button.clicked.connect(self.app().doc.refresh)

        self.property_grid = PropertyGrid()
        self.property_grid.model().data_changed.connect(self.on_data_changed)

        self.layout = QVBoxLayout(self)
        self.layout.add_widget(self.property_grid)
        self.layout.add_widget(self.refresh_button)

        self.window = QWidget()
        self.window.set_layout(self.layout)
        self.set_central_widget(self.window)

        self.app().doc.refresh()

    def create_document(self, file_path: str = None) -> Document:
        return Document(file_path, Content())

    def update_event(self, document: Document):
        super().update_event(document)

        self.property_grid.set_object(document.content)

    def on_data_changed(self, index: QModelIndex):
        item = index.internal_pointer()
        action = SetAttribute(item.name(), item.new_value(), item._ref())
        self.app().action_manager.push(action)
        action()
        self.app().doc.modified()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app = Application(sys.argv)
    qdarktheme.setup_theme()
    window = MainWindow(DEFAULT_COMPANY_NAME, DEFAULT_APP_NAME)
    window.show()
    sys.exit(app.exec())
