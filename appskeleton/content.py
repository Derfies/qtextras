import abc


class Content(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def load(self):
        ...

    @abc.abstractmethod
    def save(self):
        ...
