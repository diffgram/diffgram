from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.auth.member import Member
from methods.discussions import discussion_comment_new
from unittest.mock import patch
import flask


class TeseIssueNew(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TeseIssueNew, self).setUp()
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

    def test_view_file_list_web_route(self):
        # Create mock tasks
        job = data_mocking.create_job({
            'name': 'my-test-job',
            'project': self.project
        }, self.session)

        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        file2 = data_mocking.create_file({'project_id': self.project.id}, self.session)
        file3 = data_mocking.create_file({'project_id': self.project.id}, self.session)
        file.created_time = datetime.datetime(2020, 5, 11)
        file2.created_time = datetime.datetime(2020, 5, 17)
        file3.created_time = datetime.datetime(2020, 5, 25)
        self.session.commit()
        directory = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': [file, file2, file3]
        }, self.session)

        request_data = {
            'metadata': {
                'directory_id': directory.id,
                'date_from': datetime.datetime(2020, 5, 11).strftime('%Y-%m-%d'),
                'date_to': datetime.datetime(2020, 5, 18).strftime('%Y-%m-%d'),
                'annotations_are_machine_made_setting': "All",
                'annotation_status': "All",
                'limit': 25,
                'media_type': 'All',
                'request_next_page': False,
                'file_view_mode': 'annotation',
                'request_previous_page': False,
                'previous': {'annotation_status': "All",
                             'date_from': None,
                             'date_to': None,
                             'directory_id': None,
                             'file': {},
                             'file_view_mode': None,
                             'job_id': None,
                             'label': {'start_index': 0},
                             'limit': 25,
                             'machine_made_setting': "All",
                             'media_type': "All",
                             'pagination': {},
                             'search_term': None,
                             'start_index': 0,
                             'request_next_page': False,
                             'request_previous_page': False,
                             },
                'options': {'itemsPerPage': -1, 'sortDesc': [True]},
                'job_id': None,
            }
        }

        endpoint = "/api/project/{}/user/{}/file/list".format(self.project.project_string_id,
                                                              self.project_data['users'][0].id)
        credentials = b64encode("{}:{}".format(self.auth_api.client_id, self.auth_api.client_secret).encode()).decode(

            'utf-8')

        response = self.client.post(
            endpoint,
            data = json.dumps(request_data),
            headers = {

                'Authorization': 'Basic {}'.format(credentials)
            }

        )

        data = response.json
        ids = [x['id'] for x in data['file_list']]
        # Testing Date filter case.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(ids), 2)
        self.assertTrue(file.id in ids)
        self.assertTrue(file2.id in ids)
