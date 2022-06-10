from shared.database_setup_supporting import *
from shared.shared_logger import get_shared_logger
from ConsumersCreator import ConsumerCreator
from shared.settings import settings
from startup.system_startup_checker import EventHandlerSystemStartupChecker
import traceback
logger = get_shared_logger()

startup_checker = EventHandlerSystemStartupChecker()
startup_checker.execute_startup_checks()

consumer_creator = ConsumerCreator()
logger.info(f'Queue Consumers Started. Waiting for new messages...')
logger.info(f'Listening for messages in {settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}')
execute = True
while execute:
    try:
        consumer_creator.start_processing()
        logger.info(f'Finished Processing Mesages')
    except KeyboardInterrupt:
        consumer_creator.stop_processing()
        execute = False
    except Exception as e:
        data = traceback.format_exc()
        logger.error(f'Error Processing event: {data}')