import logging
from dataclasses import fields

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QSplitter, QWidget

from applicationframework.openrecentmenu import OpenRecentMenu

# noinspection PyUnresolvedReferences
# from __feature__ import snake_case


logger = logging.getLogger(__name__)


OBJECT_GROUP = 'objects'
DATACLASS_GROUP = 'dataclass'
WIDGET_GROUP = 'widgets'


class PreferencesManager:

    def __init__(self):
        """
        Initialise settings without application name or organisation name will
        borrow them from the application object.

        """
        self._settings = QSettings()
        self._dataclasses = {}
        self._widgets = {}
        logger.debug(f'Settings file: {self._settings.fileName()}')

    def register_dataclass(self, name: str, obj: object):
        self._dataclasses[name] = obj

    def register_widget(self, name: str, widget: QWidget):
        self._widgets[name] = widget

    def _load_dataclass(self, name: str, dataclass):
        self._settings.beginGroup(name)
        for field in fields(dataclass):
            if field.name not in self._settings.all_keys():
                continue

            # This is stupid.
            kwargs = {}
            if isinstance(getattr(dataclass, field.name), bool):
                kwargs['type'] = bool
            value = self._settings.value(field.name, **kwargs)
            logger.debug(f'Loading dataclass preference: {name} field: {field.name} value: {value}')
            setattr(dataclass, field.name, value)
        self._settings.endGroup()

    def _save_dataclass(self, name: str, dataclass):
        self._settings.beginGroup(name)
        for field in fields(dataclass):
            value = getattr(dataclass, field.name)
            logger.debug(f'Saving dataclass preference: {name} field: {field.name} value: {value}')
            self._settings.setValue(field.name, value)
        self._settings.endGroup()

    def _load_widget(self, name: str, widget: QWidget):
        self._settings.beginGroup(name)
        for attr, method_name in (
            ('rect', 'setGeometry'),
            ('splitterSettings', 'restoreState'),
            ('recentFilePaths', 'set_file_paths'),
        ):
            if attr not in self._settings.allKeys():
                continue
            value = self._settings.value(attr)
            logger.debug(f'Loading widget preference: {name} attr: {attr} value: {value}')
            getattr(widget, method_name)(value)
        self._settings.endGroup()

    def _save_widget(self, name: str, widget: QWidget):
        self._settings.beginGroup(name)
        for widget_cls, attr, method_name in (
            (QWidget, 'rect', 'geometry'),
            (QSplitter, 'splitterSettings', 'saveState'),
            (OpenRecentMenu, 'recentFilePaths', 'paths'),
        ):
            if not isinstance(widget, widget_cls):
                continue
            value = getattr(widget, method_name)()
            logger.debug(f'Saving widget preference: {name} attr: {attr} value: {value}')
            self._settings.setValue(attr, value)
        self._settings.endGroup()

    def _load_dataclasses(self):
        self._settings.beginGroup(DATACLASS_GROUP)
        for name, dataclass in self._dataclasses.items():
            self._load_dataclass(name, dataclass)
        self._settings.endGroup()

    def _save_dataclasses(self):
        self._settings.beginGroup(DATACLASS_GROUP)
        for name, dataclass in self._dataclasses.items():
            self._save_dataclass(name, dataclass)
        self._settings.endGroup()

    def _load_widgets(self):
        self._settings.beginGroup(WIDGET_GROUP)
        for name, widget in self._widgets.items():
            self._load_widget(name, widget)
        self._settings.endGroup()

    def _save_widgets(self):
        self._settings.beginGroup(WIDGET_GROUP)
        for name, widget in self._widgets.items():
            self._save_widget(name, widget)
        self._settings.endGroup()

    def load(self):
        logger.debug(f'Loading preferences from: {self._settings.fileName()}')
        self._load_dataclasses()
        self._load_widgets()

    def save(self):
        logger.debug(f'Saving preferences to: {self._settings.fileName()}')
        self._settings.clear()
        self._save_dataclasses()
        self._save_widgets()
