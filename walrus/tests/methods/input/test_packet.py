from walrus.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from methods.input import packet
from unittest.mock import patch
from shared.regular import regular_log


class TestPacket(testing_setup.DiffgramBaseTestCase):

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestPacket, self).setUp()
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

    def test_validate_file_data_for_input_packet(self):
        log = regular_log.default()
        file1 = data_mocking.create_file({'project_id': self.project.id}, self.session)
        # Case of file ID
        input_data = {
            'file_id': file1.id
        }
        result, log, file_id = packet.validate_file_data_for_input_packet(
            session = self.session,
            project_string_id = self.project.project_string_id,
            input = input_data,
            log = log
        )
        self.assertTrue(result)
        self.assertEqual(len(log['error'].keys()), 0)
        self.assertEqual(file_id, file1.id)

        # Case of Media URL
        input_data = {
            'media': {
                'url': 'test_url'
            }
        }
        result, log, file_id = packet.validate_file_data_for_input_packet(
            session = self.session,
            project_string_id = self.project.project_string_id,
            input = input_data,
            log = log
        )
        self.assertFalse(result)
        self.assertEqual(len(log['error'].keys()), 1)
        self.assertEqual(file_id, None)

        input_data['media']['type'] = 'image'
        log = regular_log.default()
        result, log, file_id = packet.validate_file_data_for_input_packet(
            session = self.session,
            project_string_id = self.project.project_string_id,
            input = input_data,
            log = log
        )

        self.assertTrue(result)
        self.assertEqual(len(log['error'].keys()), 0)
        self.assertEqual(file_id, None)

        # Case of Filename + Directory

        file2 = data_mocking.create_file({'project_id': self.project.id, 'original_filename': 'test1.jpg'}, self.session)
        directory = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': [file2]
        }, self.session)
        input_data = {
            'file_name': 'test1.jpg',
            'directory_id': directory.id

        }
        log = regular_log.default()
        result, log, file_id = packet.validate_file_data_for_input_packet(
            session = self.session,
            project_string_id = self.project.project_string_id,
            input = input_data,
            log = log
        )

        self.assertTrue(result)
        self.assertEqual(len(log['error'].keys()), 0)
        self.assertEqual(file_id, file2.id)

        input_data = {
            'file_name': 'test1111.jpg',
            'directory_id': directory.id

        }
        log = regular_log.default()
        result, log, file_id = packet.validate_file_data_for_input_packet(
            session = self.session,
            project_string_id = self.project.project_string_id,
            input = input_data,
            log = log
        )
        print('log', log)
        self.assertFalse(result)
        self.assertEqual(len(log['error'].keys()), 1)
        self.assertEqual(file_id, None)
