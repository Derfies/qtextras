import abc


class ContentBase(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def load(self, file_path: str):
        ...

    @abc.abstractmethod
    def save(self, file_path: str):
        ...
