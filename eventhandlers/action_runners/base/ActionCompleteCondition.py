class ActionCompleteCondition:
    """A class representing a condition for completing an action.

    Attributes:
        default_event (str): The default event to trigger if no other events are specified.
        event_list (List[str]): A list of events that can trigger the completion of the action.
    """

    def __init__(self, default_event: str, event_list: List[str]):
        """Initialize an ActionCompleteCondition instance.

        Args:
            default_event (str): The default event to trigger if no other events are specified.
            event_list (List[str]): A list of events that can trigger the completion of the action.
        """
        self.default_event = default_event
        self.event_list = event_list

    def build_event_list(self, event_list: List[str]) -> List[Dict[str, str]]:
        """Build a list of event dictionaries.

        Args:
            event_list (List[str]): A list of event names.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, each containing a single event name and value.
        """
        return [{
            'name': e,
            'value': e
        } for e in event_list]

    def build_data(self) -> Dict[str, Union[str, List[Dict[str, str]]]]:
        """Build a dictionary containing the default event name and a list of event dictionaries.

        Returns:
            Dict[str, Union[str, List[Dict[str, str]]]]: A dictionary containing the default event name and a list of event dictionaries.
        """
        event_list = self.build_event_list(self.event_list)
        return {
            'default_event_name': self.default_event,
            'event_list': event_list,
        }
