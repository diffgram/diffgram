from shared.database.system_events.system_events import SystemEvents
from shared.system_startup.system_startup_base import SystemStartupBase
from methods.regular.regular_api import logger
from shared.settings import settings


class DefaultServiceSystemStartupChecker(SystemStartupBase):

    def __init__(self):
        self.service_name = settings.DIFFGRAM_SERVICE_NAME

    def check_settings_values_validity(self):
        if not settings.URL_BASE:
            raise Exception(f'URL_BASE is not set. Please provide a value for URL_BASE')
        if not settings.URL_BASE.endswith('/'):
            raise Exception(f'Invalid URL_BASE value setting: "{settings.URL_BASE}". URL_BASE should end with "/"')

    def execute_startup_checks(self):
        logger.info('[{}] Performing System Checks...'.format(self.service_name))
        self.check_settings_values_validity()
        result = SystemEvents.system_startup_events_check(self.service_name)
        if not result:
            raise Exception('System Startup Check Failed.')

        return result
