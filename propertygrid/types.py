from PySide6.QtGui import QImage

import sys
if 'unittest' not in sys.modules.keys():

    # noinspection PyUnresolvedReferences
    from __feature__ import snake_case


class FilePathQImage:

    """
    Simple wrapper around QImage which keeps the file path property for later
    serialisation.

    """

    def __init__(self, file_path: str = ''):
        self.file_path = file_path

    def __deepcopy__(self, memodict: dict = None):
        return self.__class__(self.file_path)

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
