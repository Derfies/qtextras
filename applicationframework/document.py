import logging
import os
from enum import Flag, auto

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

from applicationframework.contentbase import ContentBase


logger = logging.getLogger(__name__)


class UpdateFlag(Flag):

    MODIFIED = auto()
    SELECTION = auto()


class Document:

    def __init__(self, file_path: None, content: ContentBase):
        self.file_path = file_path
        self.content = content
        self.dirty = False
        self._selection = []

    def app(self) -> QCoreApplication:
        return QApplication.instance()

    @property
    def title(self):
        if self.file_path is not None:
            return os.path.basename(self.file_path)
        else:
            return 'untitled'

    @property
    def selection(self):
        return self._selection

    @selection.setter
    def selection(self, selection: list):
        self._selection = selection
        self.selection_modified()

    def load(self):
        logger.info(f'Loading content: {self.file_path}')
        self.content.load(self.file_path)
        self.refresh()

    def save(self, file_path: str = None):
        file_path = file_path or self.file_path
        logger.debug(f'Saving content: {file_path}')
        self.content.save(file_path)
        self.dirty = False
        self.refresh()

    def refresh(self):
        logger.debug(f'Emitting updated')
        self.app().updated.emit(self, None)

    def modified(self):
        self.dirty = True
        logger.debug(f'Emitting updated')
        self.app().updated.emit(self, UpdateFlag.MODIFIED)

    def selection_modified(self):
        logger.debug(f'Emitting selection_modified')
        self.app().selection_updated.emit(self, UpdateFlag.MODIFIED)
