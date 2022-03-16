from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from unittest.mock import patch
from methods.task.task_template.job_resync import job_resync_core, threaded_job_resync
from shared.utils import job_dir_sync_utils


class TestJobResync(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestJobResync, self).setUp()
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
        self.project_data = project_data
        self.project = project_data['project']

    def test_job_resync_api(self):
        # Create mock job.
        job = data_mocking.create_job({
            'name': 'my-test-job',
            'project': self.project
        }, self.session)
        request_data = {
            'task_template_id': job.id,
        }
        endpoint = f"/api/v1/project/{job.project.project_string_id}/job/resync"
        auth_api = common_actions.create_project_auth(project = job.project, session = self.session)
        credentials = b64encode(f"{auth_api.client_id}:{auth_api.client_secret}".encode()).decode('utf-8')
        response = self.client.post(
            endpoint,
            data = json.dumps(request_data),
            headers = {
                'directory_id': str(self.project.directory_default_id),
                'Authorization': f"Basic {credentials}"
            }
        )
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['resync_result'], True)

    def test_job_resync_core(self):
        job = data_mocking.create_job({
            'name': 'my-test-job',
            'project': self.project
        }, self.session)
        auth_api = common_actions.create_project_auth(project = job.project, session = self.session)
        resync_result, log = job_resync_core(session = self.session,
                                             project = self.project,
                                             member = auth_api.member,
                                             task_template_id = job.id,
                                             log = regular_log.default())

        self.assertTrue(resync_result)
        self.assertEqual(len(log['error'].keys()), 0)

    def test_threaded_job_resync(self):
        job = data_mocking.create_job({
            'name': 'my-test-job',
            'status': 'active',
            'project': self.project
        }, self.session)
        auth_api = common_actions.create_project_auth(project = job.project, session = self.session)
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        file_missing1 = data_mocking.create_file({'project_id': self.project.id}, self.session)
        file_missing2 = data_mocking.create_file({'project_id': self.project.id}, self.session)
        directory = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': [file, file_missing1, file_missing2]
        }, self.session)
        job.update_attached_directories(self.session,
                                        [{'directory_id': directory.id, 'selected': 'sync'}]
                                        )

        log = regular_log.default()
        sync_manager = job_dir_sync_utils.JobDirectorySyncManager(
            session = self.session,
            log = log,
            job = job
        )
        sync_manager._JobDirectorySyncManager__add_file_into_job(
            file,
            directory,
            create_tasks = True
        )
        self.session.commit()


        result = threaded_job_resync(
            task_template_id = job.id,
            member_id = auth_api.member_id
        )

        self.assertEqual(len(result), 2)
