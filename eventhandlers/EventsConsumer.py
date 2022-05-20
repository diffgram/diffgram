import json

from pika.exchange_type import ExchangeType
import pika
import threading
from pika.exchange_type import ExchangeType
from shared.queuemanager.QueueManager import RoutingKeys, Exchanges, QueueNames
from shared.database.action.action import ActionTriggerEventTypes
from shared.shared_logger import get_shared_logger
from shared.queuemanager.QueueManager import QueueManager
import functools

logger = get_shared_logger()


class EventsConsumer:

    def __init__(self, channel, connection):
        self.channel = channel
        self.connection = connection
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
        threads = []
        on_message_callback = functools.partial(EventsConsumer.on_message, args = (connection, threads))
        self.channel.basic_consume(queue = QueueNames.events_new.value,
                                   on_message_callback = on_message_callback,
                                   auto_ack = True)

    @staticmethod
    def on_message(ch, method_frame, _header_frame, body, args):
        (conn, thrds) = args
        delivery_tag = method_frame.delivery_tag
        t = threading.Thread(target = EventsConsumer.process_new_event, args = (conn, ch, delivery_tag, body))
        t.start()
        thrds.append(t)

    @staticmethod
    def process_new_event(channel, method, properties, msg):
        """
            Receives a trigger event a finds any actions matching the event trigger for action
            execution.
        :return:
        """
        queuemanager = QueueManager()
        msg_data = json.loads(msg)
        logger.info(f'New Event Message: {msg}')
        kind = msg_data.get('kind')
        if not kind:
            logger.info(f'Event was discarded. Kind is {kind}')
            return

        actions_kinds_list = [k.value for k in ActionTriggerEventTypes]

        if kind in actions_kinds_list:
            logger.info("Event Matched Action Triggers. Publishing Action Trigger Message...")
            queuemanager.send_message(message = msg_data,
                                      routing_key = RoutingKeys.action_trigger_event_new.value,
                                      exchange = Exchanges.actions.value)
        else:
            logger.info(f'No matching actions for event. Kind is {kind}')
