from eventhandlers.action_runners.base.ActionRunner import ActionRunner
from eventhandlers.action_runners.base.ActionTrigger import ActionTrigger
from eventhandlers.action_runners.base.ActionCondition import ActionCondition
from eventhandlers.action_runners.base.ActionCompleteCondition import ActionCompleteCondition


class MySampleAction(ActionRunner):
    public_name = 'your_action_name'
    icon = 'https://www.svgrepo.com/show/46774/export.svg'
    kind = 'my_sample_action'  # The kind has to be unique to all actions
    category = 'some_category'  # Optional

    # What events can this action listen to?
    trigger = ActionTrigger(default_event = 'some_diffgram_event', event_list = ['some_diffgram_event'])

    condition_data = ActionCondition()  # What pre-conditions can this action have?
    completion_condition_data = ActionCompleteCondition()  # How to declare the actions as completed?

    def execute_pre_conditions(self, session) -> bool:
        # Return true if no pre-conditions are needed.
        return True

    def execute_action(self, session):
        # Your core Action logic will go here.
        pass
