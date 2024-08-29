import logging

from PySide6.QtCore import QModelIndex, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QItemDelegate, QStyleOptionViewItem, QWidget

from .model import Model, ModelEvent
from .properties import PropertyBase

# noinspection PyUnresolvedReferences
from __feature__ import snake_case


logger = logging.getLogger(__name__)


class TypeDelegate(QItemDelegate):

    def create_editor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        print('create editor called')
        item = index.internal_pointer()
        return item.create_editor(parent)

    def set_editor_data(self, editor: QWidget, index: QModelIndex):
        self.block_signals(True)
        item = index.internal_pointer()
        item.set_editor_data(editor)
        self.block_signals(False)

    def set_model_data(self, editor: QWidget, model: Model, index: QModelIndex, **kwargs):
        """
        Might need to expose some way of signalling a dialog cancellation.

        editor: QWidget, model: Model, index: QModelIndex, **kwargs

        """
        #pass
        #print(args, kwargs)
        item = index.internal_pointer()
        if 'value' in kwargs:
            value = kwargs['value']
        else:
            value = kwargs.get('value', item.get_editor_data(editor))
        #print('->', args)
        #index, value = args

        event = ModelEvent(item._ref(), item.name(), value)
        index.model().data_changed.emit(event)

    def set_model_changing_data(self, index: QModelIndex, value):
        item = index.internal_pointer()
        event = ModelEvent(item._ref(), item.name(), value)
        index.model().data_changing.emit(event)

    def paint_non_modal_editor(self, painter: QPainter, index: QModelIndex, item: PropertyBase):
        editor = item.create_editor(self.parent())
        item.set_editor_data(editor)
        if not self.parent().index_widget(index):
            self.parent().set_index_widget(index, editor)
        if item.changing(editor) is not None:
            item.changing(editor).connect(lambda value: self.set_model_changing_data(index, value))
        #print(item, item.changed(editor))
        item.changed(editor).connect(lambda value: self.set_model_data(editor, index.model(), index, value=value))

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        item = index.internal_pointer()
        if index.column() == 1 and not item.modal_editor:
            self.paint_non_modal_editor(painter, index, item)
        else:
            super().paint(painter, option, index)
