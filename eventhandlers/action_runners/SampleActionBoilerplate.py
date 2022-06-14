from eventhandlers.action_runners.ActionRunner import ActionRunner


class MySampleAction(ActionRunner):
    public_name = 'your_action_name'
    icon = 'https://www.svgrepo.com/show/46774/export.svg'
    kind = 'my_sample_action'  # The kind has to be unique to all actions
    category = 'some_category'  # Optional
    trigger_data = {'trigger_event_name': 'some_diffgram_event'}  # What events can this action listen to?
    condition_data = {'event_name': 'some_diffgram_event'}  # What pre-conditions can this action have?
    completion_condition_data = {'event_name': 'some_diffgram_event'}  # What options are available to declare the actions as completed?

    def execute_pre_conditions(self, session) -> bool:
        # Return true if no pre-conditions are needed.
        return True

    def execute_action(self, session):
        # Your core Action logic will go here.
        pass
