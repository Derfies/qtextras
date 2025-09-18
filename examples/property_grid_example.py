import logging
import sys
from dataclasses import dataclass
from dataclasses import fields
from enum import Enum, Flag

import qdarktheme
from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QColor, QColorConstants
from PySide6.QtWidgets import QAbstractItemView, QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from applicationframework.actions import SetAttributes
from applicationframework.application import Application
from applicationframework.contentbase import ContentBase
from applicationframework.document import Document
from applicationframework.mainwindow import MainWindow as MainWindowBase
from gradientwidget.widget import Gradient
from propertygrid.widget import Widget as PropertyGrid

# noinspection PyUnresolvedReferences
from __feature__ import snake_case


logger = logging.getLogger(__name__)


DEFAULT_COMPANY_NAME = 'Enron'
DEFAULT_APP_NAME = 'Application Framework'


class EnumValues(Enum):

    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3


@dataclass
class Data:

    bool_value: bool
    int_value: int
    float_value: float
    string_value: str
    enum_value: EnumValues
    colour_property: QColor
    gradient: Gradient


class Content(ContentBase):

    def __init__(self):
        self.data = (
            Data(
                False,
                0,
                0.1,
                'zero',
                EnumValues.ZERO,
                QColorConstants.Red,
                Gradient(),
            ),
            Data(
                True,
                1,
                1.1,
                'one',
                EnumValues.ONE,
                QColorConstants.Blue,
                Gradient(),
            ),
        )

    def load(self, file_path: str):
        pass

    def save(self, file_path: str):
        pass


class UpdateFlag(Flag):

    pass


class MainWindow(MainWindowBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.refresh_button = QPushButton('Refresh')
        self.refresh_button.clicked.connect(self.app().doc.updated)

        self.grid1 = PropertyGrid()
        self.grid1.model().dataChanged.connect(self.on_data_changed)
        self.grid1.set_edit_triggers(QAbstractItemView.AllEditTriggers)

        self.grid2 = PropertyGrid()
        self.grid2.model().dataChanged.connect(self.on_data_changed)
        self.grid2.set_edit_triggers(QAbstractItemView.AllEditTriggers)

        self.grid3 = PropertyGrid()
        self.grid3.model().dataChanged.connect(self.on_data_changed)
        self.grid3.set_edit_triggers(QAbstractItemView.AllEditTriggers)

        self.grid_layout = QHBoxLayout(self)
        self.grid_layout.add_widget(self.grid1)
        self.grid_layout.add_widget(self.grid2)
        self.grid_layout.add_widget(self.grid3)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.add_layout(self.grid_layout)
        self.main_layout.add_widget(self.refresh_button)

        self.window = QWidget()
        self.window.set_layout(self.main_layout)
        self.set_central_widget(self.window)

        self.app().doc.updated(dirty=False)

    def create_document(self, file_path: str = None) -> Document:
        return Document(file_path, Content(), UpdateFlag)

    def update_event(self, doc: Document, flags: UpdateFlag):
        super().update_event(doc, flags)

        def get_attrs(obj):
            return {field.name: getattr(obj, field.name) for field in fields(obj)}

        attr1, attr2 = get_attrs(doc.content.data[0]), get_attrs(doc.content.data[1])
        self.grid1.set_dict(attr1, owner=[doc.content.data[0]])
        self.grid2.set_dict(attr2, owner=[doc.content.data[1]])
        self.grid3.set_concurrent_dicts([attr1, attr2], owner=doc.content.data)

    def on_data_changed(self, index: QModelIndex):
        logger.debug(f'on_data_changed: {index}')
        prop = index.internal_pointer()
        action = SetAttributes(prop.name(), prop.value(), *prop.object())
        self.app().action_manager.push(action)
        action()
        self.app().doc.updated()

    def on_data_changing(self, index: QModelIndex):
        logger.debug(f'on_data_changed: {index}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app = Application('foo', 'bar', sys.argv)
    qdarktheme.setup_theme()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
