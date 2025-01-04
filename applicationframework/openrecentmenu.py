from functools import partial
from pathlib import Path

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu

# noinspection PyUnresolvedReferences
from __feature__ import snake_case


class OpenRecentMenu(QMenu):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._paths: list[Path] = []
        
    def paths(self):
        return self._paths

    def update_actions(self):
        self.clear()
        for path in self._paths:
            open_action = QAction(str(path), self)
            open_action.set_data(path)
            open_action.triggered.connect(partial(self.parent().open_event, open_action.data()))
            self.add_action(open_action)
        self.add_separator()
        self.clear_action = QAction('&Clear Recent', self)
        self.clear_action.triggered.connect(self.clear_file_paths)
        self.add_action(self.clear_action)

        # Seems to be required to redraw menu actions.
        self.show()
        self.hide()

    def add_file_path(self, file_path: str):
        path = Path(file_path)
        if path not in self._paths:
            self._paths.append(path)
        self.update_actions()

    def set_file_paths(self, file_paths: list[str]):
        for file_path in file_paths:
            path = Path(file_path)
            if path not in self._paths:
                self._paths.append(path)
        self.update_actions()

    def clear_file_paths(self):
        self._paths = []
        self.update_actions()
