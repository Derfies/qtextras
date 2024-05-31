from types import SimpleNamespace
from typing import Sequence

from PySide6.QtWidgets import QTreeView

from propertygrid.model import Model
from propertygrid.typedelegate import TypeDelegate

# noinspection PyUnresolvedReferences
from __feature__ import snake_case


class Undefined: pass


class MultiObjectWrapper:

    """
    Use __dict__ directly to avoid calling __setattr__.

    A property will show if it's common to all objects.
    The property's value will be *visible* if it's the same for all objects.

    """

    def __init__(self, objs: list[object]):
        self.__dict__['objs'] = objs

        # Collect common properties.
        common = dict(vars(objs[0]))
        for obj in objs:
            attributes = vars(obj)
            for key in list(common.keys()):
                if key not in attributes:
                    common.pop(key)
                elif attributes[key] != common[key]:
                    common[key] = Undefined

        for key, value in common.items():
            self.__dict__[key] = value

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        for obj in self.objs:
            setattr(obj, key, value)


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
