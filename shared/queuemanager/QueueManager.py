import pika
from pika.exchange_type import ExchangeType
from shared.utils.singleton import Singleton
import json
from enum import Enum
from shared.settings import settings


class QueueNames(Enum):
    action_triggers = 'actions.triggers'
    events_new = 'event.new'


class Exchanges(Enum):
    actions = 'actions'
    events = 'events'


class RoutingKeys(Enum):
    action_trigger_event_new = 'actions.new_actions_trigger'
    event_new = 'events.new'


class QueueManager(metaclass = Singleton):
    EXCHANGE_NAME_ACTIONS = 'actions'

    def __init__(self):
        print('qweqwe', settings.RABBITMQ_DEFAULT_PASS, settings.RABBITMQ_DEFAULT_USER)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host = 'localhost',
                                      credentials = pika.PlainCredentials(settings.RABBITMQ_DEFAULT_USER,
                                                                          settings.RABBITMQ_DEFAULT_PASS))
        )
        self.main_channel = self.connection.channel()

        self.main_channel.exchange_declare(exchange = self.EXCHANGE_NAME_ACTIONS,
                                           exchange_type = ExchangeType.direct)
        self.main_channel.exchange_declare(
            exchange = self.EXCHANGE_NAME_ACTIONS, exchange_type = ExchangeType.direct)

    def send_message(self, message: dict, routing_key: str):
        """
            Publishes a message to rabbit MQ. For now its using the default
            actions exchange. But we can modify this wrapper to include more paremeters
            for the exchange name.
        :param message:
        :return:
        """
        self.main_channel.basic_publish(
            exchange = self.EXCHANGE_NAME_ACTIONS,
            routing_key = routing_key,
            body = json.dumps(message),
            properties = pika.BasicProperties(content_type = 'application/json'))
