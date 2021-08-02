from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.database.system_events.system_events import SystemEvents
from unittest.mock import patch
import analytics
import requests


class TestSystemEvents(testing_setup.DiffgramBaseTestCase):
    """

    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestSystemEvents, self).setUp()
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

    def test_system_startup_events_check(self):
        # Test correct setup of settings.

        with patch.object(SystemEvents, 'new') as mock_1:
            with patch.object(SystemEvents, 'check_version_upgrade') as mock_2:
                with patch.object(SystemEvents, 'check_version_upgrade') as mock_3:
                    result = SystemEvents.system_startup_events_check('test_service')
                    mock_1.asser_called_once()
                    mock_2.asser_called_once()
                    mock_3.asser_called_once()
                    self.assertTrue(result)

    def test_check_version_upgrade(self):
        system_event = SystemEvents.check_version_upgrade(session = self.session, service_name = 'test_service')

        self.assertEqual(system_event.diffgram_version, settings.DIFFGRAM_VERSION_TAG)
        self.assertEqual(system_event.kind, 'version_upgrade')
        self.assertEqual(system_event.service_name, 'test_service')

        system_event = SystemEvents.check_version_upgrade(session = self.session, service_name = 'test_service')

        self.assertIsNone(system_event)

    def test_check_os_change(self):
        system_event = SystemEvents.check_os_change(session = self.session, service_name = 'test_service')

        self.assertEqual(system_event.host_os, settings.DIFFGRAM_HOST_OS)
        self.assertEqual(system_event.kind, 'os_change')
        self.assertEqual(system_event.service_name, 'test_service')
        settings.DIFFGRAM_HOST_OS = 'test_os'
        system_event = SystemEvents.check_os_change(session = self.session, service_name = 'test_service')

        self.assertEqual(system_event.host_os, 'test_os')
        self.assertEqual(system_event.kind, 'os_change')
        self.assertEqual(system_event.service_name, 'test_service')

    def test_serialize(self):
        event_data = {
            'kind': 'test_event',
            'description': 'test_description',
            'install_fingerprint': 'test_install_fingerprint',
            'previous_version': 'test_previous_version',
            'diffgram_version': 'test_diffgram_version',
            'host_os': 'test_host_os',
            'storage_backend': 'test_storage_backend',
            'service_name': 'test_service_name',
            'startup_time': datetime.datetime.utcnow(),
            'shut_down_time': datetime.datetime.utcnow(),
            'created_date': datetime.datetime.utcnow(),
        }
        system_event = data_mocking.new_system_event(
            event_data,
            self.session
        )

        for key in event_data.keys():
            self.assertEqual(getattr(system_event, key), event_data.get(key))

    def test_send_to_segment(self):
        event_data = {
            'kind': 'test_event',
            'description': 'test_description',
            'install_fingerprint': 'test_install_fingerprint',
            'previous_version': 'test_previous_version',
            'diffgram_version': 'test_diffgram_version',
            'host_os': 'test_host_os',
            'storage_backend': 'test_storage_backend',
            'service_name': 'test_service_name',
            'startup_time': datetime.datetime.utcnow(),
            'shut_down_time': datetime.datetime.utcnow(),
            'created_date': datetime.datetime.utcnow(),
        }
        system_event = data_mocking.new_system_event(
            event_data,
            self.session
        )
        with patch.object(analytics, 'track') as mock_1:
            result = system_event.send_to_segment()
            self.assertIsNone(result)

    def test_send_to_eventhub(self):
        event_data = {
            'kind': 'test_event',
            'description': 'test_description',
            'install_fingerprint': 'test_install_fingerprint',
            'previous_version': 'test_previous_version',
            'diffgram_version': 'test_diffgram_version',
            'host_os': 'test_host_os',
            'storage_backend': 'test_storage_backend',
            'service_name': 'test_service_name',
            'startup_time': datetime.datetime.utcnow(),
            'shut_down_time': datetime.datetime.utcnow(),
            'created_date': datetime.datetime.utcnow(),
        }
        system_event = data_mocking.new_system_event(
            event_data,
            self.session
        )
        with patch.object(requests, 'post') as mock_1:
            result = system_event.send_to_eventhub()
            self.assertIsNone(result)
            mock_1.asser_called_once()
