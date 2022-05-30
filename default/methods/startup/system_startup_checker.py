from shared.database.system_events.system_events import SystemEvents
from shared.system_startup.system_startup_base import SystemStartupBase
from methods.regular.regular_api import logger
from shared.settings import settings
from shared.queueclient.QueueClient import QueueClient
import traceback
class DefaultServiceSystemStartupChecker(SystemStartupBase):

    def __init__(self):
        self.service_name = settings.DIFFGRAM_SERVICE_NAME

    def execute_startup_checks(self):
        logger.info(f"[{self.service_name}] Performing System Checks...")
        self.check_settings_values_validity()
        result = SystemEvents.system_startup_events_check(self.service_name)
        # Make Connection to Queue
        try:
            client = QueueClient()
        except Exception as e:
            data = traceback.format_exc()
            logger.error(data)
            logger.error(f'Error connecting to rabbit MQ')
            raise (Exception('Error connecting to RabbitMQ'))

        return result
