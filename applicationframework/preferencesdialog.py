from dataclasses import fields
from decimal import Decimal
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QDoubleValidator, QIntValidator, QValidator
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QStackedWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from customwidgets.colourpicker import ColourPicker

# noinspection PyUnresolvedReferences
from __feature__ import snake_case


class PreferenceWidgetBase(QWidget):

    """
    Should define a panel that can easily be added to the preference dialog, and
    a dict that can be passed when the dialog is dismissed.

    TODO: Maybe use name / label so we can have pretty user string and the string
    to use to same values against.

    TODO: Would be cool to use marshmallow to do type conversion similar to
    Django forms.

    """

    def __init__(self, title: str, name: str | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title = title
        if name is None:
            name = self.title.lower().replace(' ', '_')
        self.name = name
        self.layout = QVBoxLayout(self)

    def preferences(self) -> dict[str, Any]:
        ...

    def set_preferences(self, data):
        ...


class ManagedPreferenceWidgetBase(PreferenceWidgetBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._grid_layout = QGridLayout()
        self.layout.add_layout(self._grid_layout)
        self.layout.add_stretch()
        self._widgets = {}

    def _get_widget_value(self, widget: QWidget):
        if isinstance(widget, QCheckBox):
            value = widget.is_checked()
        elif isinstance(widget, QLineEdit):
            value = widget.text()
        elif isinstance(widget, QComboBox):

            # TODO: Sanity check me here - is this logical to do?
            if widget.current_index() < 0:
                value = None
            else:
                value = widget.current_text()
        elif isinstance(widget, ColourPicker):
            value = widget.colour()
        else:
            raise Exception(f'Unknown widget type: {widget}')

        # Seems a decent assumption to cast to the type indicated by the
        # validator.
        if hasattr(widget, 'validator'):
            if isinstance(widget.validator(), QIntValidator):
                value = int(value)
            elif isinstance(widget.validator(), QDoubleValidator):
                value = Decimal(value)
        return value

    def _set_widget_value(self, widget: QWidget, value: Any):
        if isinstance(widget, QCheckBox):
            widget.set_checked(value)
        elif isinstance(widget, QLineEdit):
            widget.set_text(str(value))
        elif isinstance(widget, QComboBox):
            index = widget.find_text(value)
            widget.set_current_index(index)
        elif isinstance(widget, ColourPicker):
            widget.set_colour(value)
        else:
            raise Exception(f'Unknown widget type: {widget}')

    def add_managed_widget(
        self,
        title: str,
        widget: QWidget,
        validator: QValidator | None = None,
        name: str | None = None,
    ):
        name = title.lower().replace(' ', '_') or name
        assert name not in self._widgets, f'Duplicate widget name: {name}'
        if validator is not None:
            widget.set_validator(validator)
        label = QLabel(title)
        next_row_idx = len(self._widgets)
        self._grid_layout.add_widget(label, next_row_idx, 0)
        self._grid_layout.add_widget(widget, next_row_idx, 1)
        self._widgets[name] = widget

    def preferences(self) -> dict[str, Any]:
        return {
            name: self._get_widget_value(widget)
            for name, widget in self._widgets.items()
        }

    def set_preferences(self, data: dict[str, Any]):
        for key, value in data.items():
            if key not in self._widgets:
                continue
            widget = self._widgets[key]
            self._set_widget_value(widget, value)


class DataclassPreferenceWidgetBase(ManagedPreferenceWidgetBase):

    def __init__(self, dataclass, *args, **kwargs):
        super().__init__(*args, **kwargs)

        widget_cls_map = {
            str: QLineEdit,
        }

        # TODO: Can pull a lot of tricky stuff here with the meta field that
        # dataclasses expose.
        for field in fields(dataclass):
            title = self.snake_to_title(field.name)
            self.add_managed_widget(title, widget_cls_map[field.type](), validator=None, name=field.name)

    @staticmethod
    def snake_to_title(s: str) -> str:
        return ' '.join(word.capitalize() for word in s.split('_'))


class PreferencesDialog(QDialog):

    """
    TODO: Figure out where to save this (QSettings or json blob)
    TODO: Figure out if these are project-centric or application centric (maybe both)?

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_window_title('Preferences')

        self.widgets = {}
        self.preferences = {}

        # Create the main layout.
        main_layout = QVBoxLayout(self)

        # Create a horizontal layout for the content.
        self.hsplitter = QSplitter(Qt.Orientation.Horizontal)

        # Create the tree view for categories.
        self.tree_view = QTreeWidget()
        self.tree_view.set_header_hidden(True)

        # Create a stacked widget to show the content of each category.
        self.stacked_widget = QStackedWidget()

        # Connect the tree selection to the stacked widget.
        self.tree_view.selection_model().selectionChanged.connect(self.on_selection_changed)

        # Add the tree view and stacked widget to the content layout.
        self.hsplitter.add_widget(self.tree_view)
        self.hsplitter.add_widget(self.stacked_widget)

        # Add content layout to the main layout.
        main_layout.add_widget(self.hsplitter)

        # Add OK and Cancel buttons.
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.save_preferences)
        buttons.rejected.connect(self.reject)
        main_layout.add_widget(buttons)

    def add_widget(self, widget: PreferenceWidgetBase, parent=None):
        if parent is None:
            parent = self.tree_view
        item = QTreeWidgetItem(parent)
        item.set_data(0, Qt.UserRole, widget)
        item.set_text(0, widget.title)
        self.stacked_widget.add_widget(widget)
        self.widgets[widget.name] = widget

        return item

    def on_selection_changed(self, selected, deselected):
        """Handle changes in the tree view selection."""
        item = self.tree_view.selected_items()[0]
        widget = item.data(0, Qt.UserRole)
        self.stacked_widget.set_current_widget(widget)

    def load_preferences(self, data: dict):
        for key, value in data.items():
            if key in self.widgets:
                self.widgets[key].set_preferences(value)

    def save_preferences(self):
        """Save the preferences when OK is pressed."""
        self.preferences = {}
        for key, widget in self.widgets.items():
            self.preferences[key] = widget.preferences()
        self.accept()  # Close the dialog
