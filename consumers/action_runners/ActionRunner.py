from shared.database.action.action import Action
from shared.queuemanager.QueueManager import QueueManager, RoutingKeys
from shared.database.event.event import Event
from shared.regular import regular_log
mngr = QueueManager()


class ActionRunner:
    action: Action
    event_data: dict
    log: dict

    def __init__(self, action, event_data: dict):
        self.action = action
        self.event_data = event_data
        self.log = regular_log.default()

    def execute_pre_conditions(self, session):
        raise NotImplementedError

    def run(self, session):
        raise NotImplementedError

    def declare_action_complete(self, session):
        event = Event.new(
            session = session,
            action_id = self.action.id,
            kind = 'action_completed',
            project_id = self.action.project_id,

        )
        event_data = event.serialize()
        mngr.send_message(message = event_data, routing_key = RoutingKeys.action_trigger_event_new.value)
