from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.annotation import Annotation_Update
from unittest.mock import patch, MagicMock, Mock, call


class TestAnnotationUpdate(testing_setup.DiffgramBaseTestCase):

    def setUp(self):
        super(TestAnnotationUpdate, self).setUp()
        self.mock_session = MagicMock()
        self.mock_project = MagicMock()
        self.mock_member = MagicMock()
        self.mock_file = MagicMock()
        self.instance = Annotation_Update(session=self.mock_session, file=self.mock_file, member=self.mock_member, project=self.mock_project)
  
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
        # func_calls = Mock()
        # func_calls.m1, func_calls.m2, func_calls.m3, func_calls.m4, func_calls.m5, func_calls.m6 = mock_get_allowed_label_file_ids, mock_init_video_input, mock_task_update, mock_init_file, mock_init_existing_instances, mock_refresh_instance_count

        # Act
        instance = Annotation_Update(session=self.mock_session, file=self.mock_file, member=self.mock_member, project=self.mock_project)

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
        creating_for_instance_template = True

        # Act
        Annotation_Update(session=self.mock_session, file=self.mock_file, creating_for_instance_template=creating_for_instance_template)

        mock_get_allowed_label_file_ids.assert_not_called()
        mock_init_video_input.assert_not_called()
        mock_task_update.assert_not_called()
        mock_init_file.assert_not_called()
        mock_init_existing_instances.assert_not_called()
        mock_refresh_instance_count.assert_not_called()

    @patch('shared.annotation.Project.get_by_id')
    def test_post_init_project_fetched(self, mock_Project_get_by_id):
        # Arrange
        project_id = 123

        # Act
        Annotation_Update(session=self.mock_session, file=self.mock_file, project_id=project_id)

        # Assert
        mock_Project_get_by_id.assert_called_once_with(self.mock_session, project_id)

    @patch('shared.annotation.get_member')
    def test_post_init_member_fetched(self, mock_get_member):
        # Arrange
        project_id = 123

        # Act
        Annotation_Update(session=self.mock_session, file=self.mock_file, project_id=project_id)

        # Assert
        mock_get_member.assert_called_once_with(session=self.mock_session)

    @patch('shared.annotation.Annotation_Update.update_instance_list')
    @patch('shared.annotation.logger')
    def test_instance_template_main_empty_instance_list_new(self, mock_logger, mock_update_instance_list):
        # Arrange
        self.instance.instance_list_new = []

        # Act
        result = self.instance.instance_template_main()

        # Assert
        self.assertIsNone(result)
        mock_logger.error.assert_called_once_with('Error, please provide instance_list_new {\'error\': {}, \'info\': {}, \'success\': False}')
        mock_update_instance_list.assert_not_called()
    
    @patch('shared.annotation.Annotation_Update.update_instance_list')
    def test_instance_template_main_success(self, mock_update_instance_list):
        # Arrange
        self.instance.instance_list_new = [{'instance_id': 1}, {'instance_id': 2}]
        self.instance.per_instance_spec_list = [{'label_file_id': {'required': True}}, {'some_other_key': 'value'}]
        mock_new_added_instances = Mock()
        self.instance.new_added_instances = mock_new_added_instances

        # Act
        result = self.instance.instance_template_main()

        # Assert
        self.assertEqual(result, mock_new_added_instances)
        mock_update_instance_list.assert_called_with(hash_instances=False, validate_label_file=False, overwrite_existing_instances=True)
        self.assertEqual(self.instance.per_instance_spec_list, [{'label_file_id': {'required': False}}, {'some_other_key': 'value'}])
        
    @patch('shared.annotation.logger')
    @patch('shared.annotation.Annotation_Update.update_instance_list')
    @patch('shared.annotation.Annotation_Update.return_orginal_file_type')
    def test_instance_template_main_error_detected(self, mock_return_orginal_file_type, mock_update_instance_list, mock_logger):
        # Arrange
        mock_error_log = { "error": { "some_error": "error_message" }, "info": {}, "success": False }
        mock_instance_list = [{'instance_id': 1}, {'instance_id': 2}]
        self.instance.instance_list_new = mock_instance_list
        self.instance.log["error"] = mock_error_log["error"]

        # Act
        result = self.instance.instance_template_main()

        # Assert
        self.assertEqual(result, mock_return_orginal_file_type.return_value)
        mock_update_instance_list.assert_called_with(hash_instances=False, validate_label_file=False, overwrite_existing_instances=True)
        expected_logger_calls = [
            call(f"Error updating annotation {str(mock_error_log)}"),
            call(f"Instance list is: {mock_instance_list}")
        ]
        mock_logger.error.assert_has_calls(expected_logger_calls)
        

    def test___perform_external_map_action(self):
        # Arrange
        self.instance.external_map = Mock()
        self.instance.external_map_action = 'set_instance_id'
        self.instance.instance = Mock()

        # Act
        self.instance._Annotation_Update__perform_external_map_action()

        # Assert
        self.assertEqual(self.instance.external_map.instance, self.instance.instance)
        self.instance.session.add.assert_called_once_with(self.instance.external_map)

    def test___perform_external_map_action_wrong_action(self):
        # Arrange
        self.instance.external_map = Mock()
        self.instance.external_map_action = 'something_else'
        self.instance.instance = Mock()

        # Act
        self.instance._Annotation_Update__perform_external_map_action()

        # Assert
        self.assertNotEqual(self.instance.external_map.instance, self.instance.instance)
        self.instance.session.add.assert_not_called()

    def test___perform_external_map_action_no_external_map(self):
        # Arrange
        self.instance.external_map = None
        self.instance.external_map_action = 'set_instance_id'
        self.instance.instance = Mock()

        # Act
        self.instance._Annotation_Update__perform_external_map_action()

        # Assert
        self.instance.session.add.assert_not_called()
