from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTreeView

from propertygrid.constants import (
    Undefined,
    UndefinedBool,
    UndefinedColour,
    UndefinedInt,
)
from propertygrid.model import Model
from propertygrid.typedelegate import TypeDelegate

# noinspection PyUnresolvedReferences
from __feature__ import snake_case


class MultiObjectWrapper:

    """
    Convenience wrapper to allow the property grid to set multiple objects'
    attributes at once. I'm still not 100% set on this being the solution as
    the code already looks a bit funky. But it works, and there's *kind* of an
    elegance to it.

    Part is this stems from the issue of loading objects into the property grid.
    By the default the grid searches for attributes using vars, which does not
    pick up computed python properties.

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
                    value = Undefined()
                    if isinstance(attributes[key], bool):
                        value = UndefinedBool()
                    elif isinstance(attributes[key], int):
                        value = UndefinedInt()
                    elif isinstance(attributes[key], QColor):
                        value = UndefinedColour()
                    common[key] = value

        for key, value in common.items():
            self.__dict__[key] = value

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

        # Don't allow setting of Undefined values.
        # Ok, this fixes a crash but it bricks undo for multiple objects.
        if isinstance(value, Undefined):
            return
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
        """

        TODO: Use MultiObjectWrapper by default? It would be a weakref however
        so it would have to be stored somewhere...

        """
        self.model().add_property_object(property_object)
        self.expand_to_depth(0)

    def set_object(self, property_object):
        self.model().clear()
        self.model().add_property_object(property_object)
        self.expand_to_depth(0)
