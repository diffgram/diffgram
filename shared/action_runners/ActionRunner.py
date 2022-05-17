from shared.database.action.action import Action
from shared.queuemanager.QueueManager import QueueManager, RoutingKeys
from shared.database.event.event import Event
from shared.regular import regular_log
from shared.helpers.sessionMaker import session_scope
from consumers.action_runners.ExportActionRunner import ExportActionRunner
from consumers.action_runners.TaskTemplateActionRunner import TaskTemplateActionRunner
mngr = QueueManager()

ACTION_RUNNERS_KIND_MAPPER = {
    'create_task': TaskTemplateActionRunner,
    'export': ExportActionRunner,
}

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

    def execute_action(self, session):
        raise NotImplementedError

    def run(self):
        with session_scope() as session:
            self.execute_pre_conditions(session)
            success = self.execute_action(session)
            if success:
                self.declare_action_complete(session)
            else:
                self.declare_action_failed(session)
    def declare_action_failed(self, session):
        event = Event.new(
            session = session,
            action_id = self.action.id,
            kind = 'action_failed',
            project_id = self.action.project_id,

        )
        event_data = event.serialize()
        mngr.send_message(message = event_data, routing_key = RoutingKeys.action_trigger_event_new.value)

    def declare_action_complete(self, session):
        event = Event.new(
            session = session,
            action_id = self.action.id,
            kind = 'action_completed',
            project_id = self.action.project_id,

        )
        event_data = event.serialize()
        mngr.send_message(message = event_data, routing_key = RoutingKeys.action_trigger_event_new.value)
