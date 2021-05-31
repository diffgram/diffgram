from methods.connectors.scale_ai_connector import ScaleAIConnector
from scaleapi.tasks import Task as ScaleAITask
from walrus.tests.test_utils import testing_setup
from shared.tests.test_utils import data_mocking
from unittest.mock import patch

class TestScaleAIConnection(testing_setup.DiffgramBaseTestCase):
    """
        Test cases for the S3Connector methods. This test case test if images are uploaded sucessfully to diffgram
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        # configure_mappers()
        super(TestScaleAIConnection, self).setUp()
        self.project_string_id = 'my-scaleai-test-project'
        project_data = data_mocking.create_project_with_context(
            {
                'project_string_id': self.project_string_id,
                'project_name': self.project_string_id,
                'users': [
                    {'username': 'Test',
                     'email': 'test@test.com',
                     'password': 'diffgram123',
                     'project_string_id': self.project_string_id
                     }
                ]
            },
            self.session
        )
        scale_auth_data = {'client_secret': ''}
        self.scaleaiconn = ScaleAIConnector(scale_auth_data, {})
        self.scaleaiconn.connect()

    def test_send_task_to_scale_ai(self):
        task_file_type = None
        task = data_mocking.create_task({'name': 'test task'}, self.session)
        attachment = None
        # Unsupported file types: label
        task_file_type = 'image'
        meta_data = {
            'label_file_list': [],
            'diffgram_task_id': task.id,
            'source_id': -1  # TODO: add source when ready.
        }

        objects_to_annotate = []
        if 'label_file_list_serialized' in task.label_dict:
            for elm in task.label_dict['label_file_list_serialized']:
                if elm['type'] == 'label':
                    objects_to_annotate.append(elm['label']['name'])

        with patch.object(self.scaleaiconn,
                          'put_data',
                          return_value={'result': ScaleAITask(param_dict={'task_id': None}, client=self.scaleaiconn.connection_client)}):
            result = self.scaleaiconn.put_data({
                'action_type': 'bounding_box',
                'project': 'test',
                'instruction': 'Please Draw a box on the image.',
                'callback_url': 'http://diffgram.com/scaleai/task-completed',
                'attachment_type': task_file_type,
                'attachment': 'https://thumbor.forbes.com/thumbor/250x382/https://blogs-images.forbes.com/dorothypomerantz/files/2011/09/Spongebob-squarepants.jpg?width=960',
                'objects_to_annotate': objects_to_annotate,
                'with_labels': True,
                'metadata': meta_data,
            })
        self.assertEqual(type(result['result']).__name__, ScaleAITask.__name__)
        self.session.close()
