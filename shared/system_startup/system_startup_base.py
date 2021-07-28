from abc import ABC, abstractmethod


class SystemStartupBase(ABC):

    @abstractmethod
    def execute_startup_checks(self):
        raise NotImplementedError
