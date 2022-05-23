import pika
from pika.exchange_type import ExchangeType
import json
from enum import Enum
from shared.settings import settings


class QueueNames(Enum):
    action_triggers = 'actions.triggers'
    events_new = 'event.new'


class Exchanges(Enum):
    actions = 'actions'
    events = 'events'
    exports = 'exports'


class RoutingKeys(Enum):
    action_trigger_event_new = 'actions.new_actions_trigger'
    event_new = 'events.new'


class QueueClient:

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host = settings.RABBITMQ_HOST,
                                      port = settings.RABBITMQ_PORT,
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
