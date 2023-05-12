from eventhandlers.action_runners.base.ActionRunner import ActionRunner
from eventhandlers.action_runners.base.ActionTrigger import ActionTrigger
from eventhandlers.action_runners.base.ActionCondition import ActionCondition
from eventhandlers.action_runners.base.ActionCompleteCondition import ActionCompleteCondition


class MongoDBTextFileImportAction(ActionRunner):
    public_name = 'MongoDBTextFileImport'
    description = ''
    icon = 'https://www.svgrepo.com/show/46774/export.svg'
    kind = 'MongoDBTextFileImport'  # The kind has to be unique to all actions
    category = 'some_category'  # Optional

    # What events can this action listen to?
    trigger_data = ActionTrigger(default_event = 'some_diffgram_event',
                            event_list = ['some_diffgram_event'])

    # What pre-conditions can this action have?
    condition_data = ActionCondition(default_event = 'some_diffgram_event',
                                     event_list = ['some_diffgram_event'])

    # How to declare the actions as completed?
    completion_condition_data = ActionCompleteCondition(default_event = 'some_diffgram_event',
                                                        event_list = ['some_diffgram_event'])

    def execute_pre_conditions(self, session) -> bool:
        # Return true if no pre-conditions are needed.
        return True

    def execute_action(self, session):
        # Your core Action logic will go here.
        pass