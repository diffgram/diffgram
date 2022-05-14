from shared.shared_logger import get_shared_logger
from consumers.ConsumersCreator import ConsumerCreator
logger = get_shared_logger()

if __name__ == '__main__':
    manager = ConsumerCreator.create_consumers()
    logger.info(f'Queue Consumers Started.')
