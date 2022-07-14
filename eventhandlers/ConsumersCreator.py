import pika
from EventsConsumer import EventsConsumer
from ActionConsumer import ActionsConsumer
from shared.settings import settings


class ConsumerCreator:
    connection: pika.BlockingConnection
    channel: pika.adapters.blocking_connection.BlockingChannel
    events_consumer: EventsConsumer
    actions_consumer: ActionsConsumer

    def __init__(self):
        self.create_consumers()

    def create_consumers(self):
        self.connection = pika.SelectConnection(
            pika.ConnectionParameters(host = settings.RABBITMQ_HOST,
                                      port = settings.RABBITMQ_PORT,
                                      credentials = pika.PlainCredentials(settings.RABBITMQ_DEFAULT_USER,
                                                                          settings.RABBITMQ_DEFAULT_PASS))
        )
        self.channel = self.connection.channel()
        self.events_consumer = EventsConsumer(channel = self.channel, connection = self.connection)
        self.actions_consumer = ActionsConsumer(channel = self.channel, connection = self.connection)

    def stop_processing(self):
        self.channel.stop_consuming()

    def start_processing(self):
        self.channel.start_consuming()
