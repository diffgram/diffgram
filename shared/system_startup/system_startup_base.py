from abc import ABC, abstractmethod
from shared.settings import settings


class SystemStartupBase(ABC):

    def check_settings_values_validity(self):
        if not settings.URL_BASE:
            raise Exception(f'URL_BASE is not set. Please provide a value for URL_BASE')
        if not settings.URL_BASE.endswith('/'):
            settings.URL_BASE += '/'

    @abstractmethod
    def execute_startup_checks(self):
        raise NotImplementedError
