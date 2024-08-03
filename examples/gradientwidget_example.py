from PySide6 import QtWidgets

from gradientwidget.widget import GradientWidget, Gradient


# noinspection PyUnresolvedReferences
from __feature__ import snake_case


class Window(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        gradient = Gradient(((0, 'black'), (1, 'green'), (0.5, 'red')))
        gradient_widget = GradientWidget()
        gradient_widget.set_gradient(gradient)
        self.set_central_widget(gradient_widget)


app = QtWidgets.QApplication([])
w = Window()
w.show()
app.exec()
