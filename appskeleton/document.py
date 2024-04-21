import logging
import os

from PyQt6.QtWidgets import QApplication

from appskeleton.contentbase import ContentBase


logger = logging.getLogger(__name__)


class Document:

    def __init__(self, file_path: None, content: ContentBase):
        self.file_path = file_path
        self.content = content
        self.dirty = False

    @property
    def title(self):
        if self.file_path is not None:
            return os.path.basename(self.file_path)
        else:
            return 'untitled'

    def load(self):
        logger.info(f'Loading content: {self.file_path}')
        self.content.load(self.file_path)
        self.on_refresh()

    def save(self, file_path: str = None):
        file_path = file_path or self.file_path
        logger.debug(f'Saving content: {file_path}')
        self.content.save(file_path)
        self.dirty = False
        self.on_refresh()

    def on_refresh(self):
        QApplication.instance().update.emit(self)

    def on_modified(self):
        self.dirty = True
        QApplication.instance().update.emit(self)
