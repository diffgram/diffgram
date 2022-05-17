from shared.shared_logger import get_shared_logger
from consumers.ConsumersCreator import ConsumerCreator
logger = get_shared_logger()

consumer_creator = ConsumerCreator()
consumer_creator.start_processing()
logger.info(f'Queue Consumers Started.')