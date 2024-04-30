from PySide6.QtGui import QImage

# noinspection PyUnresolvedReferences
from __feature__ import snake_case


class FilePathQImage:

    """
    Simple wrapper around QImage which keeps the file path property for later
    serialisation.

    """

    def __init__(self, file_path: str = ''):
        self.file_path = file_path

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, file_path: str):
        if file_path:
            data = QImage(file_path)
        else:
            data = QImage(0, 0, QImage.Format.Format_RGBA8888)
        self.data = data
        self._file_path = file_path
