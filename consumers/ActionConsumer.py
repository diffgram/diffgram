import json

from pika.exchange_type import ExchangeType
import pika
import threading
from pika.exchange_type import ExchangeType
from shared.queuemanager.QueueManager import RoutingKeys, Exchanges, QueueNames
from shared.shared_logger import get_shared_logger
from shared.database.action.action import Action
from shared.database.action.workflow import Workflow
logger = get_shared_logger()


class ActionsConsumer:
    num_threads = 2

    def __init__(self, num_threads = 2):
        threading.Thread.__init__(self)
        self.num_threads = num_threads
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.exchange = self.channel.exchange_declare(
            exchange = Exchanges.actions.value,
            exchange_type = ExchangeType.direct.value,
            durable = True,
            passive = False,
            auto_delete = False
        )
        self.channel.queue_declare(queue = QueueNames.action_triggers.value)
        self.channel.queue_bind(
            queue = QueueNames.action_triggers.value,
            exchange = Exchanges.actions.value,
            routing_key = RoutingKeys.action_trigger_event_new.value)
        self.channel.basic_qos(prefetch_count = 1)
        self.channel.basic_consume(queue = QueueNames.action_triggers.value,
                                   on_message_callback = self.process_trigger_event,
                                   auto_ack = False)

    def start_processing(self):
        self.channel.start_consuming()

    def process_trigger_event(self, msg):
        """
            Receives a trigger event a finds any actions matching the event trigger for action
            execution.
        :return:
        """
        msg_data = json.loads(msg)
        kind = msg_data.get('kind')
        if not kind:
            logger.warning(f'Invalid event kind {kind}')
            return

        actions_list = Action.get_triggered_actions(trigger_kind = kind)

        for action in actions_list:
            action_runner = action.get_runner()
