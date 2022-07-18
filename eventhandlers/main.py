from shared.database_setup_supporting import *
from shared.shared_logger import get_shared_logger
from ConsumersCreator import ConsumerCreator
from shared.settings import settings
from startup.system_startup_checker import EventHandlerSystemStartupChecker
from action_runners.ActionRegistrar import register_all
import traceback
logger = get_shared_logger()

startup_checker = EventHandlerSystemStartupChecker()
startup_checker.execute_startup_checks()

# Register runners
register_all()

consumer_creator = ConsumerCreator()

logger.info(f'Listening for messages in {settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}')
try:
    consumer_creator.run()
    logger.info(f'Finished Processing Messages')
except Exception as e:
    data = traceback.format_exc()
    logger.error(f'Error Processing event: {data}')