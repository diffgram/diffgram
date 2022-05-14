import pika
from consumers.EventsConsumer import EventsConsumer
from consumers.ActionConsumer import ActionsConsumer


class ConsumerCreator:

    def create_consumers(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        events_consumer = EventsConsumer(connection = connection)
        actions_consumer = ActionsConsumer(connection = connection)

        events_consumer.start_processing()
        actions_consumer.start_processing()
