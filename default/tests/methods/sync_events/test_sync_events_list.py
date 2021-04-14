from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from methods.sync_events.sync_events_list import sync_events_list_core
from unittest.mock import patch
import flask


class TestSyncEventsList(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestSyncEventsList, self).setUp()
        project_data = data_mocking.create_project_with_context(
            {
                'users': [
                    {'username': 'Test',
                     'email': 'test@test.com',
                     'password': 'diffgram123',
                     }
                ]
            },
            self.session
        )
        self.project = project_data['project']

    def test_sync_events_list_api(self):
        # Create mock tasks
        num_events = 5
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project
        }, self.session)
        all_sync_events = []
        for i in range(0, num_events):
            sync_event = data_mocking.create_sync_event({
                'description': 'syncevent{}'.format(i),
                'job_id': job.id,
                'project': self.project
            }, self.session)
            all_sync_events.append(sync_event)

        request_payload = {
            'metadata':{
                'job_id': job.id,
                'mode_data': 'list',
                'project_string_id': self.project.project_string_id
            }
        }

        endpoint = "/api/v1/sync-events/list"

        with self.client.session_transaction() as session:
            auth_api = common_actions.create_project_auth(project=self.project, session=self.session)
            credentials = b64encode("{}:{}".format(auth_api.client_id, auth_api.client_secret).encode()).decode(
                'utf-8')
            session['Authorization'] = credentials
            common_actions.add_auth_to_session(session, self.project.users[0])
        response = self.client.post(
            endpoint,
            data=json.dumps(request_payload),
            headers={
                'directory_id': str(job.project.directory_default_id),
                'Authorization': 'Basic {}'.format(credentials)
            }
        )
        print(response.data)
        self.assertEqual(response.status_code, 200)
        new_session = sessionMaker.session_factory()
        self.assertEqual(len(response.json['sync_events_list']), num_events)

    def test_sync_events_list_core(self):
        # Create mock tasks
        num_tasks = 5
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(2),
            'project': self.project
        }, self.session)
        all_tasks = []
        for i in range(0, num_tasks):
            sync_event = data_mocking.create_sync_event({
                'description': 'syncevent{}'.format(i),
                'job_id': job.id,
                'project': self.project
            }, self.session)
            all_tasks.append(sync_event)
        self.session.commit()
        with self.app.test_request_context():
            common_actions.add_auth_to_session(flask.session, self.project.users[0])
            result = sync_events_list_core(self.session,
                                           date_from=None,
                                           date_to=None,
                                           status=None,
                                           job_id=job.id,
                                           dataset_source_id=None,
                                           dataset_destination_id=None,
                                           created_task_id=None,
                                           completed_task_id=None,
                                           event_effect_type=None,
                                           event_trigger_type=None,
                                           incoming_directory_id=None,
                                           project_string_id=self.project.project_string_id,
                                           limit=30,
                                           output_mode='serialize')
        logger.info(result)
        self.assertEqual(len(result), num_tasks)
