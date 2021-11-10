from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.utils.task import task_complete
from shared.database.task.task import TASK_STATUSES
from shared.utils.task import task_assign_reviewer
from unittest.mock import patch


class TestTaskAssignReviewer(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestTaskAssignReviewer, self).setUp()
        self.project_data = data_mocking.create_project_with_context(
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
        self.project = self.project_data['project']
        self.auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        self.member = self.auth_api.member
        self.member.user = data_mocking.register_user({
            'username': 'test_user',
            'email': 'test@test.com',
            'password': 'diffgram123',
            'project_string_id': self.project.project_string_id,
            'member_id': self.member.id
        }, self.session)

    def test_task_complete(self):
        # Create mock tasks
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project,
            'allow_reviews': True
        }, self.session)

        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        task_list = []
        user1 = data_mocking.register_user({
            'username': 'test_user1',
            'email': 'test1@test.com',
            'password': 'diffgram123',
            'project_string_id': self.project.project_string_id,
            'member_id': common_actions.create_project_auth(project = self.project, session = self.session).member.id
        }
            , self.session)
        user2 = data_mocking.register_user({
            'username': 'test_user1',
            'email': 'test1@test.com',
            'password': 'diffgram123',
            'project_string_id': self.project.project_string_id,
            'member_id': common_actions.create_project_auth(project = self.project, session = self.session).member.id
        }, self.session)
        user3 = data_mocking.register_user({
            'username': 'test_user1',
            'email': 'test1@test.com',
            'password': 'diffgram123',
            'project_string_id': self.project.project_string_id,
            'member_id': common_actions.create_project_auth(project = self.project, session = self.session).member.id
        }, self.session)

        job.update_reviewer_list(
            session = self.session,
            reviewer_list_ids = [user1.member_id, user2.member_id, user3.member_id],
            log = regular_log.default()
        )
        for i in range(0, 25):
            task = data_mocking.create_task({'name': 'test task', 'file': file, 'job': job}, self.session)
            task_list.append(task)

        task_list[0].add_reviewer(self.session, user1)
        task_list[1].add_reviewer(self.session, user1)
        task_list[2].add_reviewer(self.session, user1)

        task_list[3].add_reviewer(self.session, user2)
        task_list[4].add_reviewer(self.session, user2)
        task_list[5].add_reviewer(self.session, user2)
        task_list[6].add_reviewer(self.session, user2)
        task_list[7].add_reviewer(self.session, user2)

        task_list[8].add_reviewer(self.session, user3)
        task_list[9].add_reviewer(self.session, user3)
        task_list[10].add_reviewer(self.session, user3)
        task_list[11].add_reviewer(self.session, user3)
        task_list[12].add_reviewer(self.session, user3)

        self.session.flush()
        self.session.commit()
        with patch.object(task_list[13], 'add_reviewer') as mock_add_reviewer:
            task_assign_reviewer.auto_assign_reviewer_to_task(
                session = self.session,
                task = task_list[13]
            )
            mock_add_reviewer.assert_called_once_with(
                session = self.session,
                user = user1
            )

        result = task_assign_reviewer.auto_assign_reviewer_to_task(
            session = self.session,
            task = task_list[14]
        )
        self.assertEqual(result.id, user1.id)

        task_list[15].add_reviewer(self.session, user1)
        task_list[16].add_reviewer(self.session, user1)
        task_list[17].add_reviewer(self.session, user2)
        task_list[18].add_reviewer(self.session, user2)

        result = task_assign_reviewer.auto_assign_reviewer_to_task(
            session = self.session,
            task = task_list[19]
        )
        self.assertEqual(result.id, user3.id)
