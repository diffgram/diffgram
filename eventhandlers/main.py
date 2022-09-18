from shared.database_setup_supporting import *
from shared.shared_logger import get_shared_logger
from shared.database.action.action_run import ActionRun
from ConsumersCreator import ConsumerCreator
from shared.settings import settings
from startup.system_startup_checker import EventHandlerSystemStartupChecker
from action_runners.ActionRegistrar import register_all
from shared.helpers import sessionMaker
import traceback
import atexit

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

def exit_handler():
    with sessionMaker.session_scope_threaded() as session:
        ActionRun.shout_down_running_actions(session)

atexit.register(exit_handler)