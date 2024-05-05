import logging
import sys
from dataclasses import dataclass
from enum import Enum, Flag

import qdarktheme
from PySide6.QtCore import QModelIndex, QPointF, Qt
from PySide6.QtGui import QColor, QColorConstants, QPainterPath, QPen, QPolygonF
from PySide6.QtWidgets import QGraphicsItem, QGraphicsEllipseItem, QGraphicsPathItem, QGraphicsScene, QGraphicsView, QPushButton, QSplitter, QVBoxLayout, QWidget

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
NODE_RADIUS = 5


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


class UpdateFlag(Flag):

    pass


class Node(QGraphicsEllipseItem):

    def __init__(self, path, index):
        super(Node, self).__init__(-NODE_RADIUS, -NODE_RADIUS, 2 * NODE_RADIUS, 2 * NODE_RADIUS)

        self.rad = NODE_RADIUS
        self.path = path
        self.index = index

        self.setZValue(1)
        self.set_flag(QGraphicsItem.ItemIsMovable)
        self.set_flag(QGraphicsItem.ItemSendsGeometryChanges)
        self.set_brush(Qt.green)

    def item_change(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            self.path.update_element(self.index, value.to_point())
        return QGraphicsEllipseItem.item_change(self, change, value)


class Path(QGraphicsPathItem):

    def __init__(self, path, scene):
        super(Path, self).__init__(path)

        self.path = path
        for i in range(path.element_count() - 1):
            node = Node(self, i)
            node.set_pos(QPointF(path.element_at(i)))
            scene.add_item(node)
        self.set_pen(QPen(Qt.red, 1.75))

    def update_element(self, index, pos):
        self.path.set_element_position_at(index, pos.x(), pos.y())
        if index == 0 or index == self.path.element_count() - 1:
            self.path.set_element_position_at(0,  pos.x(), pos.y())
            self.path.set_element_position_at(self.path.element_count() - 1, pos.x(), pos.y())
        self.set_path(self.path)


class MainWindow(MainWindowBase):

    """
    https://stackoverflow.com/questions/2173146/how-can-i-draw-nodes-and-edges-in-pyqt

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)

        # Add a shape.
        path = QPainterPath()
        poly = QPolygonF([
            QPointF(0, 0),
            QPointF(0, 100),
            QPointF(100, 100),
            QPointF(100, 0),
            QPointF(0, 0)
        ])
        path.add_polygon(poly)

        self.scene.add_item(Path(path, self.scene))

        self.property_grid = PropertyGrid()
        self.property_grid.model().data_changed.connect(self.on_data_changed)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.add_widget(self.view)
        self.splitter.add_widget(self.property_grid)

        self.refresh_button = QPushButton('Refresh')
        self.refresh_button.clicked.connect(self.app().doc.updated)

        self.layout = QVBoxLayout(self)
        self.layout.add_widget(self.splitter)
        self.layout.add_widget(self.refresh_button)

        self.window = QWidget()
        self.window.set_layout(self.layout)
        self.set_central_widget(self.window)

        self.widget_manager.register_widget('main_splitter', self.splitter)

        self.app().doc.updated(dirty=False)

    def create_document(self, file_path: str = None) -> Document:
        return Document(file_path, Content(), UpdateFlag)

    def update_event(self, doc: Document, flags: UpdateFlag):
        super().update_event(doc, flags)

        self.property_grid.set_object(doc.content)

    def on_data_changed(self, index: QModelIndex):
        item = index.internal_pointer()
        action = SetAttribute(item.name(), item.new_value(), item._ref())
        self.app().action_manager.push(action)
        action()
        self.app().doc.updated()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app = Application(sys.argv)
    qdarktheme.setup_theme()
    window = MainWindow(DEFAULT_COMPANY_NAME, DEFAULT_APP_NAME)
    window.show()
    sys.exit(app.exec())
