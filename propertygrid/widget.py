from PySide6.QtWidgets import QTreeView

from propertygrid.model import Model
from propertygrid.typedelegate import TypeDelegate

# noinspection PyUnresolvedReferences
from __feature__ import snake_case


class Widget(QTreeView):

    """
    Subclassed QTreeView that displays property name & value in tidy manner.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_model(Model(self))
        self.set_item_delegate(TypeDelegate(self))

    def add_object(self, property_object):
        self.model().add_property_object(property_object)
        self.expand_to_depth(0)

    def set_object(self, property_object):
        self.model().clear()
        self.model().add_property_object(property_object)
        self.expand_to_depth(0)
