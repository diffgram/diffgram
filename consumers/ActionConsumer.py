from pika.exchange_type import ExchangeType
import pika
import threading
from pika.exchange_type import ExchangeType


class ActionsConsumer:
    num_threads = 2
    EXCHANGE_NAME = 'actions'
    TRIGGERS_QUEUE_NAME = 'actions.triggers'
    ROUTE_KEY = 'actions.trigger'


    def __init__(self, num_threads = 2):
        threading.Thread.__init__(self)
        self.num_threads = num_threads
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.exchange = self.channel.exchange_declare(
            exchange = self.EXCHANGE_NAME,
            exchange_type = ExchangeType.direct,
            durable = True,
            passive = False,
            auto_delete = False
        )
        self.channel.queue_declare(queue = self.TRIGGERS_QUEUE_NAME)
        self.channel.queue_bind(
            queue = self.TRIGGERS_QUEUE_NAME,
            exchange = self.EXCHANGE_NAME,
            routing_key = self.ROUTE_KEY)
        self.channel.basic_qos(prefetch_count = 1)
        self.channel.basic_consume(queue = self.TRIGGERS_QUEUE_NAME,
                                   on_message_callback = self.process_trigger_event(),
                                   auto_ack = False)

    def start_processing(self):
        self.channel.start_consuming()

    def process_trigger_event(self):
        """
            Receives a trigger event a finds any actions matching the event trigger for action
            execution.
        :return:
        """
