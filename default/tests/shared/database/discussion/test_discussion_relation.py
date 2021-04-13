from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.discussion.discussion_comment import DiscussionComment
from shared.database.discussion.discussion_relation import DiscussionRelation
from unittest.mock import patch
import flask


class TeseDiscussionRelation(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TeseDiscussionRelation, self).setUp()
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

    def test_new(self):
        # Create mock issue
        discussion = data_mocking.create_discussion(
            {
                'project_id': self.project.id,
                'name': 'test',
                'title': 'test',
            },
            self.session,
        )
        issue_relation = DiscussionRelation.new(
            session = self.session,
            discussion_id = discussion.id,
        )

        self.assertIsNotNone(issue_relation)
        query = self.session.query(DiscussionRelation).filter(DiscussionRelation.id == issue_relation.id).first()
        self.assertIsNotNone(query)


    def test_serialize(self):
        discussion = data_mocking.create_discussion(
            {
                'project_id': self.project.id,
                'name': 'test',
                'title': 'test',
            },
            self.session,
        )
        issue_relation = data_mocking.create_discussion_relation({
            'discussion_id': discussion.id,
            'user_id': self.project_data['users'][0].id,
            'content': 'test'
        }, self.session)
        issue_relation_data = issue_relation.serialize(self.session)
        self.assertTrue('discussion_id' in issue_relation_data)
        self.assertTrue('created_time' in issue_relation_data)
        self.assertTrue('id' in issue_relation_data)