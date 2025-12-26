import logging
import sys
from dataclasses import dataclass, fields
from enum import Enum, Flag

import qdarktheme
from PySide6.QtCore import QModelIndex, QPointF, Qt
from PySide6.QtGui import QColor, QColorConstants, QPainterPath, QPen, QPolygonF
from PySide6.QtWidgets import QGraphicsItem, QGraphicsEllipseItem, QGraphicsPathItem, QGraphicsScene, QGraphicsView, QPushButton, QSplitter, QVBoxLayout, QWidget

from applicationframework.actions import SetAttributes
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
NODE_RADIUS = 2


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


def bounding_box(points):
    x_coordinates, y_coordinates = zip(*points)

    return [(min(x_coordinates), min(y_coordinates)), (max(x_coordinates), max(y_coordinates))]


class View(QGraphicsView):

    def wheel_event(self, event):
        #if self.hasPhoto():
        if event.angle_delta().y() > 0:
            factor = 1.25

        else:
            factor = 0.8

        print(factor)

        self.scale(factor, factor)


class MainWindow(MainWindowBase):

    """
    https://stackoverflow.com/questions/2173146/how-can-i-draw-nodes-and-edges-in-pyqt

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.scene = QGraphicsScene()
        self.view = View(self.scene)

        import sys
        if r'C:\Users\Jamie Davies\Documents\git\gameengines' not in sys.path:
            sys.path.append(r'C:\Users\Jamie Davies\Documents\git\gameengines')

        from gameengines.build.duke3d import MapReader as Duke3dMapReader
        file_path = r'C:\Program Files (x86)\Steam\steamapps\common\Duke Nukem 3D\gameroot\maps\LL-SEWER.MAP'
        with open(file_path, 'rb') as file:
            m = Duke3dMapReader()(file)
        # self.assertEqual(1, len(m.sectors))
        # self.assertEqual(4, len(m.walls))
        # self.assertEqual(0, len(m.sprites))

        for sector in m.sectors:

            print('')
            print(sector)

            cells = []
            cell = []
            cell_wallptr = sector.wallptr
            next_point_idx = sector.wallptr
            for i in range(sector.wallnum):

                wall = m.walls[next_point_idx]
                print('    wall:', wall)
                cell.append((wall.x / 100, wall.y / 100))
                next_point_idx = wall.point2

                # HAX
                if next_point_idx < 0:
                    break

                # If the next point returns to the start and we haven't reached the
                # end of the sector's walls then the sector has a hole which we
                # currently can't support.
                print('next_point_idx:', next_point_idx, 'cell_wallptr:', cell_wallptr)
                if next_point_idx == cell_wallptr:
                    next_point_idx = sector.wallptr + i + 1
                    cell_wallptr = next_point_idx
                    cells.append(cell)
                    cell = []



            for cell in cells:

                print('cell:', cell)

                # Add a shape.
                path = QPainterPath()
                points = [QPointF(p[0], p[1]) for p in cell]
                points.append(QPointF(cell[0][0], cell[0][1]))
                poly = QPolygonF(points)
                path.add_polygon(poly)

                self.scene.add_item(Path(path, self.scene))

        #raise

        # Add a shape.
        # path = QPainterPath()
        # poly = QPolygonF([
        #     QPointF(0, 0),
        #     QPointF(0, 100),
        #     QPointF(100, 100),
        #     QPointF(100, 0),
        #     QPointF(0, 0)
        # ])
        # path.add_polygon(poly)
        #
        # self.scene.add_item(Path(path, self.scene))

        #print(self.view._zoom)

        self.property_grid = PropertyGrid()
        self.property_grid.model().dataChanged.connect(self.on_data_changed)

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

        self.app().preferences_manager.register_widget('main_splitter', self.splitter)

        self.view.fit_in_view(self.scene.scene_rect(), Qt.AspectRatioMode.KeepAspectRatio)

        self.app().doc.updated(dirty=False)



    def create_document(self, file_path: str = None) -> Document:
        return Document(file_path, Content(), UpdateFlag)

    def update_event(self, doc: Document, flags: UpdateFlag):
        super().update_event(doc, flags)

        def get_attrs(obj):
            return {field.name: getattr(obj, field.name) for field in fields(obj)}

        self.property_grid.set_dict(get_attrs(doc.content), owner=doc.content)

    def on_data_changed(self, index: QModelIndex):
        prop = index.internal_pointer()
        action = SetAttributes(prop.name(), prop.value(), prop.object())
        self.app().action_manager.push(action)
        action()
        self.app().doc.updated()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app = Application('foo', 'bar', sys.argv)
    qdarktheme.setup_theme()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
