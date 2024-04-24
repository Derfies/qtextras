import abc
import logging

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication


logger = logging.getLogger(__name__)


class Base(metaclass=abc.ABCMeta):

    def __call__(self):
        self.redo()

    @abc.abstractmethod
    def undo(self):
        ...

    @abc.abstractmethod
    def redo(self):
        ...

    def destroy(self):
        pass


class Composite(Base):

    def __init__(self, actions):
        self.actions = actions

    def undo(self):
        for action in reversed(self.actions):
            action.undo()

    def redo(self):
        for action in self.actions:
            action.redo()

    def destroy(self):
        for action in self.actions:
            action.destroy()


class Edit(Base):

    def __init__(self, obj):

        # TODO: Maybe don't use weak ref, as certain actions that remove an
        # object (and thus result in it being garbage collected) are never
        # retrievable.
        #self._ref = weakref.ref(obj)
        self.obj = obj


class SetAttribute(Edit):

    def __init__(self, name, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.value = value
        self.old_value = getattr(self.obj, name)

    def undo(self):
        super().undo()
        logger.info(f'Setting attribute: {self.obj}, {self.name} -> {self.old_value}')
        setattr(self.obj, self.name, self.old_value)

    def redo(self):
        super().redo()
        logger.info(f'Setting attribute: {self.obj}, {self.name} -> {self.value}')
        setattr(self.obj, self.name, self.value)


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
            action.undo()
            self.app().doc.modified()

    def redo(self):
        if not self.redos:
            logger.warning('Redo queue is empty')
        else:
            action = self.redos.pop()
            self.undos.append(action)
            action.redo()
            self.app().doc.modified()

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
