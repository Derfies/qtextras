from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QItemDelegate, QStyleOptionViewItem, QWidget

from .model import Model
from .properties import PropertyBase

# noinspection PyUnresolvedReferences
from __feature__ import snake_case


class TypeDelegate(QItemDelegate):

    def create_editor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        item = index.internal_pointer()
        return item.create_editor(parent)

    def set_editor_data(self, editor: QWidget, index: QModelIndex):
        self.block_signals(True)
        item = index.internal_pointer()
        item.set_editor_data(editor)
        self.block_signals(False)

    def set_model_data(self, editor: QWidget, model: Model, index: QModelIndex, hot=False):
        item = index.internal_pointer()

        # TODO: Might need to expose some way of signalling a dialog cancellation.
        item.set_new_value(editor)

        # TODO: Might be useful to have this set as part of property grid
        # constructor, ie having properties set in place might be useful.
        #item.set_model_data(editor)
        if hot:
            try:
                model.data_changing.emit(index, index)
                print('data_changing EMIT')
            except Exception as e:
                print(e)
        else:
            model.data_changed.emit(index, index)
            print('data_changed EMIT')

    def foo(self, editor: QWidget, model: Model, index: QModelIndex):
        item = index.internal_pointer()
        item.set_old_value(editor)

    def paint_non_modal_editor(self, painter: QPainter, index: QModelIndex, item: PropertyBase):
        editor = item.create_editor(self.parent())
        item.set_editor_data(editor)
        if not self.parent().index_widget(index):
            self.parent().set_index_widget(index, editor)
        if item.about_to_change(editor) is not None:
            item.about_to_change(editor).connect(lambda: self.foo(editor, index.model(), index))
        if item.changing(editor) is not None:
            item.changing(editor).connect(lambda: self.set_model_data(editor, index.model(), index, hot=True))
        item.changed(editor).connect(lambda: self.set_model_data(editor, index.model(), index))

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        item = index.internal_pointer()
        if index.column() == 1 and not item.modal_editor:
            self.paint_non_modal_editor(painter, index, item)
        else:
            super().paint(painter, option, index)
