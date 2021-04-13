# OPEN CORE - ADD
from shared.utils.logging import DiffgramLogger
from shared.settings import settings


def get_shared_logger():
    shared_abstract_logger = DiffgramLogger('shared')
    shared_abstract_logger.configure_concrete_logger(system_mode=settings.DIFFGRAM_SYSTEM_MODE)
    logger = shared_abstract_logger.get_concrete_logger()
    return logger
