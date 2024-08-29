import copy
import logging
from enum import Enum

from PySide6.QtCore import QAbstractItemModel, QEvent, QModelIndex, Qt, Signal
from PySide6.QtGui import QColor

from gradientwidget.widget import Gradient
from propertygrid.constants import (
    UndefinedBool,
    UndefinedColour,
    UndefinedInt,
)
from propertygrid.properties import (
    BoolProperty,
    ColourProperty,
    EnumProperty,
    FloatProperty,
    FloatSliderProperty,
    FloatWithSliderProperty,
    GradientProperty,
    ImageProperty,
    IntProperty,
    PropertyBase,
    StringProperty,
)
from propertygrid.types import FilePathQImage

# noinspection PyUnresolvedReferences
from __feature__ import snake_case


logger = logging.getLogger(__name__)


class ModelEvent:

    def __init__(self, obj, name, value):
        self._object = obj
        self._name = name
        self._value = value

    def object(self):
        return self._object

    def name(self):
        return self._name

    def value(self):
        return self._value


class Model(QAbstractItemModel):

    """
    Class that creates an Qt model to the MVC so properties can be changed and
    accessed by the GUI widget.

    """

    data_changed = Signal(ModelEvent)
    data_changing = Signal(ModelEvent)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._root = PropertyBase('Root', None, None)
        self._items = []

    def row_count(self, parent=None, *args, **kwargs):
        if not parent.is_valid():
            parent_node = self._root
        else:
            parent_node = parent.internal_pointer()
        return parent_node.child_count()

    def column_count(self, parent=None, *args, **kwargs):
        return 2

    def data(self, index, role=None):
        if not index.is_valid():
            return None

        node = index.internal_pointer()
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            if index.column() == 0:
                return node.label()
            else:
                return node.value()

        decoration = node.decoration_role()
        if role == Qt.ItemDataRole.DecorationRole and index.column() == 1 and decoration is not None:
            return decoration

    def header_data(self, section, orientation, role=None):
        if role == Qt.ItemDataRole.DisplayRole:
            if section == 0:
                return 'Name'
            else:
                return 'Value'

    def flags(self, index):
        if index.column() == 0:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        else:
            return Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable

    def index(self, row, column, parent=None, *args, **kwargs):
        parent_node = self.get_node(parent)
        child_node = parent_node.child(row)
        if child_node is not None:
            return self.create_index(row, column, child_node)
        else:
            return QModelIndex()

    def parent(self, child=None):
        node = self.get_node(child)
        parent_node = node.parent()
        if parent_node == self._root:
            return QModelIndex()
        return self.create_index(parent_node.row(), 0, parent_node)

    def get_node(self, index):
        if index.is_valid():
            return index.internal_pointer()
        return self._root

    def add_property(self, property: PropertyBase):
        self._items.append(property)

    def add_property_object(self, obj: object):

        # TODO: This is the last part that feels a bit funky...
        # A better approach would be to expose a register interface, or remove
        # this idea of magic property objects...
        properties = vars(obj)
        self.begin_insert_rows(QModelIndex(), self.row_count(self._root), self.row_count(self._root))
        for key, value in properties.items():

            # We want to use a deep copy of the value being passed in so it
            # doesn't get mutated in place (for complex data objects). QColor
            # seems to crash everyone's party so duplicate that in a sensible
            # way.
            if isinstance(value, QColor):
                value = QColor(value)
            else:
                value = copy.deepcopy(value)

            property_cls = None
            if isinstance(value, bool) or isinstance(value, UndefinedBool):
                property_cls = BoolProperty
            elif isinstance(value, int) or isinstance(value, UndefinedInt):
                property_cls = IntProperty
            elif isinstance(value, float):
                property_cls = FloatWithSliderProperty
            elif isinstance(value, str):
                property_cls = StringProperty
            elif isinstance(value, Enum):
                property_cls = EnumProperty
            elif isinstance(value, QColor) or isinstance(value, UndefinedColour):
                property_cls = ColourProperty
            elif isinstance(value, FilePathQImage):
                property_cls = ImageProperty
            elif isinstance(value, Gradient):
                property_cls = GradientProperty
            if property_cls is None:
                logger.warning(f'Cannot resolve property type: {key} {value} {type(value)}')
                continue
            self.add_property(property_cls(key, obj, value, self._root))
        self.end_insert_rows()

    def clear(self):
        self.begin_remove_rows(QModelIndex(), 0, self.row_count(self._root))
        self._root = PropertyBase('Root', None, None)
        self._items.clear()
        self.end_remove_rows()
