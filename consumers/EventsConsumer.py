import json

from pika.exchange_type import ExchangeType
import pika
import threading
from pika.exchange_type import ExchangeType
from shared.queuemanager.QueueManager import RoutingKeys, Exchanges, QueueNames
from enum import Enum
from shared.shared_logger import get_shared_logger
from shared.queuemanager.QueueManager import QueueManager

queuemanager = QueueManager()
logger = get_shared_logger()


class ActionTriggerEventTypes(Enum):
    task_completed = 'task_completed'
    task_created = 'task_created'
    task_template_completed = 'task_template_completed'
    input_file_uploaded = 'input_file_uploaded'
    input_instance_uploaded = 'input_instance_uploaded'
    action_completed = 'action_completed'


class EventsConsumer:

    def __init__(self, channel):
        self.channel = channel
        self.exchange = self.channel.exchange_declare(
            exchange = Exchanges.events.value,
            exchange_type = ExchangeType.direct.value,
            passive = False,
            auto_delete = False
        )
        self.channel.queue_declare(queue = QueueNames.events_new.value)
        self.channel.queue_bind(
            queue = QueueNames.events_new.value,
            exchange = Exchanges.events.value,
            routing_key = RoutingKeys.event_new.value)
        self.channel.basic_qos(prefetch_count = 1)
        self.channel.basic_consume(queue = QueueNames.events_new.value,
                                   on_message_callback = EventsConsumer.process_trigger_event,
                                   auto_ack = True)


    @staticmethod
    def process_trigger_event(channel, method, properties, msg):
        """
            Receives a trigger event a finds any actions matching the event trigger for action
            execution.
        :return:
        """
        print('channel', channel)
        print('method', method)
        print('properties', properties)
        print('body', msg)
        msg_data = json.loads(msg)
        logger.info(f'New Event Message: {msg}')
        kind = msg_data.get('kind')
        if not kind:
            logger.info(f'Event was discarded. Kind is {kind}')
            return

        actions_kinds_list = [k.value for k in ActionTriggerEventTypes]

        if kind in actions_kinds_list:
            logger.info("Event Matched Action Triggers. Publishing Action Trigger Message...")
            queuemanager.send_message(message = msg, routing_key = RoutingKeys.action_trigger_event_new.value)
        else:
            logger.info(f'No matching actions for event. Kind is {kind}')
