import logging
import random
import sys
from dataclasses import dataclass
from enum import Enum, Flag

import pyglet
import qdarktheme
from PySide6.QtCore import QModelIndex, Qt, QTimer
from PySide6.QtGui import QColor, QColorConstants
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QPushButton, QSplitter, QVBoxLayout, QWidget
from pyglet.gl import glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT

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


class UpdateFlag(Flag):

    pass


class PygletWidget(QOpenGLWidget):

    """
    https://stackoverflow.com/questions/72714242/render-pyglet-window-inside-pyqt6-window

    """

    def __init__(self, width, height, parent=None):
        super().__init__(parent)
        self.set_minimum_size(width, height)

        self.timer = QTimer()
        self.timer.timeout.connect(self._pyglet_update)
        self.timer.set_interval(0)
        self.timer.start()

    def _pyglet_update(self):

        # Tick the pyglet clock, so scheduled events can work.
        pyglet.clock.tick()

        # Force widget to update, otherwise paintGL will not be called.
        self.update()  # self.updateGL() for pyqt5

    def paintGL(self):
        """Pyglet equivalent of on_draw event for window"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.batch.draw()

    def initializeGL(self):
        """Call anything that needs a context to be created."""
        self.batch = pyglet.graphics.Batch()
        size = self.size()
        w, h = size.width(), size.height()

        self.projection = pyglet.window.Projection2D()
        self.projection.set(w, h, w, h)


class MainWindow(MainWindowBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.viewport = PygletWidget(640, 480)

        self.property_grid = PropertyGrid()
        self.property_grid.model().data_changed.connect(self.on_data_changed)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.add_widget(self.viewport)
        self.splitter.add_widget(self.property_grid)

        self.refresh_button = QPushButton('Refresh')
        self.refresh_button.clicked.connect(self.app().doc.updated)

        self.sprite_button = QPushButton('Create Rectangle', self)
        self.sprite_button.clicked.connect(self.create_sprite_click)

        self.layout = QVBoxLayout(self)
        self.layout.add_widget(self.splitter)
        self.layout.add_widget(self.refresh_button)
        self.layout.add_widget(self.sprite_button)

        self.window = QWidget()
        self.window.set_layout(self.layout)
        self.set_central_widget(self.window)

        self.app().doc.updated(dirty=False)

        self.shapes = []

    def create_sprite_click(self):

        gl_width, gl_height = self.viewport.size().width(), self.viewport.size().height()

        width = random.randint(50, 100)
        height = random.randint(50, 100)

        x = random.randint(0, gl_width - width)
        y = random.randint(0, gl_height - height)
        color = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

        shape = pyglet.shapes.Rectangle(x, y, width, height, color=color, batch=self.viewport.batch)
        shape.opacity = random.randint(100, 255)
        self.shapes.append(shape)

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
    app = Application(DEFAULT_COMPANY_NAME, DEFAULT_APP_NAME, sys.argv)
    qdarktheme.setup_theme()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
