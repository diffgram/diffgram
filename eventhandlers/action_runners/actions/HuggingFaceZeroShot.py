from action_runners.base.ActionRunner import ActionRunner
from eventhandlers.action_runners.base.ActionTrigger import ActionTrigger
from eventhandlers.action_runners.base.ActionCondition import ActionCondition
from eventhandlers.action_runners.base.ActionCompleteCondition import ActionCompleteCondition
from shared.shared_logger import get_shared_logger
from shared.database.task.job.job import Job
from shared.helpers.sessionMaker import session_scope
from shared.utils import job_dir_sync_utils
from shared.database.source_control.file import File
from shared.ingest import packet
from transformers import pipeline


logger = get_shared_logger()


class HuggingFaceZeroShotAction(ActionRunner):
    public_name = 'Zero Shot Classification (Hugging Face)'
    description = 'Performs Zero Shot Classification for the text file'
    icon = 'https://huggingface.co/front/assets/huggingface_logo-noborder.svg'
    kind = 'HuggingFaceZeroShotAction'
    trigger_data = ActionTrigger(default_event='task_created', event_list = ['task_created', 'input_file_uploaded'])
    condition_data = ActionCondition(default_event = 'action_completed',
                                     event_list = ['action_completed'])

    completion_condition_data = ActionCompleteCondition(default_event = 'action_completed',
                                                        event_list = ['action_completed'])
    category = 'nlp'

    def execute_pre_conditions(self, session) -> bool:
        return True

    def test_execute_action(self, session, file_id, connection_id):
        pass

    def execute_action(self, session, do_save_annotations=True):
        print("Hugging face has been executed")
        return
        """
                    Creates a task from the given file_id in the given task template ID.
                :return:
                """

        file_id = self.event_data['file_id']
        if not file_id:
            logger.warning(f'Action has no file_id Stopping execution')
            return
    
        file = File.get_by_id(session, file_id = file_id)
    
        raw_text = file.text_file.get_text()
        # or could get tokens etc
        
        # Actual Prediction
        # TODO get example labels from schema
        candidate_labels = ["renewable", "politics", "emission", "temperature", "emergency", "advertisment"]

        classifier = pipeline("zero-shot-classification")

        result = classifier(raw_text, candidate_labels)

        print(result)

        # TODO load result based on mapping...
        
        result = [doc for doc in response if not doc.is_error]
    
        # Save annotations
    
        # Call ExternalMap
        # Bit of an odd one in mocking global attribute map.
        mock_external_map = {
            "negative" : {89 : {display_name: "neutral", id: 241, name: 242}},
            "positive" : {89 : {display_name: "neutral", id: 240, name: 242}},
            "neutral": {89 : {display_name: "neutral", id: 242, name: 242}}
            }
    
        instance_list = []
        for doc in result:
            print("Overall sentiment: {}".format(doc.sentiment))
            print("Scores: positive={}; neutral={}; negative={} \n".format(
                doc.confidence_scores.positive,
                doc.confidence_scores.neutral,
                doc.confidence_scores.negative,
            ))
            instance_list.append({
                #'name': mock_external_map[doc.sentiment],
                #'start_sentence': instance['sidS'],
                #'end_sentence': instance['sidE'],
                #'start_token': instance['s'],
                #'end_token': instance['e'],
                #'start_char': instance['charS'],
                #'end_char': instance['charE'],
                #'sentence': sentence['id'],
                'type': 'global',
                'attribute_groups': mock_external_map[doc.sentiment]
            })
    
        if do_save_annotations is True:
            # For tracking and flexbility
            packet.enqueue_packet(
                session=session,
                media_url=None,
                media_type='text',
                file_id=file.id,
                instance_list=instance_list,
                commit_input=True,
                mode="update")
    
    def create_action_template():
        Action_Template.new(
            session = session,
            public_name = 'Hugging Face Text Zero Shot',
            description = 'Hugging Face Text Zero Shot',
            icon = 'https://www.svgrepo.com/show/46774/export.svg',
            kind = 'HuggingFaceZeroShotAction',
            category = None,
            #trigger_data = {'trigger_event_name': 'task_completed'},
            #condition_data = {'event_name': 'all_tasks_completed'},
            #completion_condition_data = {'event_name': 'prediction_success'},
        )