from PySide6.QtGui import Qt
from PySide6.QtWidgets import QCheckBox

# noinspection PyUnresolvedReferences
from __feature__ import snake_case


class BoolCycleCheckBox(QCheckBox):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_tristate(True)

    def next_check_state(self):
        if self.check_state() == Qt.Checked:
            self.set_check_state(Qt.Unchecked)
        else:
            self.set_check_state(Qt.Checked)
