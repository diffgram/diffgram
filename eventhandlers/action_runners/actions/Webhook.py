import requests
import traceback
from action_runners.base.ActionRunner import ActionRunner
from action_runners.base.ActionTrigger import ActionTrigger
from action_runners.base.ActionCondition import ActionCondition
from action_runners.base.ActionCompleteCondition import ActionCompleteCondition
from shared.shared_logger import get_shared_logger

logger = get_shared_logger()


class WebhookAction(ActionRunner):
    public_name = 'Webhook'
    description = 'Sends POST Request to Given URL With Event Data. Expects 200 Response.'
    icon = 'data:image/png;base64,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'
    kind = 'Webhook'  # The kind has to be unique to all actions
    category = 'some_category'  # Optional

    # What events can this action listen to
    trigger_data = ActionTrigger(default_event = 'input_file_uploaded',
                                 event_list = ['input_file_uploaded',
                                               'task_created',
                                               'task_completed',
                                               'task_review_start',
                                               'task_request_changes',
                                               'task_review_complete',
                                               'task_in_progress',
                                               'task_comment_created',
                                               'task_template_completed',
                                               'file_copy',
                                               'file_move',
                                               'file_mirror'])

    # What pre-conditions can this action have
    precondition = ActionCondition(default_event = None, event_list = [])

    # How to declare the actions as completed
    completion_condition_data = ActionCompleteCondition(default_event = 'action_completed',
                                                        event_list = ['action_completed'])

    def execute_pre_conditions(self, session) -> bool:
        # Return true if no pre-conditions are needed.
        return True

    def execute_action(self, session) -> bool:
        url = self.action.config_data.get('url')
        token = self.action.config_data.get('token')
        if url is None:
            logger.error(f'Error on webhook: provide URL to post')
            return False
        if url is None:
            logger.error(f'Error on webhook: provide URL to post')
            return False

        try:
            # Your core Action logic will go here.
            self.event_data['token'] = token
            self.event_data['workflow_id'] = self.action.workflow_id
            self.event_data['action_id'] = self.action.id
            self.event_data['action_run_id'] = self.action_run.id
            response = requests.post(json = self.event_data, url=url)
            if response.status_code == 200:
                data = {}
                try:
                    data['response'] = response.json()
                except Exception as e:
                    data['response'] = 'No JSON Response found.'
                data['event_payload'] = self.event_data
                data['status_code'] = response.status_code
                data['url'] = url
                return data
            else:
                logger.error(f'Error on Webhook. Invalid Response {response.status_code}')
                self.save_error_output(data={'status_code': response.status_code,
                                             'response': response.text,
                                             'url': url,
                                             'event_payload': self.event_data},
                                       session = self.session)
                return False
        except Exception as e:
            msg = traceback.format_exc()
            logger.error(f'Error on Webhook: {msg}')
            return False
