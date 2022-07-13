class ActionCompleteCondition:
    default_event: str
    event_list: list

    def __init__(self, default_event: str, event_list: list):
        self.default_event = default_event
        self.event_list = event_list

    def build_event_list(self, event_list: list) -> list:
        res = []
        for e in event_list:
            res.append({
                'name': e,
                'value': e
            })
        return res

    def build_data(self) -> dict:
        event_list = self.build_event_list(self.event_list)
        return {
            'default_event_name': self.default_event,
            'event_list': event_list,
        }