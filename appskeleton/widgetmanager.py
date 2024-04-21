import logging

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QWidget


logger = logging.getLogger(__name__)


class WidgetManager:

    def __init__(self, company_name: str, app_name: str):
        self._settings = QSettings(company_name, app_name)
        self._widgets = {}

        logger.debug(f'Widget settings file: {self._settings.fileName()}')

    def register_widget(self, name: str, widget: QWidget):
        self._widgets[name] = widget

    def load_settings(self):
        for key in self._settings.allKeys():
            value = self._settings.value(key)
            name, param = key.split('/')
            logger.debug(f'Loading widget: {name} setting: {value}')
            if param == 'rect':
                self._widgets[name].setGeometry(value)

    def save_settings(self):
        for name, widget in self._widgets.items():
            self._settings.beginGroup(name)
            self._settings.setValue('rect', widget.geometry())
            self._settings.endGroup()
