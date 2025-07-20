from abc import ABC, abstractmethod


class StateGenerator(ABC):
    @abstractmethod
    def generate(self): ...