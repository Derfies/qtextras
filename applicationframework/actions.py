import abc
import logging
import weakref

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication


logger = logging.getLogger(__name__)


class ActionBase(metaclass=abc.ABCMeta):

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


class Edit(ActionBase):

    def __init__(self, obj):

        # TODO: Maybe don't use weak ref, as certain actions that remove an
        # object (and thus result in it being garbage collected) are never
        # retrievable.
        self._ref = weakref.ref(obj)


class SetAttribute(Edit):

    def __init__(self, name, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.value = value
        self.old_value = getattr(self._ref(), name)

    def undo(self):
        super().undo()
        setattr(self._ref(), self.name, self.old_value)

    def redo(self):
        super().redo()
        setattr(self._ref(), self.name, self.value)


class Manager:

    def __init__(self):
        self.undos = []
        self.redos = []

    def app(self) -> QCoreApplication:
        return QApplication.instance()

    def undo(self):
        if not self.undos:
            logger.info('No more undo')
        else:
            action = self.undos.pop()
            self.redos.append(action)
            action.undo()
            self.app().doc.on_modified()

    def redo(self):
        if not self.redos:
            logger.info('No more redo')
        else:
            action = self.redos.pop()
            self.undos.append(action)
            action.redo()
            self.app().doc.on_modified()

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
