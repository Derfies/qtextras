import sys
import weakref
from enum import EnumMeta

from PySide6.QtGui import QIcon, QPixmap, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QLineEdit,
    QSpinBox,
    QWidget,
)
from propertygrid.types import FilePathQImage

if 'unittest' not in sys.modules.keys():

    # noinspection PyUnresolvedReferences
    from __feature__ import snake_case


class PropertyBase:

    """
    Class that holds the (weak) reference to the parent object and name of
    property that we want to manage.

    TODO: Add label, as distinct from name.

    """

    modal_editor = True

    def __init__(self, name, obj=None, parent=None, label=None):
        self._name = name
        if obj is not None:
            self._ref = weakref.ref(obj)
        self._parent = parent
        self._label = label

        self._new_value = None
        self._children = []
        if parent is not None:
            parent.add_child(self)

    def name(self) -> str:
        return self._name

    def label(self) -> str:
        return self._label if self._label is not None else self._name

    def value(self):
        return getattr(self._ref(), self._name)

    def set_value(self, value):
        setattr(self._ref(), self._name, value)

    def new_value(self):
        return self._new_value

    def set_new_value(self, editor):
        self._new_value = self.get_editor_data(editor)

    def is_valid(self):
        return False

    def add_child(self, child):
        self._children.append(child)

    def child_count(self):
        return len(self._children)

    def child(self, row=None):
        if row is not None:
            return self._children[row]
        else:
            return self._children

    def parent(self):
        return self._parent

    def row(self):
        if self._parent is not None:
            return self.parent().child().index(self)

    def decoration_role(self):
        return None

    def changed(self, editor: QWidget):
        raise NotImplementedError

    def create_editor(self, parent) -> QWidget | None:
        return None

    def get_editor_data(self, editor: QWidget):
        raise NotImplementedError

    def set_editor_data(self, editor: QWidget):
        raise NotImplementedError


class BoolProperty(PropertyBase):

    modal_editor = False

    def changed(self, editor: QCheckBox):
        return editor.stateChanged

    def create_editor(self, parent) -> QWidget | None:
        return QCheckBox(parent)

    def get_editor_data(self, editor: QCheckBox):
        return editor.is_checked()

    def set_editor_data(self, editor: QCheckBox):
        editor.set_checked(self.value())


class IntProperty(PropertyBase):

    def create_editor(self, parent) -> QWidget | None:
        return QSpinBox(parent)

    def get_editor_data(self, editor: QSpinBox):
        return editor.value()

    def set_editor_data(self, editor: QSpinBox):
        editor.set_value(self.value())


class FloatProperty(PropertyBase):

    def create_editor(self, parent) -> QWidget | None:
        return QDoubleSpinBox(parent)

    def get_editor_data(self, editor: QSpinBox):
        return editor.value()

    def set_editor_data(self, editor: QDoubleSpinBox):
        editor.set_value(self.value())


class StringProperty(PropertyBase):

    def create_editor(self, parent) -> QWidget | None:
        return QLineEdit(parent)

    def get_editor_data(self, editor: QSpinBox):
        return editor.text()

    def set_editor_data(self, editor: QLineEdit):
        editor.set_text(self.value())


class EnumProperty(PropertyBase):

    """
    Note: Currently has a limitation in that the enum values *must* be strings.
    To fix we would have to cast the value pulled from the editor widget back
    to a type from the initial value, however we can't be sure that this type
    is valid for *all* enum values.

    """

    modal_editor = False

    @property
    def enum(self) -> EnumMeta:
        return type(self.value())

    @property
    def enum_values(self) -> list[str]:
        return [str(e.value) for e in self.enum.__members__.values()]

    def changed(self, editor: QComboBox):
        return editor.currentIndexChanged

    def create_editor(self, parent) -> QWidget | None:
        editor = QComboBox(parent)
        editor.add_items(self.enum_values)
        return editor

    def get_editor_data(self, editor: QSpinBox):
        return self.enum(editor.current_text())

    def set_editor_data(self, editor: QComboBox):
        editor.set_current_text(str(self.value().value))


class ColourProperty(PropertyBase):

    """
    Colour picking uses a dialog, so the intial value is set in the dialog
    constructor and set_editor_data does nothing.

    """

    def decoration_role(self):
        pixmap = QPixmap(26, 26)
        pixmap.fill(self.value())
        return QIcon(pixmap)

    def create_editor(self, parent) -> QWidget | None:
        return QColorDialog(self.value(), parent)

    def get_editor_data(self, editor: QColorDialog):
        return editor.current_color()

    def set_editor_data(self, editor: QColorDialog):
        pass


class ImageProperty(PropertyBase):

    def decoration_role(self):
        pixmap = QPixmap.from_image(self.value().data)
        pixmap = pixmap.scaled(26, 26, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        return QIcon(pixmap)

    def create_editor(self, parent) -> QWidget | None:

        # TODO: Start in the location of the old image.
        dialog = QFileDialog(parent, filter='PNG (*.png)')
        dialog.set_file_mode(QFileDialog.FileMode.ExistingFile)
        dialog.exec()
        return dialog

    def get_editor_data(self, editor: QFileDialog):
        return FilePathQImage(editor.selected_files()[0])

    def set_editor_data(self, editor: QColorDialog):
        pass
