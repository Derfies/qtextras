import logging
import os
from enum import EnumMeta, Flag

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

from applicationframework.contentbase import ContentBase


logger = logging.getLogger(__name__)


class Document:

    def __init__(self, file_path: str | None, content: ContentBase, UpdateFlag: EnumMeta):
        self.file_path = file_path
        self.content = content
        self.dirty = False

        # Build the update all flag.
        all_mbr = UpdateFlag(0)
        for name, member in UpdateFlag.__members__.items():
            all_mbr |= member
        self._update_all_flag = all_mbr

    def app(self) -> QCoreApplication:
        return QApplication.instance()

    @property
    def title(self):
        if self.file_path is not None:
            return os.path.basename(self.file_path)
        else:
            return 'untitled'

    def load(self):
        logger.debug(f'Loading content: {self.file_path}')
        self.content.load(self.file_path)
        self.updated(dirty=False)

    def save(self, file_path: str = None):
        file_path = file_path or self.file_path
        logger.debug(f'Saving content: {file_path}')
        self.content.save(file_path)
        self.dirty = False

    def _emit_updated(self, flags: Flag):
        logger.debug(f'Emitting updated: {flags}')
        self.app().updated.emit(self, flags)

    def updated(self, flags: Flag | None = None, dirty=True):
        flags = flags or self._update_all_flag
        if dirty:
            self.dirty = dirty
        self._emit_updated(flags)
