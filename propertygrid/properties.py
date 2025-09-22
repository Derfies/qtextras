import sys
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

from customwidgets.boolcyclecheckbox import BoolCycleCheckBox
from gradientwidget.widget import GradientWidget
from propertygrid.constants import Undefined
from propertygrid.types import FilePathQImage


if 'unittest' not in sys.modules.keys():

    # noinspection PyUnresolvedReferences
    from __feature__ import snake_case


class PropertyBase:

    """
    Class that holds the (weak) reference to the parent object and name of
    property that we want to manage.

    """

    modal_editor = True

    def __init__(self, name, obj=None, value=None, parent=None, label=None):
        self._name = name

        # TODO: Not sure why this has to be a weakref, now that I think about
        # it. I need to be able to load arbitrary key / value dicts now too and
        # only loading an object is kinda annoying. Why cant we just support a
        # dict?
        #if obj is not None:
        #   self._ref = weakref.ref(obj)
        self._obj = obj
        self._value = value
        self._parent = parent
        self._label = label

        self._children = []
        if parent is not None:
            parent.add_child(self)

    def object(self) -> str:
        return self._obj

    def name(self) -> str:
        return self._name

    def value(self):
        return self._value

    def set_value(self, value):
        self._value = value

    def label(self) -> str:
        return self._label if self._label is not None else self._name

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

    def create_editor(self, parent) -> QWidget | None:
        return None

    def get_editor_data(self, editor: QWidget):
        raise NotImplementedError

    def set_editor_data(self, editor: QWidget):
        raise NotImplementedError

    def changing(self, editor: QWidget):
        return None

    def changed(self, editor: QWidget):
        raise NotImplementedError


class BoolProperty(PropertyBase):

    modal_editor = False

    def create_editor(self, parent) -> QWidget | None:
        return BoolCycleCheckBox(parent)

    def get_editor_data(self, editor: QCheckBox):
        check_state = editor.check_state()
        if check_state == Qt.PartiallyChecked:
            return Undefined()
        elif check_state == Qt.Checked:
            return True
        elif check_state == Qt.Unchecked:
            return False

    def set_editor_data(self, editor: QCheckBox):
        value = self.value()
        if isinstance(value, Undefined):
            editor.set_check_state(Qt.PartiallyChecked)
        elif value:
            editor.set_check_state(Qt.Checked)
        else:
            editor.set_check_state(Qt.Unchecked)

    def changed(self, editor: QCheckBox):
        return editor.stateChanged


class IntProperty(PropertyBase):

    def create_editor(self, parent) -> QWidget | None:

        # TODO: Expose min / max somewhere.. but how :D
        widget = QSpinBox(parent)
        widget.set_range(-2 ** 31, 2 ** 31 - 1)
        return widget

    def get_editor_data(self, editor: QSpinBox):
        return editor.value()

    def set_editor_data(self, editor: QSpinBox):
        if not isinstance(self.value(), Undefined):
            editor.set_value(self.value())


class FloatProperty(PropertyBase):

    def create_editor(self, parent) -> QWidget | None:

        # TODO: Expose min / max somewhere.. but how :D
        widget = QDoubleSpinBox(parent)
        widget.set_minimum(-1000.0)
        widget.set_maximum(1000.0)
        widget.set_decimals(4)
        return widget

    def get_editor_data(self, editor: QDoubleSpinBox):
        return editor.value()

    def set_editor_data(self, editor: QDoubleSpinBox):
        if not isinstance(self.value(), Undefined):
            editor.set_value(self.value())


class StringProperty(PropertyBase):

    def create_editor(self, parent) -> QWidget | None:
        return QLineEdit(parent)

    def get_editor_data(self, editor: QSpinBox):
        return editor.text()

    def set_editor_data(self, editor: QLineEdit):
        if not isinstance(self.value(), Undefined):
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

    def create_editor(self, parent) -> QWidget | None:
        editor = QComboBox(parent)
        editor.add_items(self.enum_values)
        return editor

    def get_editor_data(self, editor: QComboBox):
        return self.enum(editor.current_text())

    def set_editor_data(self, editor: QComboBox):
        if not isinstance(self.value(), Undefined):
            editor.set_current_text(str(self.value().value))

    def changed(self, editor: QComboBox):
        return editor.currentIndexChanged


class ColourProperty(PropertyBase):

    """
    Colour picking uses a dialog, so the intial value is set in the dialog
    constructor and set_editor_data does nothing.

    """

    def decoration_role(self):
        pixmap = QPixmap(26, 26)
        if not isinstance(self.value(), Undefined):
            pixmap.fill(self.value())
            return QIcon(pixmap)

    def create_editor(self, parent) -> QWidget | None:
        args = [self.value()] if not isinstance(self.value(), Undefined) else []
        return QColorDialog(*args, parent=parent)

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


class GradientProperty(PropertyBase):

    modal_editor = False

    def create_editor(self, parent) -> QWidget | None:
        return GradientWidget(None, parent)

    def get_editor_data(self, editor: GradientWidget):
        return editor.gradient()

    def set_editor_data(self, editor: GradientWidget):
        if not isinstance(self.value(), Undefined):
            editor.set_gradient(self.value())

    def changing(self, editor: QWidget):
        return editor.gradient_changing

    def changed(self, editor: GradientWidget):
        return editor.gradient_changed
