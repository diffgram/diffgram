import traceback
import time
from shared.shared_logger import get_shared_logger

logger = get_shared_logger()


def get_memory_percent():
    import psutil

    memory_percent = None
    try:
        psutil_memory_result = psutil.virtual_memory()
        memory_percent = psutil_memory_result[2]
    except Exception as e:
        logger.warn(traceback.format_exc())

    return memory_percent


def is_memory_available(memory_limit_float = 75.0):
    memory_percent = get_memory_percent()
    logger.info(f'Checking for memory {memory_percent}%')
    if memory_percent is None: return True  # Don't stop if this check fails

    if memory_percent > memory_limit_float:
        logger.warn(f"[Memory] {memory_percent} % used is > {memory_limit_float} limit.")
        return False

    return True


def check_and_wait_for_memory(memory_limit_float = 85.0, check_interval = 5):
    while True:
        if is_memory_available(memory_limit_float = memory_limit_float):
            return True
        else:
            logger.warn("No memory available, waiting. There is no harm if processing large amount please wait.")
            time.sleep(check_interval)
