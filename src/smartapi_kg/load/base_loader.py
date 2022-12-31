from abc import ABC, abstractmethod


class BaseLoader(ABC):
    @abstractmethod
    def fetch(self):
        pass

    @abstractmethod
    def parse(self, _input):
        pass

    @abstractmethod
    def load(self):
        pass
