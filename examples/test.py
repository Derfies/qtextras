import os
import sys
import traceback
import argparse
import random
from pathlib import Path

import pyglet
from textwrap import dedent
from typing import TYPE_CHECKING, Final, Dict, List, Optional, Tuple, Mapping

from PySide6.QtGui import QAction, QWheelEvent
from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import (
    QFileDialog,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QMenuBar,
    QMenu,
    QStatusBar,
)
from PySide6.QtWidgets import QApplication
from PySide6.QtOpenGLWidgets import QOpenGLWidget


# Import the other constants after the UI libraries to avoid
# cluttering the symbol table when debugging import problems.
from pyglet.gl import (
    glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, glActiveTexture,
    GL_TEXTURE0, glBindTexture, GL_BLEND, glEnable, glBlendFunc, glDisable
)


class Ui_MainWindow:

    def setupUi(self, MainWindow: QtWidgets.QMainWindow) -> None:
        self._window = MainWindow

        # Set up the central window widget object
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(820, 855)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # # Create layout for shader editing
        self.gridLayout = QGridLayout(self.centralwidget)
        self.verticalLayout_3 = QVBoxLayout()

        self.compileShaderBtn = QPushButton(self.centralwidget)
        self.compileShaderBtn.clicked.connect(self.compileClick)
        self.compileShaderBtn.setObjectName("compile_shader_btn")
        self.verticalLayout_3.addWidget(self.compileShaderBtn)

        # Initialize the pyglet widget we'll draw to and lay out the window
        self.openGLWidget = PygletWidget(800, 400, self.centralwidget)
        self.openGLWidget.setMinimumSize(QtCore.QSize(800, 400))
        self.openGLWidget.setObjectName("openGLWidget")
        self.verticalLayout_3.addWidget(self.openGLWidget)
        self.gridLayout.addLayout(self.verticalLayout_3, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

    def compileClick(self) -> None:
        # color = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        self.openGLWidget.makeCurrent()
        # self.sprite = pyglet.shapes.Rectangle(0, 0, 100, 100, color=color, batch=self.openGLWidget.batch)

        # self.sprite = pyglet.text.Label('Hello, world',
        #                           font_name='Times New Roman',
        #                           font_size=36,
        #                           x=100, y=100,
        #                           anchor_x='center', anchor_y='center', batch=self.openGLWidget.batch)
        kitten = pyglet.image.load(r'c:\users\jamie davies\ure.png')
        self.sprite = pyglet.sprite.Sprite(img=kitten, batch=self.openGLWidget.batch)
        #self.sprite =

    def closeProgram(self) -> None:
        app.exit()


class PygletWidget(QOpenGLWidget):

    _default_vertex_source = """#version 150 core
        in vec4 position;

        uniform WindowBlock
        {
            mat4 projection;
            mat4 view;
        } window;

        void main()
        {
            gl_Position = window.projection * window.view * position;
        }
    """

    _default_fragment_source = """#version 150 core
        out vec4 color;

        void main()
        {
            color = vec4(1.0, 0.0, 0.0, 1.0);
        }
    """

    def __init__(self, width, height, parent):
        super().__init__(parent)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._pyglet_update)
        self.timer.setInterval(0)
        self.timer.start()

        self.shapes = []

    def _pyglet_update(self) -> None:

        # Tick the pyglet clock, so scheduled events can work.
        pyglet.clock.tick()

        # Force widget to update, otherwise paintGL will not be called.
        self.update()  # self.updateGL() for pyqt5

    def paintGL(self) -> None:
        """Pyglet equivalent of on_draw event for window"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.batch.draw()

    def resizeGL(self, width: int, height: int) -> None:
        self.projection = pyglet.math.Mat4.orthogonal_projection(0, width, 0, height, -255, 255)

        self.viewport = 0, 0, width, height

    def initializeGL(self) -> None:
        """Call anything that needs a context to be created."""

        #self._projection_matrix = pyglet.math.Mat4()
        #self._view_matrix = pyglet.math.Mat4()

        self.batch = pyglet.graphics.Batch()

        self._default_program = pyglet.graphics.shader.ShaderProgram(
            pyglet.graphics.shader.Shader(self._default_vertex_source, 'vertex'),
            pyglet.graphics.shader.Shader(self._default_fragment_source, 'fragment'))

        self.ubo = self._default_program.uniform_blocks['WindowBlock'].create_ubo()

        self.view = pyglet.math.Mat4()
        self.projection = pyglet.math.Mat4.orthogonal_projection(0, self.width(), 0, self.height(), -255, 255)
        #self.viewport = 0, 0, self.width(), self.height()

        # self.projection = pyglet.window.Projection2D()
        # self.projection.set(w, h, w, h)

    # @property
    # def viewport(self) -> Tuple[int, int, int, int]:
    #     """The Window viewport
    #
    #     The Window viewport, expressed as (x, y, width, height).
    #
    #     :return: The viewport size as a tuple of four ints.
    #     """
    #     return self._viewport
    #
    # @viewport.setter
    # def viewport(self, values: Tuple[int, int, int, int]) -> None:
    #     self._viewport = values
    #     pr = 1.0
    #     x, y, w, h = values
    #     pyglet.gl.glViewport(int(x * pr), int(y * pr), int(w * pr), int(h * pr))

    @property
    def projection(self) -> pyglet.math.Mat4:
        return self._projection_matrix

    @projection.setter
    def projection(self, matrix: pyglet.math.Mat4) -> None:
        with self.ubo as window_block:
            window_block.projection[:] = matrix

        self._projection_matrix = matrix

    @property
    def view(self) -> pyglet.math.Mat4:
        """The OpenGL window view matrix. Read-write.

        The default view is an identity matrix, but a custom
        :py:class:`pyglet.math.Mat4` instance can be set.
        Alternatively, you can supply a flat tuple of 16 values.
        """
        return self._view_matrix

    @view.setter
    def view(self, matrix: pyglet.math.Mat4) -> None:

        with self.ubo as window_block:
            window_block.view[:] = matrix

        self._view_matrix = matrix


def excepthook(exc_type, exc_value, exc_tb) -> None:
    """Replacement for Python's default exception handler function.

    See the following for more information:
    https://docs.python.org/3/library/sys.html#sys.excepthook
    """
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print(tb)


if __name__ == "__main__":
    # Create the base Qt application and initialize the UI
    app = QApplication(sys.argv)
    ui = Ui_MainWindow()#use_native_file_dialog=arguments.native_file_dialog)
    qt_window = QtWidgets.QMainWindow()
    ui.setupUi(qt_window)
    qt_window.show()

    # Replace the default exception handling *after* everything is
    # initialized to avoid swallowing fatal errors such as GL issues.
    sys.excepthook = excepthook

    # Start the application and return its exit code
    sys.exit(app.exec())