from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.discussion.discussion_comment import DiscussionComment
from shared.database.discussion.discussion_relation import DiscussionRelation
from unittest.mock import patch
import flask


class TeseDiscussionComment(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TeseDiscussionComment, self).setUp()
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

    def test_get_by_id(self):
        # Create mock issue
        discussion = data_mocking.create_discussion(
            {
                'project_id': self.project.id,
                'name': 'test',
                'title': 'test',
            },
            self.session,
        )
        issue_comment = data_mocking.create_discussion_comment({
            'discussion_id': discussion.id,
            'user_id': self.project_data['users'][0].id,
            'content': 'test'
        }, self.session)

        issue_comment2 = DiscussionComment.get_by_id(self.session, issue_comment.id)
        self.assertEqual(issue_comment, issue_comment2)

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
        content = 'thecontent'
        issue_comment = DiscussionComment.new(
            session = self.session,
            content = content,
            discussion_id = discussion.id
        )
        self.assertIsNotNone(issue_comment)
        self.assertEqual(issue_comment.content, content)
        self.assertEqual(issue_comment.discussion_id, discussion.id)

    def test_list(self):
        # Create mock issue
        discussion = data_mocking.create_discussion(
            {
                'project_id': self.project.id,
                'name': 'test',
                'title': 'test',
            },
            self.session,
        )
        comment1 = data_mocking.create_discussion_comment({
            'discussion_id': discussion.id,
            'project_id': self.project.id,
            'user_id': self.project_data['users'][0].id,
            'content': 'test'
        }, self.session)
        comment2 = data_mocking.create_discussion_comment({
            'discussion_id': discussion.id,
            'project_id': self.project.id,
            'user_id': self.project_data['users'][0].id,
            'content': 'test2'
        }, self.session)
        comments = DiscussionComment.list(
            session = self.session,
            project_id = self.project.id,
            discussion_id = discussion.id
        )
        self.assertIsNotNone(comments)
        self.assertEqual(len(comments), 2)
        ids = [comment.id for comment in comments]
        self.assertTrue(comment1.id in ids)
        self.assertTrue(comment2.id in ids)

    def test_update(self):
        # Create mock issue
        discussion = data_mocking.create_discussion(
            {
                'project_id': self.project.id,
                'name': 'test',
                'title': 'test',
            },
            self.session,
        )
        comment1 = data_mocking.create_discussion_comment({
            'discussion_id': discussion.id,
            'user_id': self.project_data['users'][0].id,
            'content': 'test'
        }, self.session)

        new_content = 'new_content'
        comment = DiscussionComment.update(
            session = self.session,
            comment_id = comment1.id,
            member = None,
            content = new_content
        )
        self.assertIsNotNone(comment)
        self.assertEqual(comment.content, new_content)

    def test_serialize(self):
        discussion = data_mocking.create_discussion(
            {
                'project_id': self.project.id,
                'name': 'test',
                'title': 'test',
            },
            self.session,
        )
        discussion_comment = data_mocking.create_discussion_comment({
            'discussion_id': discussion.id,
            'user_id': self.project_data['users'][0].id,
            'content': 'test'
        }, self.session)
        discussion_comment_data = discussion_comment.serialize()
        self.assertTrue('id' in discussion_comment_data)
        self.assertTrue('user' in discussion_comment_data)
        self.assertTrue('discussion_id' in discussion_comment_data)
        self.assertTrue('content' in discussion_comment_data)
