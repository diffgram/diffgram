import json
import functools
from pika.exchange_type import ExchangeType
import pika
import threading
from pika.exchange_type import ExchangeType
from shared.queuemanager.QueueManager import RoutingKeys, Exchanges, QueueNames
from shared.shared_logger import get_shared_logger
from shared.database.action.action import Action
from shared.database.action.workflow import Workflow
from shared.helpers import sessionMaker
logger = get_shared_logger()

trigger_kinds_with_custom_metadata = {
    'input_file_uploaded': True
}


class ActionsConsumer:

    def __init__(self, channel, connection):
        self.channel = channel
        self.connection = connection
        self.exchange = self.channel.exchange_declare(
            exchange = Exchanges.actions.value,
            exchange_type = ExchangeType.direct.value,
            passive = False,
            auto_delete = False
        )
        self.channel.queue_declare(queue = QueueNames.action_triggers.value)
        self.channel.queue_bind(
            queue = QueueNames.action_triggers.value,
            exchange = Exchanges.actions.value,
            routing_key = RoutingKeys.action_trigger_event_new.value)
        self.channel.basic_qos(prefetch_count = 1)
        threads = []
        on_message_callback = functools.partial(ActionsConsumer.on_message, args = (connection, threads))
        self.channel.basic_consume(queue = QueueNames.action_triggers.value,
                                   on_message_callback = ActionsConsumer.process_action_trigger_event,
                                   auto_ack = True)

    @staticmethod
    def on_message(ch, method_frame, _header_frame, body, args):
        (conn, thrds) = args
        delivery_tag = method_frame.delivery_tag
        t = threading.Thread(target = ActionsConsumer.process_action_trigger_event, args = (conn, ch, delivery_tag, body))
        t.start()
        thrds.append(t)

    @staticmethod
    def filter_actions_matching_directory_trigger(actions_list, event_data):
        """
            Returns actions that have the matching directory_id from the event_data.
        :param actions_list:
        :param event_data:
        :return:
        """
        result = []
        for a in actions_list:
            if a.trigger_data.get('directory_id') is None:
                return
            if a.trigger_data.get('directory_id') == event_data.get('directory_id'):
                result.append(a)
        return result

    @staticmethod
    def filter_from_trigger_metadata(kind, event_data, actions_list):
        if trigger_kinds_with_custom_metadata.get(kind):
            if kind == 'file_upload':
                result = ActionsConsumer.filter_actions_matching_directory_trigger(event_data = event_data,
                                                                                   actions_list = actions_list)
                return result
        return actions_list

    @staticmethod
    def process_action_trigger_event(channel, method, properties, msg):
        """
            Receives a trigger event a finds any actions matching the event trigger for action
            execution.
        :return:
        """
        with sessionMaker.session_scope_threaded() as session:
            msg_data = json.loads(msg)
            kind = msg_data.get('kind')
            project_id = msg_data.get('project_id')
            if not project_id:
                logger.warning(f'Invalid project_id {project_id}')
                return
            if not kind:
                logger.warning(f'Invalid event kind {kind}')
                return

            actions_list = Action.get_triggered_actions(session = session, trigger_kind = kind, project_id = project_id)
            logger.info(f'Matched with {len(actions_list)} actions.')
            actions_list = ActionsConsumer.filter_from_trigger_metadata(kind, msg_data, actions_list)
            logger.info(f'Filtered to {len(actions_list)} actions.')
            for action in actions_list:
                action_runner = action.get_runner(event_data = msg_data)
                action_runner.run()