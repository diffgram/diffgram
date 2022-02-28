from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from methods.task.task_template.job_list import job_view_core, default_metadata, filter_by_project
from unittest.mock import patch
from methods.task.task_template import job_new_or_update
from shared.utils.logging import DiffgramLogger
import flask


class TestJobList(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestJobList, self).setUp()
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

    def test_job_list_api(self):
        # Create mock job.
        num_jobs = 5
        all_jobs = []
        for i in range(0, num_jobs):
            job = data_mocking.create_job({
                'name': f"my-test-job-{i}",
                'project': self.project
            }, self.session)
            all_jobs.append(job)

        request_data = {
            'metadata': {
                'builder_or_trainer': {
                    'mode': 'builder'
                },
                'limit': 5,
                'project_string_id': self.project.project_string_id
            }
        }

        endpoint = "/api/v1/job/list"

        with self.client.session_transaction() as session:
            auth_api = common_actions.create_project_auth(project=self.project, session=self.session)
            credentials = b64encode(f"{auth_api.client_id}:{auth_api.client_secret}".encode()).decode(
                'utf-8')
            session['Authorization'] = credentials
            common_actions.add_auth_to_session(session, self.project.users[0])
        response = self.client.post(
            endpoint,
            data=json.dumps(request_data),
            headers={
                'directory_id': str(job.project.directory_default_id),
                'Authorization': f"Basic {credentials}"
            }
        )
        self.assertEqual(response.status_code, 200)
        new_session = sessionMaker.session_factory()
        self.assertEqual(len(response.json['Job_list']), num_jobs)

    def test_job_view_core(self):
        num_jobs = 3
        metadata_proposed = {
            'builder_or_trainer': {
                'mode': 'builder'
            },
            'limit': num_jobs,
            'my_jobs_only': False,
            'project_string_id': self.project.project_string_id

        }
        all_jobs = []
        for i in range(0, num_jobs):
            job = data_mocking.create_job({
                'name': f"my-test-job-{i}",
                'project': self.project
            }, self.session)
            all_jobs.append(job)
        self.session.commit()
        with self.app.test_request_context():
            common_actions.add_auth_to_session(flask.session, self.project.users[0])
            result = job_view_core(self.session,
                                   metadata_proposed,
                                   output_mode="serialize",
                                   user=self.project.users[0])
        logger.info(result)
        self.assertEqual(len(result), num_jobs - 1)

    def test_default_metadata(self):
        mock = {
            'my_jobs_only': True,
            'job_ids': [1, 2, 3],
            'builder_or_trainer': 'builder',
            'field': 'testfield',
            'category': 'mycategory',
            'type': 'typex',
            'instance_type': 'polygon',
            'status': 'completed',
            'data_mode': 'dataa',
            'project_string_id': '1235'
        }
        result = default_metadata(mock)
        self.assertEqual(result['my_jobs_only'], mock['my_jobs_only'])
        self.assertEqual(result['job_ids'], mock['job_ids'])
        self.assertEqual(result['builder_or_trainer'], mock['builder_or_trainer'])
        self.assertEqual(result['field'], mock['field'])
        self.assertEqual(result['category'], mock['category'])
        self.assertEqual(result['type'], mock['type'])
        self.assertEqual(result['instance_type'], mock['instance_type'])
        self.assertEqual(result['status'], mock['status'])
        self.assertEqual(result['data_mode'], mock['data_mode'])
        self.assertEqual(result['project_string_id'], mock['project_string_id'])

    def test_filter_by_project(self):
        other_project_data = data_mocking.create_project_with_context(
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
        other_project = other_project_data['project']
        other_job = data_mocking.create_job({
            'name': f'my-testother-job-{1}',
            'project': other_project
        }, self.session)
        query = self.session.query(Job)
        with self.app.test_request_context():
            common_actions.add_auth_to_session(flask.session, self.project.users[0])
            result = filter_by_project(session=self.session, project_string_id=self.project.project_string_id, query=query)

        jobs = result.all()
        job_ids = [x.id for x in jobs]
        self.assertTrue(other_job.id not in job_ids)