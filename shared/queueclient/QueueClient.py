import pika
from pika.exchange_type import ExchangeType
import json
from enum import Enum
from shared.settings import settings
import ssl


class QueueNames(Enum):
    action_triggers = 'actions.triggers'
    events_new = 'event.new'
    job_tasks = 'job.tasks'


class Exchanges(Enum):
    actions = 'actions'
    events = 'events'
    exports = 'exports'
    jobs = 'jobs'


class RoutingKeys(Enum):
    action_trigger_event_new = 'actions.new_actions_trigger'
    event_new = 'events.new'
    job_add_task = 'job.add_task'


class QueueClient:

    def __init__(self):
        if settings.DIFFGRAM_SYSTEM_MODE == 'testing':
            return
        ssl_options = None
        if settings.RABBITMQ_USE_SSL:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            ssl_context.set_ciphers('ECDHE+AESGCM:!ECDSA')
            ssl_options = pika.SSLOptions(context = ssl_context)

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host = settings.RABBITMQ_HOST,
                                      port = settings.RABBITMQ_PORT,
                                      ssl_options = ssl_options,
                                      heartbeat = 10,
                                      credentials = pika.PlainCredentials(settings.RABBITMQ_DEFAULT_USER,
                                                                          settings.RABBITMQ_DEFAULT_PASS))
        )
        self.main_channel = self.connection.channel()

        self.main_channel.exchange_declare(exchange = Exchanges.actions.value,
                                           exchange_type = ExchangeType.direct.value)
        self.main_channel.exchange_declare(
            exchange = Exchanges.events.value,
            exchange_type = ExchangeType.direct.value)

        self.main_channel.exchange_declare(
            exchange = Exchanges.exports.value,
            exchange_type = ExchangeType.direct.value)

    def send_message(self,
                     message: dict,
                     routing_key: str,
                     exchange: str):
        """
            Publishes a message to rabbit MQ. For now its using the default
            actions exchange. But we can modify this wrapper to include more paremeters
            for the exchange name.
        :param message:
        :param routing_key:
        :param exchange:
        :return:
        """
        self.main_channel.basic_publish(
            exchange = exchange,
            routing_key = routing_key,
            body = json.dumps(message).encode('utf-8'),
            properties = pika.BasicProperties(content_type = 'application/json'))
