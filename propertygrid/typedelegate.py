from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QWidget

from propertygrid.model import Model
from propertygrid.properties import PropertyBase

# noinspection PyUnresolvedReferences
from __feature__ import snake_case


class TypeDelegate(QStyledItemDelegate):

    def create_editor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        item = index.internal_pointer()
        return item.create_editor(parent)

    def set_editor_data(self, editor: QWidget, index: QModelIndex):
        self.block_signals(True)
        item = index.internal_pointer()
        item.set_editor_data(editor)
        self.block_signals(False)

    def set_model_data(self, editor: QWidget, model: Model, index: QModelIndex):
        item = index.internal_pointer()
        value = item.get_editor_data(editor)
        model.set_data(index, value, Qt.EditRole)

    def set_model_changing_data(self, index: QModelIndex, value):

        # TODO: Reimplement with native model event class.
        pass

    def paint_non_modal_editor(self, painter: QPainter, index: QModelIndex, item: PropertyBase):
        editor = item.create_editor(self.parent())
        item.set_editor_data(editor)
        if not self.parent().index_widget(index):
            self.parent().set_index_widget(index, editor)

            # NOTE: Only bind once!
            item.changed(editor).connect(lambda: self.set_model_data(editor, index.model(), index))
            if item.changing(editor) is not None:
                item.changing(editor).connect(lambda value: self.set_model_changing_data(index, value))

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        item = index.internal_pointer()
        if index.column() == 1 and not item.modal_editor:
            self.paint_non_modal_editor(painter, index, item)
        else:
            super().paint(painter, option, index)
