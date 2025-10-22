import copy
import logging
from enum import Enum
from typing import Any

from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from gradientwidget.widget import Gradient
from propertygrid.constants import (
    Undefined,
    UndefinedBool,
    UndefinedColour,
    UndefinedEnum,
    UndefinedFloat,
    UndefinedGradient,
    UndefinedImage,
    UndefinedInt,
    UndefinedString,
)
from propertygrid.properties import (
    BoolProperty,
    ColourProperty,
    EnumProperty,
    FloatProperty,
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


class Model(QAbstractItemModel):

    """
    Class that creates an Qt model to the MVC so properties can be changed and
    accessed by the GUI widget.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._root = PropertyBase('Root')
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
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return node.label()
            else:
                return node.value()
        elif role == Qt.ItemDataRole.DecorationRole and index.column() == 1:
            return node.decoration_role()

    def header_data(self, section, orientation, role=None):
        if role == Qt.ItemDataRole.DisplayRole:
            if section == 0:
                return 'Name'
            else:
                return 'Value'

    def set_data(self, index, value, role):
        prop = index.internal_pointer()
        prop.set_value(value)
        self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
        return True

    def flags(self, index):
        if index.column() == 0:
            return Qt.ItemFlag.ItemIsEnabled
        else:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

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

        # TODO: Store by dict?
        self._items.append(property)

    # OK we can clean this up / modular-ize it further by wrapping the following:
    # Getting the prop class
    # Copying the value
    # Getting the undefined version of the value

    def get_property_class(self, value: Any):
        property_cls = None
        if isinstance(value, bool) or isinstance(value, UndefinedBool):
            property_cls = BoolProperty
        elif isinstance(value, int) or isinstance(value, UndefinedInt):
            property_cls = IntProperty
        elif isinstance(value, float) or isinstance(value, UndefinedFloat):
            property_cls = FloatProperty
        elif isinstance(value, str) or isinstance(value, UndefinedString):
            property_cls = StringProperty
        elif isinstance(value, Enum) or isinstance(value, UndefinedEnum):
            property_cls = EnumProperty
        elif isinstance(value, QColor) or isinstance(value, UndefinedColour):
            property_cls = ColourProperty
        elif isinstance(value, FilePathQImage) or isinstance(value, UndefinedImage):
            property_cls = ImageProperty
        elif isinstance(value, Gradient) or isinstance(value, UndefinedGradient):
            property_cls = GradientProperty
        return property_cls

    def add_dict(self, d: dict, owner=None):
        owner = owner or d
        self.begin_insert_rows(QModelIndex(), self.row_count(self._root), self.row_count(self._root))
        for key, value in d.items():

            # We want to use a deep copy of the value being passed in so it
            # doesn't get mutated in place (for complex data objects). QColor
            # seems to crash everyone's party so duplicate that in a sensible
            # way.
            if isinstance(value, QColor):
                value = QColor(value)
            elif isinstance(value, FilePathQImage):
                value = FilePathQImage(value.file_path)
            else:
                value = copy.deepcopy(value)

            property_cls = self.get_property_class(value)
            if property_cls is None:
                logger.warning(f'Cannot resolve property type: {key} {value} {type(value)}')
                continue

            self.add_property(property_cls(key, owner, value, self._root))
        self.end_insert_rows()

    @staticmethod
    def get_undefined_value(value):
        uvalue = Undefined()

        if isinstance(value, bool):
            uvalue = UndefinedBool()
        elif isinstance(value, int):
            uvalue = UndefinedInt()
        elif isinstance(value, float):
            uvalue = UndefinedFloat()
        elif isinstance(value, str):
            uvalue = UndefinedString()
        elif isinstance(value, Enum):
            return UndefinedEnum('UndefinedEnum', {'UNDEFINED': ''}).UNDEFINED
        elif isinstance(value, QColor):
            uvalue = UndefinedColour()
        elif isinstance(value, Gradient):
            uvalue = UndefinedGradient()

        return uvalue

    def add_concurrent_dicts(self, ds: dict, owner=None):

        # Collect common properties.
        common = ds[0].copy()
        for d in ds:
            for key in list(common.keys()):
                if key not in d:
                    common.pop(key)
                elif d[key] != common[key]:
                    value = self.get_undefined_value(d[key])
                    common[key] = value

        self.add_dict(common, owner)

    def clear(self):
        self.begin_remove_rows(QModelIndex(), 0, self.row_count(self._root))
        self._root = PropertyBase('Root')
        self._items.clear()
        self.end_remove_rows()
