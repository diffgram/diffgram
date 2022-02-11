import threading


def publish_message(event_data):
    """
        Emits and event to the receiver.
        (Eventually we will replace this with a QueueSystem)

    :param event_data:
    :return:
    """
    raise NotImplementedError


class EventReceiver:
    """
        Temporal implementation of event receivers for async operations.
        In the future this should be handled by a queue system and then sent
        to the appropriate worker service to process it.
    """

    def receive(self, event_data):
        evt_type = event_data.get('type')

        t = threading.Thread(
            target = lambda x: x,  # Replace with function to use
            kwargs = locals().get('kwargs'))
        t.daemon = True  # Allow hot reload to work
        t.start()
