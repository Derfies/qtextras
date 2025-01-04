import logging
import os
from collections import defaultdict

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QSplitter, QWidget

from applicationframework.openrecentmenu import OpenRecentMenu

# noinspection PyUnresolvedReferences
from __feature__ import snake_case


logger = logging.getLogger(__name__)


OBJECT_GROUP = 'objects'
WIDGET_GROUP = 'widgets'


class PreferencesManager:

    """
    Quickly becoming unwieldy if we want this to save all sorts of preferences.

    TODO: using marshmallow might be a nice way to store aribtrary dataclass
    instance values.

    TODO: The total set of widget attributes is assumed, can we do the same for
    arbitrary objects? We could if they were a dataclass...

    """

    def __init__(self):
        """
        Initialise settings without application name or organisation name will
        borrow them from the application object.

        """
        self._settings = QSettings()
        self._objects = defaultdict(list)
        self._widgets = {}
        logger.debug(f'Settings file: {self._settings.file_name()}')

    def register_object(self, name: str, obj: object, member_name: str):
        default = getattr(obj, member_name)
        self._objects[name].append((obj, member_name, default))

    def register_widget(self, name: str, widget: QWidget):
        self._widgets[name] = widget

    def _load_object(self, name, object_data):
        self._settings.begin_group(name)
        for obj, attr, default in object_data:

            # This is stupid.
            kwargs = {}
            if isinstance(default, bool):
                kwargs['type'] = bool
            value = self._settings.value(attr, defaultValue=default, **kwargs)
            logger.debug(f'Loading object preference: {name} attr: {attr} value: {value} type: {type(value)} default: {default} default type: {type(default)}')
            setattr(obj, attr, value)
        self._settings.end_group()
        
    def _save_object(self, name, object_data):
        self._settings.begin_group(name)
        for obj, attr, _ in object_data:
            value = getattr(obj, attr)
            logger.debug(f'Saving object preference: {name} attr: {attr} value: {value} type: {type(value)}')
            self._settings.set_value(attr, value)
        self._settings.end_group()

    def _load_widget(self, name: str, widget: QWidget):
        self._settings.begin_group(name)
        for attr, method_name in (
            ('rect', 'set_geometry'),
            ('splitter_settings', 'restore_state'),
            ('recent_file_paths', 'set_file_paths'),
        ):
            if attr not in self._settings.all_keys():
                continue
            value = self._settings.value(attr)
            logger.debug(f'Loading widget preference: {name} attr: {attr} value: {value}')
            getattr(widget, method_name)(value)
        self._settings.end_group()

    def _save_widget(self, name: str, widget: QWidget):
        self._settings.begin_group(name)
        for widget_cls, attr, method_name in (
            (QWidget, 'rect', 'geometry'),
            (QSplitter, 'splitter_settings', 'save_state'),
            (OpenRecentMenu, 'recent_file_paths', 'paths'),
        ):
            if not isinstance(widget, widget_cls):
                continue
            value = getattr(widget, method_name)()
            logger.debug(f'Saving widget preference: {name} attr: {attr} value: {value}')
            self._settings.set_value(attr, value)
        self._settings.end_group()

    def _load_objects(self):
        self._settings.begin_group(OBJECT_GROUP)
        for name, object_data in self._objects.items():
            self._load_object(name, object_data)
        self._settings.end_group()

    def _save_objects(self):
        self._settings.begin_group(OBJECT_GROUP)
        for name, object_data in self._objects.items():
            self._save_object(name, object_data)
        self._settings.end_group()

    def _load_widgets(self):
        self._settings.begin_group(WIDGET_GROUP)
        for name, widget in self._widgets.items():
            self._load_widget(name, widget)
        self._settings.end_group()

    def _save_widgets(self):
        self._settings.begin_group(WIDGET_GROUP)
        for name, widget in self._widgets.items():
            self._save_widget(name, widget)
        self._settings.end_group()

    def load(self):
        logger.debug(f'Loading preferences from: {self._settings.file_name()}')
        self._load_objects()
        self._load_widgets()

    def save(self):
        logger.debug(f'Saving preferences to: {self._settings.file_name()}')
        self._settings.clear()
        self._save_objects()
        self._save_widgets()
