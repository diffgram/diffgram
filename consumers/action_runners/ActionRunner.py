from shared.database.action.action import Action
from shared.queuemanager.QueueManager import QueueManager, RoutingKeys

mngr = QueueManager()

class ActionRunner:
    action: Action
    event_data: dict

    def __init__(self, action, event_data: dict):
        self.action = action
        self.event_data = event_data

    def execute_pre_conditions(self):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError

    def declare_action_complete(self):
        event_data = self.action.serialize()
        event_data['kind'] =
        mngr.send_message(message = data, routing_key = RoutingKeys.action_trigger_event_new)