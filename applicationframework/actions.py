import abc
import logging
from enum import Flag

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication


logger = logging.getLogger(__name__)


class Base(metaclass=abc.ABCMeta):

    def __init__(self, flags: Flag | None = None):
        self.flags = flags

    def __call__(self):
        return self.redo()

    def app(self) -> QCoreApplication:
        return QApplication.instance()

    @abc.abstractmethod
    def undo(self):
        ...

    @abc.abstractmethod
    def redo(self):
        ...

    def destroy(self):
        ...


class Composite(Base):

    def __init__(self, actions: list[Base], **kwargs):
        super().__init__(**kwargs)

        self.actions = actions

    def undo(self):
        for action in reversed(self.actions):
            action.undo()
        return self.flags

    def redo(self):
        for action in self.actions:
            action.redo()
        return self.flags

    def destroy(self):
        for action in self.actions:
            action.destroy()


class Edit(Base):

    def __init__(self, obj, **kwargs):
        super().__init__(**kwargs)

        # TODO: Maybe don't use weak ref, as certain actions that remove an
        # object (and thus result in it being garbage collected) are never
        # retrievable.
        #self._ref = weakref.ref(obj)
        self.obj = obj


class SetAttribute(Edit):

    def __init__(self, name, value, *args):
        super().__init__(*args)
        self.name = name
        self.value = value
        self.old_value = getattr(self.obj, name)

    def undo(self):
        setattr(self.obj, self.name, self.old_value)
        return self.flags

    def redo(self):
        setattr(self.obj, self.name, self.value)
        return self.flags


class SetKey(Edit):

    def __init__(self, key, value, *args):
        super().__init__(*args)
        self.key = key
        self.value = value

        # TODO: use old_in to potentially delete a key...?
        self.old_value = self.obj.get(key)

    def undo(self):
        self.obj[self.key] = self.old_value
        return self.flags

    def redo(self):
        self.obj[self.key] = self.value
        return self.flags


class Manager:

    def __init__(self):
        self.undos = []
        self.redos = []

    def app(self) -> QCoreApplication:
        return QApplication.instance()

    def undo(self):
        if not self.undos:
            logger.warning('Undo queue is empty')
        else:
            action = self.undos.pop()
            self.redos.append(action)
            self.app().doc.updated(action.undo())

    def redo(self):
        if not self.redos:
            logger.warning('Redo queue is empty')
        else:
            action = self.redos.pop()
            self.undos.append(action)
            self.app().doc.updated(action.redo())

    def reset_undo(self):
        while self.undos:
            action = self.undos.pop()
            action.destroy()

    def reset_redo(self):
        while self.redos:
            action = self.redos.pop()
            action.destroy()

    def reset(self):
        self.reset_undo()
        self.reset_redo()

    def push(self, action):
        self.undos.append(action)
        self.reset_redo()
