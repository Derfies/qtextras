from functools import partial
from pathlib import Path

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu

# noinspection PyUnresolvedReferences
from __feature__ import snake_case


class OpenRecentMenu(QMenu):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.file_paths = []

    def update_actions(self):
        self.clear()
        for file_path in self.file_paths:
            path = Path(file_path)
            open_action = QAction(path.name, self)
            open_action.set_data(file_path)
            open_action.triggered.connect(partial(self.parent().open_event, open_action.data()))
            self.add_action(open_action)
        self.show()
        self.hide()

    def add_file_path(self, file_path: str):
        if file_path not in self.file_paths:
            self.file_paths.append(file_path)
