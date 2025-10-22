import logging
import os
from enum import EnumMeta, Flag

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

from applicationframework.contentbase import ContentBase
from applicationframework.mixins import HasAppMixin


logger = logging.getLogger(__name__)


class Document(HasAppMixin):

    def __init__(self, file_path: str | None, content: ContentBase, UpdateFlag: EnumMeta):
        self.file_path = file_path
        self.content = content
        self.dirty = False

        # Build the update all flag.
        all_mbr = UpdateFlag(0)
        for name, member in UpdateFlag.__members__.items():
            all_mbr |= member
        self._default_flags = all_mbr

    @property
    def title(self):
        if self.file_path is not None:
            return os.path.basename(self.file_path)
        else:
            return 'untitled'

    @property
    def default_flags(self):
        return self._default_flags

    @property
    def new_flags(self):
        return self.default_flags

    @property
    def load_flags(self):
        return self.default_flags

    def load(self):
        logger.debug(f'Loading content: {self.file_path}')
        self.content.load(self.file_path)
        self.updated(flags=self.load_flags, dirty=False)

    def save(self, file_path: str = None):
        file_path = file_path or self.file_path
        logger.debug(f'Saving content: {file_path}')
        self.content.save(file_path)
        self.dirty = False

    def _emit_updated(self, flags: Flag):
        logger.debug(f'Emitting updated: {flags}')
        self.app().updated.emit(self, flags)

    def updated(self, flags: Flag | None = None, dirty=True):
        flags = flags or self.default_flags
        if dirty:
            self.dirty = dirty
        self._emit_updated(flags)
