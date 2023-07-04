import traceback
import time
from shared.shared_logger import get_shared_logger

logger = get_shared_logger()


def get_cpu_percent():
    import psutil
    cpu_percent = None
    try:
        cpu_percent = psutil.cpu_percent()
    except Exception as e:
        logger.warn(traceback.format_exc())

    return cpu_percent


def is_cpu_available(limit: float):
    cpu_percent = get_cpu_percent()
    logger.debug(f'Checking for CPU {cpu_percent}%')
    if cpu_percent is None: return True  # Don't stop if this check fails

    if cpu_percent > limit:
        logger.warn(f"[CPU] {cpu_percent} % used is > {limit} limit.")
        return False

    return True


def check_and_wait_for_cpu(limit = 3.0, check_interval = 5):
    while True:
        if is_cpu_available(limit = limit):
            return True
        else:
            logger.warn("CPU at set limit. Please wait.")
            time.sleep(check_interval)
