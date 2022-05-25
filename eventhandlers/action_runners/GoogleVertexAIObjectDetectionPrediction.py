from eventhandlers.action_runners.ActionRunner import ActionRunner
from shared.shared_logger import get_shared_logger
from shared.database.task.job.job import Job
from shared.helpers.sessionMaker import session_scope
from shared.utils import job_dir_sync_utils
from shared.database.source_control.file import File
from methods.input.packet import enqueue_packet

logger = get_shared_logger()


class GoogleVertexAIObjectDetectionPrediction(ActionRunner):
    def execute_pre_conditions(self, session) -> bool:
        return True


    def test_execute_action(self, session, file_id, connection_id):
        pass

    def execute_action(self, session, do_save_annotations=True):
        """
                   Creates a task from the given file_id in the given task template ID.
               :return:
               """
        file_id = self.event_data['file_id']
        if not file_id:
            logger.warning(f'Action has no file_id Stopping execution')
            return

        file = File.get_by_id(session, file_id = file_id)

        # TODO following example from prior, cast data to b64  expected format

        connection_mock : {
            endpoint : private_host
            }

        # TODO get google vertex AI client
        # or   with connection:  "
        client = connection.get_client()

        # TODO run it
        response = something()
        # Save annotations

        # Call ExternalMap
        # Bit of an odd one in mocking global attribute map.
        mock_external_map = {
            "negative" : {89 : {display_name: "neutral", id: 241, name: 242}},
            }

        instance_list = []
        for doc in result:         
            instance_list.append({
                'type': 'global',
                'attribute_groups': mock_external_map[doc.sentiment]
            })

        if do_save_annotations is True:
            # For tracking and flexbility 
            enqueue_packet(
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
            public_name = 'TBD',
            description = 'sss',
            icon = '',
            kind = '',
            category = None,
            #trigger_data = {'trigger_event_name': 'task_completed'},
            #condition_data = {'event_name': 'all_tasks_completed'},
            #completion_condition_data = {'event_name': 'prediction_success'},
        )