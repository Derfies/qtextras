import logging
import os
from pathlib import Path
from typing import Callable

from PySide6 import QtCore


logger = logging.getLogger(__name__)


class DirectoryWatcher(QtCore.QThread):

    """
    Class for watching a directory and all subdirectories below it for 
    changes.

    TODO: Possibly to keep in line with Qt standards the handlers should be
    signals?

    """

    def __init__(
        self,
        directory: Path | str | None = None,
        on_added: Callable | None = None,
        on_removed: Callable | None = None,
        on_modified: Callable | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        if directory is not None:
            self.set_directory(directory)

        self.on_added_fn = on_added
        self.on_removed_fn = on_removed
        self.on_modified_fn = on_modified

    def _recurse(self, dir_path):
        """
        
        """
        file_dict = {}

        def set_dict(key):
            try:
                file_dict[key] = os.path.getmtime(key)
            except Exception as e:
                logger.error(f'Failed to get modified time for file: {key}')

        for dir_path, dir_names, file_names in os.walk(dir_path, True):
            for file_name in file_names:
                file_path = Path(dir_path).joinpath(file_name)
                set_dict(file_path)

        return file_dict

    def set_directory(self, dir_path):
        """Set the directory for watching."""
        self.dir_path = dir_path
        self.before = self._recurse(self.dir_path)

    def run(self):
        """
        Main watcher function. Don't use this to start the watcher, use 
        start() to run the daemon instead.
        
        """
        while True:
            after = self._recurse(self.dir_path)

            # Work out which files were added, removed or modified.
            added = [f for f in after if not f in self.before]
            removed = [f for f in self.before if not f in after]
            modified = [
                f for f in after
                if f in self.before and after[f] != self.before[f]
            ]

            # Call handlers.
            if added:
                self.on_added(added)
            if removed:
                self.on_removed(removed)
            if modified:
                self.on_modified(modified)

            self.before = after

            # Sleep a bit so we don't max out the thread.
            self.msleep(1)

    def on_added(self, file_paths):
        if self.on_added_fn is not None:
            self.on_added_fn(file_paths)

    def on_removed(self, file_paths):
        if self.on_removed_fn is not None:
            self.on_removed_fn(file_paths)

    def on_modified(self, file_paths):
        if self.on_modified_fn is not None:
            self.on_modified_fn(file_paths)
