import sys
import weakref
from enum import EnumMeta

from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon, QPixmap, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QHBoxLayout,
    QLineEdit,
    QSlider,
    QSpinBox,
    QWidget,
)

from gradientwidget.widget import GradientWidget
from propertygrid.constants import (
    Undefined,
    UndefinedBool,
    UndefinedColour,
    UndefinedInt,
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

    def __init__(self, name, obj=None, value=None, parent=None, label=None):
        #super().__init__()
        self._name = name
        if obj is not None:
           self._ref = weakref.ref(obj)
        self._value = value
        self._parent = parent
        self._label = label

        self._children = []
        if parent is not None:
            parent.add_child(self)

    def name(self) -> str:
        return self._name

    def value(self):
        return self._value

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

    class CheckBox(QCheckBox):

        _changed = Signal(bool)

        def __init__(self, property: PropertyBase, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.stateChanged.connect(self.on_state_changed)

        def on_state_changed(self):
            self._changed.emit(self.is_checked())

    def create_editor(self, parent) -> CheckBox | None:
        return BoolProperty.CheckBox(self, parent)

    def set_editor_data(self, editor: CheckBox):
        editor.set_checked(self.value())

    def changed(self, editor: CheckBox):
        return editor._changed


class IntProperty(PropertyBase):

    modal_editor = False

    class SpinBox(QSpinBox):

        _changed = Signal(int)

        def __init__(self, property: PropertyBase, *args, **kwargs):
            super().__init__(*args, **kwargs)

            if property.min is not None:
                self.set_minimum(property.min)
            if property.max is not None:
                self.set_maximum(property.max)
            self.valueChanged.connect(self.on_value_changed)

        def on_value_changed(self):
            self._changed.emit(self.value())

    def __init__(self, *args, **kwargs):
        self.min = kwargs.pop('min', None)
        self.max = kwargs.pop('max', None)
        super().__init__(*args, **kwargs)

    def create_editor(self, parent) -> SpinBox | None:
        return IntProperty.SpinBox(self, parent)

    def set_editor_data(self, editor: SpinBox):
        editor.set_value(self.value())

    def changed(self, editor: SpinBox):
        return editor._changed


class FloatProperty(PropertyBase):

    modal_editor = False

    class DoubleSpinBox(QDoubleSpinBox):

        _changed = Signal(float)

        def __init__(self, property: PropertyBase, *args, **kwargs):
            super().__init__(*args, **kwargs)

            if property.min is not None:
                self.set_minimum(property.min)
            if property.max is not None:
                self.set_maximum(property.max)
            self.valueChanged.connect(self.on_value_changed)

        def on_value_changed(self):
            self._changed.emit(self.value())

    def __init__(self, *args, **kwargs):
        self.min = kwargs.pop('min', None)
        self.max = kwargs.pop('max', None)
        super().__init__(*args, **kwargs)

    def create_editor(self, parent) -> DoubleSpinBox | None:
        return FloatProperty.DoubleSpinBox(self, parent)

    def set_editor_data(self, editor: DoubleSpinBox):
        editor.set_value(float(self.value()))

    def changed(self, editor: DoubleSpinBox):
        return editor._changed


class FloatSliderProperty(FloatProperty):

    modal_editor = False

    class Slider(QSlider):

        _changed = Signal(float)

        def __init__(self, property: PropertyBase, *args, **kwargs):
            super().__init__(*args, **kwargs)

            if property.min is not None:
                self.set_minimum(property.min)
            if property.max is not None:
                self.set_maximum(property.max)
            self.sliderReleased.connect(self.on_slider_moved)

        def on_slider_moved(self):
            self._changed.emit(self.value())

    def __init__(self, *args, **kwargs):
        self.min = kwargs.pop('min', None)
        self.max = kwargs.pop('max', None)
        super().__init__(*args, **kwargs)

    def create_editor(self, parent) -> Slider | None:
        return FloatSliderProperty.Slider(self, Qt.Orientation.Horizontal, parent)

    def changing(self, editor: Slider):
        return editor.sliderMoved

    def changed(self, editor: Slider):
        return editor._changed


class FloatWithSliderProperty(FloatProperty):

    modal_editor = False

    class FloatWithSliderWidget(QWidget):

        _changing = Signal(float)
        _changed = Signal(float)

        def __init__(self, property: PropertyBase, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.spin_box = QDoubleSpinBox(self)
            self.spin_box.valueChanged.connect(self.on_value_changed)

            self.slider = QSlider(Qt.Orientation.Horizontal, self)
            self.slider.set_tick_interval(0.1)
            self.slider.set_single_step(0.1)
            self.slider.sliderMoved.connect(self.on_slider_moved)
            self.slider.sliderReleased.connect(self.on_slider_released)

            self.layout = QHBoxLayout()
            self.layout.add_widget(self.spin_box)
            self.layout.add_widget(self.slider)
            self.set_layout(self.layout)

            if property.min is not None:
                self.slider.set_minimum(property.min)
                self.spin_box.set_minimum(property.min)
            if property.max is not None:
                self.slider.set_maximum(property.max)
                self.spin_box.set_maximum(property.max)

        def on_slider_moved(self, value):
            self.spin_box.block_signals(True)
            self.spin_box.set_value(value)
            self.spin_box.block_signals(False)
            self._changing.emit(value)

        def on_slider_released(self):
            self._changed.emit(self.slider.value())

        def on_value_changed(self):
            self._changed.emit(self.spin_box.value())

    def __init__(self, *args, **kwargs):
        self.min = kwargs.pop('min', None)
        self.max = kwargs.pop('max', None)
        super().__init__(*args, **kwargs)

    def create_editor(self, parent) -> FloatWithSliderWidget | None:
        return FloatWithSliderProperty.FloatWithSliderWidget(self, parent)

    def set_editor_data(self, editor: FloatWithSliderWidget):
        editor.spin_box.block_signals(True)
        editor.slider.block_signals(True)
        editor.spin_box.set_value(self.value())
        editor.slider.set_value(self.value())
        editor.spin_box.block_signals(False)
        editor.slider.block_signals(False)

    def changing(self, editor: FloatWithSliderWidget):
        return editor._changing

    def changed(self, editor: FloatWithSliderWidget):
        return editor._changed


class StringProperty(PropertyBase):

    modal_editor = False

    class LineEdit(QLineEdit):

        _changed = Signal(str)

        def __init__(self, property: PropertyBase, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.returnPressed.connect(self.on_return_pressed)

        def on_return_pressed(self):
            self._changed.emit(self.text())

    def create_editor(self, parent) -> LineEdit | None:
        return StringProperty.LineEdit(parent)

    def set_editor_data(self, editor: LineEdit):
        if not isinstance(self.value(), Undefined):
            editor.set_text(self.value())

    def changed(self, editor: LineEdit):
        return editor._changed

    # def get_editor_data(self, editor):
    #     return editor.text()


class EnumProperty(PropertyBase):

    """
    Note: Currently has a limitation in that the enum values *must* be strings.
    To fix we would have to cast the value pulled from the editor widget back
    to a type from the initial value, however we can't be sure that this type
    is valid for *all* enum values.

    """

    modal_editor = False

    class ComboBox(QComboBox):

        _changed = Signal(EnumMeta)

        def __init__(self, property: PropertyBase, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.enum_type = type(property.value())
            self.add_items([str(e.value) for e in self.enum_type.__members__.values()])
            self.currentIndexChanged.connect(self.on_current_index_changed)

        def on_current_index_changed(self):
            self._changed.emit(self.enum_type(self.current_text()))

    def create_editor(self, parent) -> ComboBox | None:
        return EnumProperty.ComboBox(self, parent)

    def set_editor_data(self, editor: ComboBox):
        editor.set_current_text(self.value().value)

    def changed(self, editor: ComboBox):
        return editor._changed


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
        editor.set_gradient(self.value())

    def changing(self, editor: GradientWidget):
        return editor.gradient_changing

    def changed(self, editor: GradientWidget):
        return editor.gradient_changed
