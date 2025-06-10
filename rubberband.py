from PySide6.QtGui import QColorConstants, QPainter, QPen
from PySide6.QtWidgets import QGraphicsRectItem, QStyleOptionGraphicsItem, QWidget

# noinspection PyUnresolvedReferences
from __feature__ import snake_case


class RubberBandGraphicsItem(QGraphicsRectItem):

    # TODO: Deprecate

    def __init__(self, *args, **wargs):
        super().__init__(*args, **wargs)
        self.pen = QPen(QColorConstants.Cyan)
        self.pen.set_cosmetic(True)
        #self.set_pen(pen)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget | None = ...) -> None:
        painter.set_pen(self.pen)
        painter.fill_rect(self.rect(), QColorConstants.DarkCyan)
        painter.draw_rect(self.rect().adjusted(0, 0, 0, 0))
