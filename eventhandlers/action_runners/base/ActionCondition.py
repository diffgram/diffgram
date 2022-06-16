class ActionCondition:
    default_event: str
    event_list: list

    def __init__(self, default_event: str or None, event_list: list):
        self.default_event = default_event
        self.event_list = event_list

    def build_trigger_data(self) -> dict:
        return {
            'event_name': self.default_event,
            'event_list': self.event_list,
        }
