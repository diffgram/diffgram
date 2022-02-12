from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.database.task.job.user_to_job import User_To_Job


class TestUserToJob(testing_setup.DiffgramBaseTestCase):
    """

    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestUserToJob, self).setUp()
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
        self.project_data = project_data
        self.auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        self.member = self.auth_api.member
        self.member.user = data_mocking.register_user({
            'username': 'test_user',
            'email': 'test@test.com',
            'password': 'diffgram123',
            'project_string_id': 'myproject',
            'member_id': self.member.id
        }, self.session)

    def test_serialize_trainer_info_default(self):
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project
        }, self.session)
        user_to_job = data_mocking.create_user_to_job({
            'user_id': self.member.user_id,
            'job_id': job.id,
            'relation': 'annotator',
            'status': 'active'
        }, self.session)

        result = user_to_job.serialize_trainer_info_default()

        self.assertEqual(result['status'], 'active')
        self.assertEqual(result['relation'], 'annotator')

    def test_serialize(self):
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project
        }, self.session)
        user_to_job = data_mocking.create_user_to_job({
            'user_id': self.member.user_id,
            'job_id': job.id,
            'relation': 'annotator',
            'status': 'active'
        }, self.session)

        result = user_to_job.serialize()

        self.assertEqual(result, user_to_job.user_id)

    def test_get_job_ids_from_user(self):
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project
        }, self.session)
        user_to_job = data_mocking.create_user_to_job({
            'user_id': self.member.user_id,
            'job_id': job.id,
            'relation': 'annotator',
            'status': 'active'
        }, self.session)

        result = User_To_Job.get_job_ids_from_user(self.session, self.member.user_id)

        self.assertEqual(result, [job.id])

    def test_get_all_by_user_id(self):
        self.auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        self.member = self.auth_api.member
        self.member.user = data_mocking.register_user({
            'username': 'test_user2',
            'email': 'test2@test.com',
            'password': 'diffgram1223',
            'project_string_id': 'myproject',
            'member_id': self.member.id
        }, self.session)
        job = data_mocking.create_job({
            'name': 'my-test22-job-{}'.format(1),
            'project': self.project
        }, self.session)
        job2 = data_mocking.create_job({
            'name': 'my2-tes22t-job-{}'.format(1),
            'project': self.project
        }, self.session)
        user_to_job = data_mocking.create_user_to_job({
            'user_id': self.member.user_id,
            'job_id': job.id,
            'relation': 'annotator',
            'status': 'active'
        }, self.session)
        user_to_job2 = data_mocking.create_user_to_job({
            'user_id': self.member.user_id,
            'job_id': job2.id,
            'relation': 'annotator',
            'status': 'active'
        }, self.session)

        res_list = [user_to_job, user_to_job2]
        result = User_To_Job.get_all_by_user_id(self.session, self.member.user_id, True)

        for elm in res_list:

            self.assertTrue(elm in result)

    def test_get_single_by_ids(self):
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project
        }, self.session)
        user_to_job = data_mocking.create_user_to_job({
            'user_id': self.member.user_id,
            'job_id': job.id,
            'relation': 'annotator',
            'status': 'active'
        }, self.session)

        result = User_To_Job.get_single_by_ids(self.session, self.member.user_id, job.id)

        self.assertEqual(user_to_job, result)

    def test_get_by_job_id(self):
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project
        }, self.session)
        user_to_job = data_mocking.create_user_to_job({
            'user_id': self.member.user_id,
            'job_id': job.id,
            'relation': 'annotator',
            'status': 'active'
        }, self.session)

        result = User_To_Job.get_by_job_id(self.session,  job.id)

        self.assertTrue(user_to_job in result)


    def test_list(self):
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project
        }, self.session)
        user_to_job = data_mocking.create_user_to_job({
            'user_id': self.member.user_id,
            'job_id': job.id,
            'relation': 'annotator',
            'status': 'active'
        }, self.session)

        result = User_To_Job.list(
            session = self.session,
            user_id_ignore_list = [],
            job = job,
            serialize = False,
            user = self.member.user
        )

        self.assertTrue(user_to_job in result)
