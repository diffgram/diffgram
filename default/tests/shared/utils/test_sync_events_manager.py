from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from methods.task.task.task_list import task_list_core
from unittest.mock import patch
from shared.utils.sync_events_manager import SyncEventManager
import flask


class TestSyncEventsManager(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestSyncEventsManager, self).setUp()
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

    def test_sync_events_manager(self):
        # Create mock tasks
        num_tasks = 5
        job = data_mocking.create_job({
            'name': f"my-test-job-{1}",
            'project': self.project
        }, self.session)
        manager = SyncEventManager.create_sync_event_and_manager(
            session=self.session,
            dataset_source=None,
            dataset_source_id=None,
            dataset_destination=None,
            dataset_destination_id=None,
            description='my test',
            file=None,
            job=job,
            input=None,
            input_id=None,
            project=None,
            status=None,
            created_task=None,
            completed_task=None,
            new_file_copy=None,
            transfer_action=None,
            event_effect_type=None,
            event_trigger_type=None,
            processing_deferred=None,
            member_created=None,
            member_updated=None
        )
        self.assertEqual(manager.sync_event.description, 'my test')
        self.assertEqual(manager.sync_event.job, job)
        manager.set_description('new desc')
        self.assertEqual(manager.sync_event.description, 'new desc')
        manager.set_status('mystatus')
        self.assertEqual(manager.sync_event.status, 'mystatus')
        manager.set_event_effect_type('123')
        self.assertEqual(manager.sync_event.event_effect_type, '123')

