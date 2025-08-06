from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QPushButton, QVBoxLayout, QWidget

# noinspection PyUnresolvedReferences
from __feature__ import snake_case


class ColourPicker(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._colour = QColor()
        self.button = QPushButton()
        self.button.clicked.connect(self.show_colour_dialog)
        layout = QVBoxLayout()
        layout.add_widget(self.button)
        layout.set_contents_margins(0, 0, 0, 0)
        self.set_layout(layout)
        self.set_colour(QColor())

    def show_colour_dialog(self):
        dialog = QColorDialog(self._colour)
        dialog.set_option(QColorDialog.ShowAlphaChannel, True)
        if dialog.exec():
            self.set_colour(dialog.selected_color())

    def colour(self):
        return self._colour

    def set_colour(self, colour: QColor):
        self._colour = colour
        self.button.set_style_sheet(f'background-color: {self.colour().name()};')
