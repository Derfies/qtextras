import copy
from typing import Iterable
from dataclasses import dataclass

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor

import sys
if 'unittest' not in sys.modules.keys():
    # noinspection PyUnresolvedReferences
    from __feature__ import snake_case


STOP_SIZE = QSize(10, 10)


@dataclass
class GradientStop:

    position: float
    colour: QColor

    def __deepcopy__(self, memo):
        """
        Default deep copy behaviour seems to crash python. My guess is that deep
        copying a python wrapper around a C++ object is a no-no.

        """
        return self.__class__(self.position, QColor(self.colour))

    def clamp(self):
        self.position = max(0.0, min(1.0, self.position))


class Gradient:

    def __init__(self, stops: Iterable[tuple[float, str]] | None = None):

        # TODO: Use namedtuple?
        if stops is None:
            stops = [
                (0.0, QColor('#000000')),
                (1.0, QColor('#ffffff')),
            ]
        self._stops = [GradientStop(t[0], t[1]) for t in stops]

    def __len__(self):
        return len(self._stops)

    def __iter__(self):
        return iter(self._stops)

    def __getitem__(self, index):
        return self._stops[index]

    def __setitem__(self, index, val):
        self._stops[index] = val

    def __delitem__(self, index):
        del self._stops[index]

    def insert(self, index, val):
        self._stops.insert(index, val)

    def append(self, val):
        self._stops.append(val)

    def validate(self):
        self._stops = sorted(self._stops, key=lambda h: h.position)
        for stop in self._stops:
            stop.clamp()


class GradientWidget(QtWidgets.QWidget):

    gradient_changed = Signal()
    gradient_changing = Signal(Gradient)

    def __init__(self, gradient: Gradient | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._gradient = gradient or Gradient()
        self._drag_index = None

        self.set_size_policy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

    def paint_event(self, event):
        painter = QtGui.QPainter(self)
        w, h = painter.device().width(), painter.device().height()

        # Draw the linear horizontal gradient.
        gradient = QtGui.QLinearGradient(0, 0, w, 0)
        for stop in self._gradient:
            gradient.set_color_at(stop.position, stop.colour)
        rect = QtCore.QRect(0, 0, w, h)
        painter.fill_rect(rect, gradient)

        # Draw the stops.
        pen = QtGui.QPen()
        y = painter.device().height() / 2
        for stop in self._gradient:
            pen.set_color(QtGui.QColor('white'))
            painter.set_pen(pen)
            painter.draw_line(
                stop.position * w,
                y - STOP_SIZE.height(),
                stop.position * w,
                y + STOP_SIZE.height(),
            )
            pen.set_color(QtGui.QColor('red'))
            painter.set_pen(pen)
            rect = QtCore.QRect(
                stop.position * w - STOP_SIZE.width() / 2,
                y - STOP_SIZE.height() / 2,
                STOP_SIZE.width(),
                STOP_SIZE.height()
            )
            painter.draw_rect(rect)

        painter.end()

    # def size_hint(self):
    #     return QtCore.QSize(200, 50)

    def gradient(self) -> Gradient:
        return self._gradient

    def set_gradient(self, gradient: Gradient):

        # TODO: This could potentially change the object so perhaps we should be
        # working with a copy.
        self._gradient = gradient
        self._gradient.validate()
        self.gradient_changed.emit()
        self.update()

    def add_stop(self, position: float, colour: QColor | None = None):
        if position <= 0 or position >= 1.0:
            raise ValueError('New stop position must be within 0-1 range')

        # Find the correct index to insert the new stop, or append if it was
        # after the last stop.
        for i, stop in enumerate(self._gradient):
            if stop.position > position:
                self._gradient.insert(i, GradientStop(position, colour or stop.colour))
                break
        else:
            self._gradient.append(GradientStop(position, colour or stop.colour))
        self._gradient.validate()
        self.gradient_changed.emit()
        self.update()

    def remove_stop(self, index: int):

        # TODO: Validate gradient before doing anything else??
        #if not 0 < index < len(self._gradient) - 1:
        #    raise ValueError(f'Index must be within 0-{len(self._gradient) - 1} range')
        del self._gradient[index]
        self.gradient_changed.emit()
        self.update()

    def choose_stop_colour(self, stop: GradientStop):

        # TODO: Change default colours to vec3 or something sensible...?
        dlg = QtWidgets.QColorDialog(self)
        dlg.set_current_color(stop.colour)
        if dlg.exec_():
            stop.colour = dlg.current_color()
            self.gradient_changed.emit()
            self.update()

    def _get_event_stop_index(self, event) -> int | None:
        width = self.width()
        height = self.height()
        midpoint = height / 2

        # Are we inside a stop point? First check y.
        if midpoint - STOP_SIZE.height() <= event.y() <= midpoint + STOP_SIZE.height():
            for index, stop in enumerate(self._gradient):
                if stop.position * width - STOP_SIZE.width() <= event.x() <= stop.position * width + STOP_SIZE.width():
                    return index

        return None

    def mouse_press_event(self, event):
        if event.button() == Qt.RightButton:
            index = self._get_event_stop_index(event)
            self.remove_stop(index)
        elif event.button() == Qt.LeftButton:
            index = self._get_event_stop_index(event)

            # TODO: Expose constructor kwarg to lock end stops...
            #if index is not None and 0 < index < len(self._gradient) - 1:
            self._drag_index = index

    def mouse_move_event(self, event):
        if self._drag_index is not None:
            stop = self._gradient[self._drag_index]
            stop.position = event.x() / self.width()
            #self._gradient.validate()
            self.update()
            self.gradient_changing.emit(self._gradient)

    def mouse_release_event(self, e):
        self._drag_index = None
        self._gradient.validate()
        self.gradient_changed.emit()

    def mouse_double_click_event(self, event):
        index = self._get_event_stop_index(event)
        if index is not None:
            self.choose_stop_colour(self._gradient[index])
        else:
            self.add_stop(event.x() / self.width())
