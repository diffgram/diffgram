import json
import functools
import pika
import threading
from pika.exchange_type import ExchangeType
from shared.queueclient.QueueClient import RoutingKeys, Exchanges, QueueNames
from shared.shared_logger import get_shared_logger
from shared.database.action.action import Action
from shared.database.action.workflow import Workflow
from action_runners.ActionRegistrar import get_runner
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
    def filter_from_trigger_metadata(session, kind, event_data, actions_list):
        if trigger_kinds_with_custom_metadata.get(kind):
            if kind == 'file_uploaded':
                result = ActionsConsumer.filter_actions_matching_directory_trigger(event_data = event_data,
                                                                                   actions_list = actions_list)
                return result
        if kind == 'action_completed':
            # If the action is listening to action completed, we need to make sure the action that was completed
            # is the previous action.
            filtered_list = []
            action_id = event_data.get('action_id')
            if action_id is None:
                return  filtered_list
            for action in actions_list:
                prev_action = action.get_previous_action(session = session)
                if prev_action.id == action_id:
                    filtered_list.append(action)
            return filtered_list
        return actions_list

    @staticmethod
    def process_action_trigger_event(channel, method, properties, msg):
        """
            Receives a trigger event a finds any actions matching the event trigger for action
            execution.
        :return:
        """
        print(msg)
        with sessionMaker.session_scope_threaded() as session:
            msg_data = json.loads(msg)
            kind = msg_data.get('kind')
            project_id = msg_data.get('project_id')
            logger.debug(f'Processing action trigger event {msg}')
            if not project_id:
                logger.warning(f'Invalid project_id {project_id}')
                return
            if not kind:
                logger.warning(f'Invalid event kind {kind}')
                return

            actions_list = Action.get_triggered_actions(session = session, trigger_kind = kind, project_id = project_id)
            logger.debug(f'Matched with {len(actions_list)} actions.')
            actions_list = ActionsConsumer.filter_from_trigger_metadata(session, kind, msg_data, actions_list)
            logger.debug(f'Filtered to {len(actions_list)} actions.')
            for action in actions_list:
                action_runner = get_runner(action = action, event_data = msg_data)
                action_runner.run()