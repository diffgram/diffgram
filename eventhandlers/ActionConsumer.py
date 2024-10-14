import json
import logging
from pika import Channel, SelectConnection
from shared.queueclient.QueueClient import RoutingKeys, Exchanges, QueueNames
from shared.shared_logger import get_shared_logger
from shared.database.action.action import Action
from shared.database.action.workflow import Workflow
from action_runners.ActionRegistrar import get_runner
from shared.helpers import sessionMaker

LOGGER = get_shared_logger()
TRIGGER_KINDS_WITH_CUSTOM_METADATA = {
    'input_file_uploaded': True
}

class ActionsConsumer:
    """
    A class to consume action trigger events from RabbitMQ.
    """

    def __init__(self, channel: Channel, connection: SelectConnection):
        """
        Initialize the ActionsConsumer with a channel and connection.
        """
        self.channel = channel
        self.connection = connection
        self.__delare_exchange()

    def __delare_exchange(self):
        """
        Declare the exchange and bind the queue to it.
        """
        self.channel.exchange_declare(
            exchange=Exchanges.actions.value,
            exchange_type='direct',
            passive=False,
            auto_delete=False,
            callback=self.on_exchange_declareok
        )

    def on_exchange_declareok(self, channel, frame):
        """
        Callback method for exchange declaration.
        """
        self.channel.queue_declare(queue=QueueNames.action_triggers.value)
        self.channel.queue_bind(
            queue=QueueNames.action_triggers.value,
            exchange=Exchanges.actions.value,
            routing_key=RoutingKeys.action_trigger_event_new.value
        )
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=QueueNames.action_triggers.value,
            on_message_callback=self.on_message,
            auto_ack=True
        )
        LOGGER.info('Queues ready to listen for messages')

    @staticmethod
    def filter_actions_matching_directory_trigger(actions_list, event_data):
        """
        Returns actions that have the matching directory_id from the event_data.
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
        """
        Filters the list of actions based on the trigger metadata.
        """
        if trigger_kinds_with_custom_metadata.get(kind):
            if kind == 'file_uploaded':
                result = ActionsConsumer.filter_actions_matching_directory_trigger(event_data, actions_list)
                return result
        if kind == 'action_completed':
            filtered_list = []
            action_id = event_data.get('action_id')
            if action_id is None:
                return filtered_list
            for action in actions_list:
                prev_action = action.get_previous_action(session=session)
                if prev_action.id == action_id:
                    filtered_list.append(action)
            return filtered_list
        return actions_list

    @staticmethod
    def process_actions(session, actions_list, event_data):
        """
        Process the list of actions.
        """
        for action in actions_list:
            session.add(action)
            LOGGER.info(f'Getting action {action.kind}')
            action_runner = get_runner(session=session, action=action, event_data=event_data)
            action_runner.run()

    def stop(self):
        """
        Stop the consumer.
        """
        self.connection.close()

    def on_message(self, channel, method_frame, header_frame, body):
        """
        Callback method for message processing.
        """
        try:
            msg_data = json.loads(body)
            kind = msg_data.get('kind')
            project_id = msg_data.get('project_id')
            LOGGER.debug(f'Processing action trigger event {body}')
            if not project_id:
                LOGGER.warning(f'Invalid project_id {project_id}')
                return
            if not kind:
                LOGGER.warning(f'Invalid event kind {kind}')
                return

            actions_list = Action.get_triggered_actions(session=session, trigger_kind=kind, project_id=project_id)
            LOGGER.debug(f'Matched with {len(actions_list)} actions.')
            actions_list = self.filter_from_trigger_metadata(session, kind, msg_data, actions_list)
            LOGGER.debug(f'Filtered to {len(actions_list)} actions.')
            with sessionMaker.session_scope_threaded() as session:
                self.process_actions(session, actions_list, msg_data)
        except Exception as e:
            LOGGER.error(f'Error processing message: {e}')
