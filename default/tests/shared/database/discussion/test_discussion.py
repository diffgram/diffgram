from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.discussion.discussion import Discussion
from shared.database.discussion.discussion_relation import DiscussionRelation
from unittest.mock import patch
import flask


class TestDiscussion(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestDiscussion, self).setUp()
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
        self.auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        self.member = self.auth_api.member


    def test_attach_element(self):
        # Create mock issue
        issue = data_mocking.create_discussion(
            {
                'project_id': self.project.id,
                'name': 'test',
                'title': 'test',
            },
            self.session,
        )
        job = data_mocking.create_job({
            'name': 'my-test-job'
        }, self.session)

        file = data_mocking.create_file({'project_id': job.project.id, 'job_id': job.id}, self.session)
        issue_relation_file = issue.attach_element(
            session = self.session,
            element = {'type': 'file', 'id': file.id}
        )
        issue_relation_job = issue.attach_element(
            session = self.session,
            element = {'type': 'job', 'id': job.id}
        )
        self.session.commit()
        query_rel_file = self.session.query(DiscussionRelation).first()
        query_rel_job = self.session.query(DiscussionRelation).first()
        self.assertIsNotNone(issue_relation_file)
        self.assertIsNotNone(issue_relation_job)
        self.assertIsNotNone(query_rel_file)
        self.assertIsNotNone(query_rel_job)

    def test_new(self):
        issue = Discussion.new(
            session = self.session,
            title = 'test',
            description = 'description',
            project_id = self.project.id,
            status = 'open'
        )

        self.assertEqual(issue.title, 'test')
        self.assertEqual(issue.description, 'description')
        self.assertEqual(issue.project_id, self.project.id)
        self.assertEqual(issue.status, 'open')

    def test_get_by_id(self):
        issue = Discussion.new(
            session = self.session,
            title = 'test',
            description = 'description',
            project_id = self.project.id,
            status = 'open'
        )
        issue2 = Discussion.get_by_id(self.session, issue.id)
        self.assertEqual(issue, issue2)

    def test_serialize_attached_elements(self):
        issue = Discussion.new(
            session = self.session,
            title = 'test',
            description = 'description',
            project_id = self.project.id,
            status = 'open'
        )
        job = data_mocking.create_job({
            'name': 'my-test-job'
        }, self.session)
        file = data_mocking.create_file({'project_id': job.project.id, 'job_id': job.id}, self.session)
        rel1 = issue.attach_element(
            session = self.session,
            element = {'type': 'file', 'id': file.id}
        )
        rel2 = issue.attach_element(
            session = self.session,
            element = {'type': 'job', 'id': job.id}
        )
        elements = issue.serialize_attached_elements(self.session)
        element_ids = [x['id'] for x in elements]
        self.assertEqual(len(elements), 3)
        self.assertTrue('type' in elements[0])
        self.assertTrue('discussion_id' in elements[0])
        self.assertTrue('id' in elements[0])
        self.assertTrue('created_time' in elements[0])
        self.assertTrue(rel1.id in element_ids)
        self.assertTrue(rel2.id in element_ids)

    def test_serialize(self):
        issue = Discussion.new(
            session = self.session,
            title = 'test',
            description = 'description',
            project_id = self.project.id,
            status = 'open'
        )
        job = data_mocking.create_job({
            'name': 'my-test-job'
        }, self.session)
        file = data_mocking.create_file({'project_id': job.project.id, 'job_id': job.id}, self.session)
        rel1 = issue.attach_element(
            session = self.session,
            element = {'type': 'file', 'id': file.id}
        )
        rel2 = issue.attach_element(
            session = self.session,
            element = {'type': 'job', 'id': job.id}
        )
        issue_data = issue.serialize(self.session)
        self.assertEqual(len(issue_data['attached_elements']), 3)
        self.assertTrue('id' in issue_data)
        self.assertTrue('created_time' in issue_data)
        self.assertTrue('description' in issue_data)
        self.assertTrue('title' in issue_data)
        self.assertTrue('project_id' in issue_data)
        self.assertTrue('status' in issue_data)

    def test_serialize_for_list(self):
        issue = Discussion.new(
            session = self.session,
            title = 'test',
            description = 'description',
            project_id = self.project.id,
            status = 'open'
        )
        job = data_mocking.create_job({
            'name': 'my-test-job'
        }, self.session)
        issue_data = issue.serialize(self.session)
        self.assertTrue('id' in issue_data)
        self.assertTrue('created_time' in issue_data)
        self.assertTrue('description' in issue_data)
        self.assertTrue('title' in issue_data)
        self.assertTrue('project_id' in issue_data)
        self.assertTrue('status' in issue_data)

    def test_update_attached_instances(self):
        # Create mock discussion
        discussion = data_mocking.create_discussion({
            'title': 'test',
            'description': 'test',
            'member_created_id': self.member.id,
            'project_id': self.project.id
        }, self.session)
        member = self.member
        instance = data_mocking.create_instance({
            'project_id': self.project.id,
            'type': 'box',
            'x_min': 0,
            'x_max': 0,
            'y_min': 0,
            'y_max': 0,
        }, self.session)
        discussion.update_attached_instances(
            session = self.session,
            attached_elements = [{'type': 'instance', 'instance_id': instance.id}]
        )
        self.session.commit()
        disc = Discussion.get_by_id(session = self.session, id=discussion.id)
        self.assertEqual(len(disc.serialize_attached_elements(self.session)), 2)

    def test_detach_all_instances(self):
        # Create mock discussion
        discussion = data_mocking.create_discussion({
            'title': 'test',
            'description': 'test',
            'member_created_id': self.member.id,
            'project_id': self.project.id
        }, self.session)
        member = self.member

        instance = data_mocking.create_instance({
            'project_id': self.project.id,
            'type': 'box',
            'x_min': 0,
            'x_max': 0,
            'y_min': 0,
            'y_max': 0,
        }, self.session)
        discussion.attach_element(session = self.session, element = {
            'type': 'instance',
            'id': instance.id
        })
        self.session.commit()
        discussion_updated = Discussion.update(
            session = self.session,
            discussion_id = discussion.id,
            attached_elements = []
        )
        attached = discussion_updated.serialize_attached_elements(self.session)
        self.assertEqual(len(attached), 1)


    def test_list(self):
        issue = Discussion.new(
            session = self.session,
            title = 'test',
            description = 'description',
            project_id = self.project.id,
            status = 'open'
        )
        issue2 = Discussion.new(
            session = self.session,
            title = 'test',
            description = 'description',
            project_id = self.project.id,
            status = 'open'
        )
        issues = Discussion.list(
            session = self.session,
            project_id = self.project.id,
        )

        self.assertEqual(type(issues), list)
        self.assertEqual(len(issues), 2)