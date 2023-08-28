from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.annotation import Annotation_Update
from unittest.mock import patch, MagicMock, Mock, call


class TestAnnotationUpdate(testing_setup.DiffgramBaseTestCase):

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestAnnotationUpdate, self).setUp()
  
    # TODO: How can we clean this up / re-use all the setup?

    @patch('shared.annotation.regular_log.default')
    @patch('shared.annotation.Project.get_by_id')
    @patch('shared.annotation.get_member')
    @patch('shared.annotation.Annotation_Update.get_allowed_label_file_ids')
    @patch('shared.annotation.Annotation_Update.init_video_input')
    @patch('shared.annotation.Annotation_Update.task_update')
    @patch('shared.annotation.Annotation_Update.init_file')
    @patch('shared.annotation.Annotation_Update.init_existing_instances')
    @patch('shared.annotation.Annotation_Update.refresh_instance_count')
    def test_post_init_main_functions_called(self, mock_refresh_instance_count, mock_init_existing_instances, mock_init_file, mock_task_update, mock_init_video_input, mock_get_allowed_label_file_ids, mock_get_member, mock_Project_get_by_id, mock_default_log):
        # Arrange
        mock_session = MagicMock()
        mock_project = MagicMock()
        mock_member = MagicMock()
        mock_file = MagicMock()

        # func_calls = Mock()
        # func_calls.m1, func_calls.m2, func_calls.m3, func_calls.m4, func_calls.m5, func_calls.m6 = mock_get_allowed_label_file_ids, mock_init_video_input, mock_task_update, mock_init_file, mock_init_existing_instances, mock_refresh_instance_count

        # Act
        instance = Annotation_Update(session=mock_session, file=mock_file, member=mock_member, project=mock_project)

        # Assert
        self.assertEqual(instance.log, mock_default_log.return_value) # Log was initialized
        mock_Project_get_by_id.assert_not_called() # Project was not fetched
        mock_get_member.assert_not_called() # Member was not fetched

        # TODO: This isnt working, got it from here https://stackoverflow.com/questions/32463321/how-to-assert-method-call-order-with-python-mock
        # func_calls.assert_has_calls([call.m1(), call.m2(), call.m3(), call.m4(), call.m5(), call.m6()])
        mock_get_allowed_label_file_ids.assert_called_once()
        self.assertEqual(instance.previous_next_instance_map, {})
        mock_init_video_input.assert_called_once()
        mock_task_update.assert_called_once()
        mock_init_file.assert_called_once()
        mock_init_existing_instances.assert_called_once()
        mock_refresh_instance_count.assert_called_once()

    @patch('shared.annotation.Annotation_Update.get_allowed_label_file_ids')
    @patch('shared.annotation.Annotation_Update.init_video_input')
    @patch('shared.annotation.Annotation_Update.task_update')
    @patch('shared.annotation.Annotation_Update.init_file')
    @patch('shared.annotation.Annotation_Update.init_existing_instances')
    @patch('shared.annotation.Annotation_Update.refresh_instance_count')
    def test_post_init_project_creating_for_instance_template(self, mock_refresh_instance_count, mock_init_existing_instances, mock_init_file, mock_task_update, mock_init_video_input, mock_get_allowed_label_file_ids):
        # Arrange
        mock_session = MagicMock()
        mock_file = MagicMock()
        creating_for_instance_template = True

        # Act
        Annotation_Update(session=mock_session, file=mock_file, creating_for_instance_template=creating_for_instance_template)

        mock_get_allowed_label_file_ids.assert_not_called()
        mock_init_video_input.assert_not_called()
        mock_task_update.assert_not_called()
        mock_init_file.assert_not_called()
        mock_init_existing_instances.assert_not_called()
        mock_refresh_instance_count.assert_not_called()

    @patch('shared.annotation.Project.get_by_id')
    def test_post_init_project_fetched(self, mock_Project_get_by_id):
        # Arrange
        mock_session = MagicMock()
        mock_file = MagicMock()
        project_id = 123

        # Act
        Annotation_Update(session=mock_session, file=mock_file, project_id=project_id)

        # Assert
        mock_Project_get_by_id.assert_called_once_with(mock_session, project_id)

    @patch('shared.annotation.get_member')
    def test_post_init_member_fetched(self, mock_get_member):
        # Arrange
        mock_session = MagicMock()
        mock_file = MagicMock()
        project_id = 123

        # Act
        Annotation_Update(session=mock_session, file=mock_file, project_id=project_id)

        # Assert
        mock_get_member.assert_called_once_with(session=mock_session)


