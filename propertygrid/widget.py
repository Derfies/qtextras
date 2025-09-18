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

        self.set_model(self.get_model_class()())
        self.set_item_delegate(TypeDelegate(self))

    def get_model_class(self):
        return Model

    def add_dict(self, d: dict, owner=None):
        self.model().add_dict(d, owner=owner)
        self.expand_to_depth(0)

    def set_dict(self, d: dict, owner=None):
        self.model().clear()
        self.model().add_dict(d, owner=owner)
        self.expand_to_depth(0)

    def set_concurrent_dicts(self, ds: list[dict], owner=None):
        self.model().clear()
        self.model().add_concurrent_dicts(ds, owner=owner)
        self.expand_to_depth(0)