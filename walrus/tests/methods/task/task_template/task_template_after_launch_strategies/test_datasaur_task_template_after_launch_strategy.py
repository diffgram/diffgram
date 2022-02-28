from walrus.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from walrus.methods.task.task_template.task_template_after_launch_strategies.datasaur_task_template_after_launch_strategy import \
    DatasaurTaskTemplateAfterLaunchStrategy
from shared.database.task.task import Task
from shared.regular import regular_log
from shared.database.external.external import ExternalMap
from shared.regular.regular_methods import commit_with_rollback
from unittest.mock import patch


class TestScaleAITaskTemplateAfterLaunchStrategy(testing_setup.DiffgramBaseTestCase):
    """

        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestScaleAITaskTemplateAfterLaunchStrategy, self).setUp()
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

    def test_execute_after_launch_strategy(self):
        file = data_mocking.create_file({'project_id': self.project.id, 'type': 'text'}, self.session)
        label = data_mocking.create_label({
            'name': 'mylabel',

        }, self.session)
        label_file = data_mocking.create_label_file({
            'label': label,
            'project_id': self.project.id
        }, self.session)
        attach_dir1 = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': [file]
        }, self.session)

        connection = data_mocking.create_connection({
            'name': 'test',
            'integration_name': 'datasaur',
            'project_id': self.project.id
        }, self.session)

        labeldict = {"label_file_list_serialized": [
            {"id": label_file.id, "hash": "083e9ebc48d64e9a8874c6b95f490b56b8c4c5b0f4dacd90bd3534085e87d9fa",
             "type": "label",
             "state": "added", "created_time": "2020-07-15T18:48:34.477333",
             "time_last_updated": "2020-07-15T18:48:34.705290", "ann_is_complete": None, "original_filename": None,
             "video_id": None, "video_parent_file_id": None, "count_instances_changed": None, "attribute_group_list": [
                {"id": 2, "kind": "multiple_select", "is_root": True, "name": "carwheeltag",
                 "prompt": "How is this car wheel", "show_prompt": True, "time_updated": "2020-08-05 19:37:07.703576",
                 "attribute_template_list": [
                     {"id": 4, "name": "Is rounded", "value_type": None, "archived": False, "group_id": 2,
                      "display_order": None},
                     {"id": 5, "name": "is squared", "value_type": None, "archived": False, "group_id": 2,
                      "display_order": None},
                     {"id": 6, "name": "is beautiful", "value_type": None, "archived": False, "group_id": 2,
                      "display_order": None},
                     {"id": 7, "name": "is crazy", "value_type": None, "archived": False, "group_id": 2,
                      "display_order": None}]}, {"id": 3, "kind": "select", "is_root": True, "name": "selectwheel",
                                                 "prompt": "Please selectt something special about this wheels",
                                                 "show_prompt": True, "time_updated": "2020-08-12 16:29:54.817801",
                                                 "attribute_template_list": [
                                                     {"id": 10, "name": "Silver Wheel", "value_type": None,
                                                      "archived": False, "group_id": 3, "display_order": None},
                                                     {"id": 9, "name": "+Gold wheel", "value_type": None,
                                                      "archived": False, "group_id": 3, "display_order": None}]},
                {"id": 4, "kind": "text", "is_root": True, "name": "freewheel",
                 "prompt": "What are your thought on this wheel?", "show_prompt": True,
                 "time_updated": "2020-08-05 20:50:59.195249", "attribute_template_list": []},
                {"id": 5, "kind": "radio", "is_root": True, "name": "clean", "prompt": "Is this wheel clean?",
                 "show_prompt": True, "time_updated": "2020-08-05 20:53:46.314143", "attribute_template_list": [
                    {"id": 11, "name": "Wheel is dirty", "value_type": None, "archived": False, "group_id": 5,
                     "display_order": None},
                    {"id": 12, "name": "Wheek is clean", "value_type": None, "archived": False, "group_id": 5,
                     "display_order": None}]},
                {"id": 6, "kind": "text", "is_root": True, "name": "TEST", "prompt": "TEST28", "show_prompt": True,
                 "time_updated": "2020-08-12 16:30:03.770141", "attribute_template_list": []}],
             "colour": {"hex": "#194d33", "hsl": {"h": 150, "s": 0.5, "l": 0.2, "a": 1},
                        "hsv": {"h": 150, "s": 0.66, "v": 0.3, "a": 1}, "rgba": {"r": 25, "g": 77, "b": 51, "a": 1},
                        "a": 1}, "label": {"id": 5, "name": "Car wheel", "default_sequences_to_single_frame": False}}],
            "label_file_colour_map": {}}
        job = data_mocking.create_job({
            'name': f"my-test-job-{1}",
            'project': self.project,
            'status': 'active',
            'type': "Normal",
            'label_dict': labeldict,
            'attached_directories': [
                attach_dir1
            ],
            'interface_connection_id': connection.id
        }, self.session)

        strategy = DatasaurTaskTemplateAfterLaunchStrategy(
            task_template=job,
            session=self.session,
            log=regular_log.default()
        )
        with patch.object(DatasaurTaskTemplateAfterLaunchStrategy,
                          'create_datasaur_labelset',
                          return_value={'result': {'createLabelSet': {'id': 'mytestid'}}}):
            with patch.object(DatasaurTaskTemplateAfterLaunchStrategy,
                              'create_datasaur_project',
                              return_value={'result': {'id': 'datasaur_test'}}):
                with patch.object(DatasaurTaskTemplateAfterLaunchStrategy,
                                  'get_project_files_list',
                                  return_value={'result': {'id': 'datasaur_test',
                                                           'documents': [{'id': str(file.id), 'name': str(file.id)}]}}):
                    strategy.execute_after_launch_strategy()
                    commit_with_rollback(self.session)
                    tasks_count = self.session.query(Task).filter(
                        Task.job_id == job.id
                    ).count()
                    tasks = self.session.query(Task).filter(
                        Task.job_id == job.id
                    ).all()
                    self.assertEqual(tasks_count, 1)

                    external_map = ExternalMap.get(
                        session=self.session,
                        job_id=job.id,
                        external_id='mytestid',
                        connection_id=connection.id,
                        diffgram_class_string='',
                        type=f"{connection.integration_name}_label_set",
                    )

                    self.assertNotEqual(external_map, None)

                    project_map = ExternalMap.get(
                        session=self.session,
                        job_id=job.id,
                        external_id='datasaur_test',
                        connection_id=connection.id,
                        diffgram_class_string='task_template',
                        type=f"{connection.integration_name}_project",
                    )
                    self.assertNotEqual(project_map, None)

                    files_maps = ExternalMap.get(
                        session=self.session,
                        job_id=job.id,
                        external_id=str(file.id),
                        file_id=file.id,
                        connection_id=connection.id,
                        diffgram_class_string='file',
                        type=f"{connection.integration_name}_file",
                    )
                    self.assertNotEqual(files_maps, None)
