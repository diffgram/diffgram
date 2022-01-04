from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.annotation import Annotation_Update
import uuid
from unittest.mock import patch


class TestAnnotationUpdate(testing_setup.DiffgramBaseTestCase):
    """



    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestAnnotationUpdate, self).setUp()
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

        self.credentials = b64encode("{}:{}".format(self.auth_api.client_id,
                                                    self.auth_api.client_secret).encode()).decode('utf-8')

    def test_check_polygon_points_and_build_bounds(self):
        label_file = data_mocking.create_file({'project_id': self.project.id, 'type': 'label'}, self.session)
        file1 = data_mocking.create_file({'project_id': self.project.id, 'type': 'video'}, self.session)
        frame = data_mocking.create_file(
            {'project_id': self.project.id, 'type': 'frame', 'video_parent_file_id': file1.id, 'frame_number': 5},
            self.session)

        self.project.label_dict['label_file_id_list'] = [label_file.id]
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            instance_list_new = [],
            file = file1,
            do_init_existing_instances = False
        )
        ann_update.instance = data_mocking.create_instance(
            {'creation_ref_id': str(uuid.uuid4()),
             'type': 'polygon',
             'file_id': file1.id,
             'label_file_id': label_file.id
            },
            self.session
        )
        result = ann_update.check_polygon_points_and_build_bounds()
        self.assertFalse(result)
        self.assertTrue('filtered_points' in ann_update.log['error'])
        self.assertEqual(ann_update.log['error']['filtered_points'], '1 or less points.')
        ann_update.instance = data_mocking.create_instance(
            {'creation_ref_id': str(uuid.uuid4()),
             'type': 'polygon',
             'points': {'points':  [{'x': 1, 'y': 1, 'figure_id': 'a'}, {'x': 2, 'y': 2, 'figure_id': 'a'}, {'x': 3, 'y': 3, 'figure_id': 'b'}, {'x': 4, 'y': 4, 'figure_id': 'b'}]},
             'file_id': file1.id,
             'label_file_id': label_file.id
            },
            self.session
        )
        result = ann_update.check_polygon_points_and_build_bounds()
        self.assertTrue(result)
        self.assertEqual(ann_update.instance.points['points'][0]['figure_id'], 'a')
        self.assertEqual(ann_update.instance.points['points'][1]['figure_id'], 'a')
        self.assertEqual(ann_update.instance.points['points'][2]['figure_id'], 'b')
        self.assertEqual(ann_update.instance.points['points'][3]['figure_id'], 'b')

    def test_update_sequence_id_in_cache_list(self):
        label_file = data_mocking.create_file({'project_id': self.project.id, 'type': 'label'}, self.session)
        file1 = data_mocking.create_file({'project_id': self.project.id, 'type': 'video'}, self.session)
        frame = data_mocking.create_file(
            {'project_id': self.project.id, 'type': 'frame', 'video_parent_file_id': file1.id, 'frame_number': 5},
            self.session)
        sequence = data_mocking.create_sequence({
            'label_file_id': label_file.id,
            'video_file_id': file1.id,
            'cache_expiry': time.time() + 500000,
            'number': 1,

        }, self.session)
        instance1 = data_mocking.create_instance(
            {'creation_ref_id': str(uuid.uuid4()), 'x_min': 1, 'x_max': 18, 'y_min': 1, 'y_max': 18,
             'file_id': file1.id, 'label_file_id': label_file.id},
            self.session
        )

        self.project.label_dict['label_file_id_list'] = [label_file.id]
        video_data = {
            'video_mode': True,
            'video_file_id': file1.id,
            'current_frame': frame.frame_number
        }
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            video_data = video_data,
            instance_list_new = [],
            file = file1,
            do_init_existing_instances = False
        )
        ann_update.instance_list_kept_serialized = [
            instance1.serialize_with_label()
        ]
        self.assertEqual(ann_update.instance_list_kept_serialized[0]['sequence_id'], None)
        instance1.sequence_id = sequence.id
        ann_update.update_sequence_id_in_cache_list(instance1)

        self.assertEqual(ann_update.instance_list_kept_serialized[0]['sequence_id'], sequence.id)

    def test_duplicate_instance_update_existing_false(self):
        """
        We send duplicate instances with update_existing = False.
        Expect: Just one of the instances should be saved.
        :return:
        """
        label_file = data_mocking.create_file({'project_id': self.project.id, 'type': 'label'}, self.session)
        file1 = data_mocking.create_file({'project_id': self.project.id, 'type': 'video'}, self.session)
        frame = data_mocking.create_file(
            {'project_id': self.project.id, 'type': 'frame', 'video_parent_file_id': file1.id, 'frame_number': 5},
            self.session)
        inst1 = {
            'creation_ref_id': str(uuid.uuid4()),
            'x_min': 1,
            'y_min': 1,
            'x_max': 18,
            'y_max': 18,
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'box'
        }
        inst2 = inst1.copy()
        self.project.label_dict['label_file_id_list'] = [label_file.id]
        video_data = {
            'video_mode': True,
            'video_file_id': file1.id,
            'current_frame': frame.frame_number
        }
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            video_data = video_data,
            instance_list_new = [inst1, inst2],
            file = file1,
            do_init_existing_instances = False
        )
        updated_file = ann_update.annotation_update_main()
        updated_frame_file = File.get_by_id(self.session, frame.id)

        new_instance_list = updated_frame_file.cache_dict['instance_list']
        deleted_instances = ann_update.new_deleted_instances
        added_instances = ann_update.new_added_instances
        self.assertEqual(len(added_instances), 1)
        self.assertEqual(len(new_instance_list), 1)
        self.assertEqual(len(ann_update.duplicate_hash_new_instance_list), 1)
        self.assertEqual(ann_update.duplicate_hash_new_instance_list[0].x_min, inst1['x_min'])
        self.assertEqual(ann_update.duplicate_hash_new_instance_list[0].x_max, inst1['x_max'])
        self.assertEqual(ann_update.duplicate_hash_new_instance_list[0].y_min, inst1['y_min'])
        self.assertEqual(ann_update.duplicate_hash_new_instance_list[0].y_max, inst1['y_max'])
        self.assertEqual(len(deleted_instances), 0)


    def test_overlap_existing_instances(self):
        """
        2 instances with ids are in different position and then one is placed on the exact position as the other one
        Expect: new overlapped instance is soft deleted and original instance is preserved in cache.
        :return:
        """
        label_file = data_mocking.create_file({'project_id': self.project.id, 'type': 'label'}, self.session)
        file1 = data_mocking.create_file({'project_id': self.project.id, 'type': 'video'}, self.session)
        frame = data_mocking.create_file(
            {'project_id': self.project.id, 'type': 'frame', 'video_parent_file_id': file1.id, 'frame_number': 5},
            self.session)
        inst1 = {
            'creation_ref_id': str(uuid.uuid4()),
            'x_min': 1,
            'y_min': 1,
            'x_max': 18,
            'y_max': 18,
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'box'
        }
        inst2 = {
            'creation_ref_id': str(uuid.uuid4()),
            'x_min': 5,
            'y_min': 5,
            'x_max': 55,
            'y_max': 55,
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'box'
        }

        self.project.label_dict['label_file_id_list'] = [label_file.id]
        video_data = {
            'video_mode': True,
            'video_file_id': file1.id,
            'current_frame': frame.frame_number
        }
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            video_data = video_data,
            instance_list_new = [inst1, inst2],
            file = file1,
            do_init_existing_instances = True
        )
        updated_file = ann_update.annotation_update_main()
        updated_frame_file = File.get_by_id(self.session, frame.id)

        new_instance_list = updated_frame_file.cache_dict['instance_list']
        deleted_instances = ann_update.new_deleted_instances
        added_instances = ann_update.new_added_instances
        self.assertEqual(len(added_instances), 2)
        self.assertEqual(len(new_instance_list), 2)
        self.assertEqual(len(deleted_instances), 0)

        self.assertEqual(new_instance_list[0]['x_min'], inst1['x_min'])
        self.assertEqual(new_instance_list[0]['y_min'], inst1['y_min'])
        self.assertEqual(new_instance_list[0]['x_max'], inst1['x_max'])
        self.assertEqual(new_instance_list[0]['y_max'], inst1['y_max'])
        self.assertFalse(new_instance_list[0]['soft_delete'])
        self.assertIsNotNone(new_instance_list[0]['id'])

        self.assertEqual(new_instance_list[1]['x_min'], inst2['x_min'])
        self.assertEqual(new_instance_list[1]['y_min'], inst2['y_min'])
        self.assertEqual(new_instance_list[1]['x_max'], inst2['x_max'])
        self.assertEqual(new_instance_list[1]['y_max'], inst2['y_max'])
        self.assertFalse(new_instance_list[1]['soft_delete'])
        self.assertIsNotNone(new_instance_list[0]['id'])

        # 2. Now place one instance on top of the other one
        inst1['id'] = new_instance_list[0]['id']
        inst2['id'] = new_instance_list[1]['id']
        inst2['x_min'] = inst1['x_min']
        inst2['x_max'] = inst1['x_max']
        inst2['y_min'] = inst1['y_min']
        inst2['y_max'] = inst1['y_max']
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            video_data = video_data,
            instance_list_new = [inst1, inst2],
            file = file1,
            do_init_existing_instances = True
        )
        updated_file = ann_update.annotation_update_main()
        updated_frame_file = File.get_by_id(self.session, frame.id)

        new_instance_list = updated_frame_file.cache_dict['instance_list']
        deleted_instances = ann_update.new_deleted_instances
        added_instances = ann_update.new_added_instances
        for x in new_instance_list:
            print('aaa', x)

        print(inst1['id'], 'id')
        print(inst2['id'], 'id')
        print('deleted_instances', deleted_instances)
        self.assertEqual(len(added_instances), 0)
        self.assertEqual(len(new_instance_list), 1)
        self.assertEqual(len(deleted_instances), 1)
        self.assertEqual(deleted_instances[0], inst2['id'])
        self.assertFalse(new_instance_list[0]['soft_delete'])
        self.assertIsNotNone(new_instance_list[0]['id'])
        self.assertEqual(new_instance_list[0]['id'], inst1['id'])
        self.assertNotEqual(new_instance_list[0]['id'], inst2['id'])
        updated_inst1 = Instance.get_by_id(self.session, instance_id = inst1['id'])
        updated_inst2 = Instance.get_by_id(self.session, instance_id = inst2['id'])
        self.assertFalse(updated_inst1.soft_delete)
        self.assertTrue(updated_inst2.soft_delete)

    def test_update_move_and_undo_case(self):
        """
            We create an instance, move it, save it, undo it, save it and redoit and save again
            Expect:File cache should have the newest instance as this was the latests version of it
        :return:
        """
        label_file = data_mocking.create_file({'project_id': self.project.id, 'type': 'label'}, self.session)
        file1 = data_mocking.create_file({'project_id': self.project.id, 'type': 'video'}, self.session)
        frame = data_mocking.create_file(
            {'project_id': self.project.id, 'type': 'frame', 'video_parent_file_id': file1.id, 'frame_number': 5},
            self.session)
        inst1 = {
            'creation_ref_id': str(uuid.uuid4()),
            'x_min': 1,
            'y_min': 1,
            'x_max': 18,
            'y_max': 18,
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'box'
        }

        self.project.label_dict['label_file_id_list'] = [label_file.id]
        video_data = {
            'video_mode': True,
            'video_file_id': file1.id,
            'current_frame': frame.frame_number
        }
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            video_data = video_data,
            instance_list_new = [inst1],
            file = file1,
            do_init_existing_instances = True
        )
        updated_file = ann_update.annotation_update_main()
        updated_frame_file = File.get_by_id(self.session, frame.id)

        new_instance_list = updated_frame_file.cache_dict['instance_list']
        deleted_instances = ann_update.new_deleted_instances
        added_instances = ann_update.new_added_instances

        self.assertEqual(len(added_instances), 1)
        self.assertEqual(len(new_instance_list), 1)
        self.assertEqual(len(deleted_instances), 0)

        self.assertEqual(new_instance_list[0]['x_min'], inst1['x_min'])
        self.assertEqual(new_instance_list[0]['y_min'], inst1['y_min'])
        self.assertEqual(new_instance_list[0]['x_max'], inst1['x_max'])
        self.assertEqual(new_instance_list[0]['y_max'], inst1['y_max'])
        self.assertFalse(new_instance_list[0]['soft_delete'])
        self.assertIsNotNone(new_instance_list[0]['id'])
        old_id = int(new_instance_list[0]['id'])

        # 2. Move The Instance
        inst1 = {
            'id': old_id,
            'creation_ref_id': str(uuid.uuid4()),
            'x_min': 10,
            'y_min': 10,
            'x_max': 28,
            'y_max': 28,
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'box'
        }
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            video_data = video_data,
            instance_list_new = [inst1],
            file = file1,
            do_init_existing_instances = True
        )
        updated_file = ann_update.annotation_update_main()
        updated_frame_file = File.get_by_id(self.session, frame.id)

        new_instance_list = updated_frame_file.cache_dict['instance_list']
        deleted_instances = ann_update.new_deleted_instances
        added_instances = ann_update.new_added_instances

        self.assertEqual(len(added_instances), 1)
        self.assertEqual(len(new_instance_list), 1)
        self.assertEqual(len(deleted_instances), 1)
        self.assertEqual(deleted_instances[0], old_id)
        self.assertEqual(new_instance_list[0]['x_min'], inst1['x_min'])
        self.assertEqual(new_instance_list[0]['y_min'], inst1['y_min'])
        self.assertEqual(new_instance_list[0]['x_max'], inst1['x_max'])
        self.assertEqual(new_instance_list[0]['y_max'], inst1['y_max'])
        self.assertFalse(new_instance_list[0]['soft_delete'])
        self.assertNotEqual(new_instance_list[0]['id'], old_id)
        moved_id = int(new_instance_list[0]['id'])
        # 3. Undo the instance
        inst_undone = {
            'id': moved_id,
            'creation_ref_id': str(uuid.uuid4()),
            'x_min': 10,
            'y_min': 10,
            'x_max': 28,
            'y_max': 28,
            'soft_delete': True,
            'label_file_id': label_file.id,
            'type': 'box'
        }
        inst1 = {
            'id': old_id,
            'creation_ref_id': str(uuid.uuid4()),
            'x_min': 1,
            'y_min': 1,
            'x_max': 18,
            'y_max': 18,
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'box'
        }
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            video_data = video_data,
            instance_list_new = [inst_undone, inst1],
            file = file1,
            do_init_existing_instances = True
        )
        updated_file = ann_update.annotation_update_main()
        updated_frame_file = File.get_by_id(self.session, frame.id)

        new_instance_list = updated_frame_file.cache_dict['instance_list']
        deleted_instances = ann_update.new_deleted_instances
        added_instances = ann_update.new_added_instances

        self.assertEqual(len(added_instances), 2)
        self.assertEqual(len(new_instance_list), 2)
        self.assertEqual(len(deleted_instances), 1)
        self.assertEqual(deleted_instances[0], inst_undone['id'])
        self.assertEqual(new_instance_list[0]['x_min'], inst_undone['x_min'])
        self.assertEqual(new_instance_list[0]['y_min'], inst_undone['y_min'])
        self.assertEqual(new_instance_list[0]['x_max'], inst_undone['x_max'])
        self.assertEqual(new_instance_list[0]['y_max'], inst_undone['y_max'])
        self.assertNotEqual(inst_undone['id'], new_instance_list[0]['id'])
        self.assertNotEqual(new_instance_list[0]['id'], old_id)
        self.assertTrue(new_instance_list[0]['soft_delete'])

        self.assertEqual(new_instance_list[1]['x_min'], inst1['x_min'])
        self.assertEqual(new_instance_list[1]['y_min'], inst1['y_min'])
        self.assertEqual(new_instance_list[1]['x_max'], inst1['x_max'])
        self.assertEqual(new_instance_list[1]['y_max'], inst1['y_max'])
        self.assertFalse(new_instance_list[1]['soft_delete'])
        self.assertNotEqual(new_instance_list[1]['id'], old_id)
        newest_id = int(new_instance_list[1]['id'])
        deleted_id = int(new_instance_list[0]['id'])
        # 4. Redo the instance
        inst_redone = {
            'id': deleted_id,
            'creation_ref_id': str(uuid.uuid4()),
            'x_min': 10,
            'y_min': 10,
            'x_max': 28,
            'y_max': 28,
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'box'
        }
        inst1 = {
            'id': newest_id,
            'creation_ref_id': str(uuid.uuid4()),
            'x_min': 1,
            'y_min': 1,
            'x_max': 18,
            'y_max': 18,
            'soft_delete': True,
            'label_file_id': label_file.id,
            'type': 'box'
        }
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            video_data = video_data,
            instance_list_new = [inst_redone, inst1],
            file = file1,
            do_init_existing_instances = True
        )
        updated_file = ann_update.annotation_update_main()
        updated_frame_file = File.get_by_id(self.session, frame.id)

        new_instance_list = updated_frame_file.cache_dict['instance_list']
        deleted_instances = ann_update.new_deleted_instances
        added_instances = ann_update.new_added_instances

        self.assertEqual(len(added_instances), 2)
        self.assertEqual(len(new_instance_list), 2)
        self.assertEqual(len(deleted_instances), 2)
        self.assertEqual(deleted_instances[0], newest_id)
        self.assertEqual(deleted_instances[1], deleted_id)
        self.assertEqual(new_instance_list[0]['x_min'], inst_redone['x_min'])
        self.assertEqual(new_instance_list[0]['y_min'], inst_redone['y_min'])
        self.assertEqual(new_instance_list[0]['x_max'], inst_redone['x_max'])
        self.assertEqual(new_instance_list[0]['y_max'], inst_redone['y_max'])
        self.assertNotEqual(inst_redone['id'], new_instance_list[0]['id'])
        self.assertNotEqual(new_instance_list[0]['id'], deleted_id)
        self.assertFalse(new_instance_list[0]['soft_delete'])

        self.assertEqual(new_instance_list[1]['x_min'], inst1['x_min'])
        self.assertEqual(new_instance_list[1]['y_min'], inst1['y_min'])
        self.assertEqual(new_instance_list[1]['x_max'], inst1['x_max'])
        self.assertEqual(new_instance_list[1]['y_max'], inst1['y_max'])
        self.assertTrue(new_instance_list[1]['soft_delete'])
        self.assertNotEqual(new_instance_list[1]['id'], newest_id)

    def test_update_on_duplicate_instance_undo_case(self):
        """
            We send 2 instances that are equal, one with an ID and the other one with no ID
            expect: Instance with ID should be existing and new instance should be ignored
        :return:
        """
        label_file = data_mocking.create_file({'project_id': self.project.id, 'type': 'label'}, self.session)
        file1 = data_mocking.create_file({'project_id': self.project.id, 'type': 'video'}, self.session)
        frame = data_mocking.create_file(
            {'project_id': self.project.id, 'type': 'frame', 'video_parent_file_id': file1.id, 'frame_number': 5},
            self.session)
        inst1 = {
            'creation_ref_id': str(uuid.uuid4()),
            'x_min': 1,
            'y_min': 1,
            'x_max': 18,
            'y_max': 18,
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'box'
        }

        self.project.label_dict['label_file_id_list'] = [label_file.id]
        video_data = {
            'video_mode': True,
            'video_file_id': file1.id,
            'current_frame': frame.frame_number
        }
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            video_data = video_data,
            instance_list_new = [inst1],
            file = file1,
            do_init_existing_instances = True
        )
        updated_file = ann_update.annotation_update_main()
        updated_frame_file = File.get_by_id(self.session, frame.id)

        new_instance_list = updated_frame_file.cache_dict['instance_list']
        deleted_instances = ann_update.new_deleted_instances
        added_instances = ann_update.new_added_instances

        self.assertEqual(len(added_instances), 1)
        self.assertEqual(len(new_instance_list), 1)
        self.assertEqual(len(deleted_instances), 0)

        self.assertEqual(new_instance_list[0]['x_min'], inst1['x_min'])
        self.assertEqual(new_instance_list[0]['y_min'], inst1['y_min'])
        self.assertEqual(new_instance_list[0]['x_max'], inst1['x_max'])
        self.assertEqual(new_instance_list[0]['y_max'], inst1['y_max'])
        self.assertFalse(new_instance_list[0]['soft_delete'])
        self.assertIsNotNone(new_instance_list[0]['id'])
        old_id = int(new_instance_list[0]['id'])

        # 2. Move The Instance
        inst1 = {
            'id': old_id,
            'creation_ref_id': str(uuid.uuid4()),
            'x_min': 10,
            'y_min': 10,
            'x_max': 28,
            'y_max': 28,
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'box'
        }
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            video_data = video_data,
            instance_list_new = [inst1],
            file = file1,
            do_init_existing_instances = True
        )
        updated_file = ann_update.annotation_update_main()
        updated_frame_file = File.get_by_id(self.session, frame.id)

        new_instance_list = updated_frame_file.cache_dict['instance_list']
        deleted_instances = ann_update.new_deleted_instances
        added_instances = ann_update.new_added_instances

        self.assertEqual(len(added_instances), 1)
        self.assertEqual(len(new_instance_list), 1)
        self.assertEqual(len(deleted_instances), 1)
        self.assertEqual(deleted_instances[0], old_id)
        self.assertEqual(new_instance_list[0]['x_min'], inst1['x_min'])
        self.assertEqual(new_instance_list[0]['y_min'], inst1['y_min'])
        self.assertEqual(new_instance_list[0]['x_max'], inst1['x_max'])
        self.assertEqual(new_instance_list[0]['y_max'], inst1['y_max'])
        self.assertFalse(new_instance_list[0]['soft_delete'])
        self.assertNotEqual(new_instance_list[0]['id'], old_id)
        # 3. Undo the instance
        inst_undone = {
            'id': new_instance_list[0]['id'],
            'creation_ref_id': str(uuid.uuid4()),
            'x_min': 10,
            'y_min': 10,
            'x_max': 28,
            'y_max': 28,
            'soft_delete': True,
            'label_file_id': label_file.id,
            'type': 'box'
        }
        inst1 = {
            'id': old_id,
            'creation_ref_id': str(uuid.uuid4()),
            'x_min': 1,
            'y_min': 1,
            'x_max': 18,
            'y_max': 18,
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'box'
        }
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            video_data = video_data,
            instance_list_new = [inst_undone, inst1],
            file = file1,
            do_init_existing_instances = True
        )
        updated_file = ann_update.annotation_update_main()
        updated_frame_file = File.get_by_id(self.session, frame.id)

        new_instance_list = updated_frame_file.cache_dict['instance_list']
        deleted_instances = ann_update.new_deleted_instances
        added_instances = ann_update.new_added_instances

        self.assertEqual(len(added_instances), 2)
        self.assertEqual(len(new_instance_list), 2)
        self.assertEqual(len(deleted_instances), 1)
        self.assertEqual(deleted_instances[0], inst_undone['id'])
        self.assertEqual(new_instance_list[0]['x_min'], inst_undone['x_min'])
        self.assertEqual(new_instance_list[0]['y_min'], inst_undone['y_min'])
        self.assertEqual(new_instance_list[0]['x_max'], inst_undone['x_max'])
        self.assertEqual(new_instance_list[0]['y_max'], inst_undone['y_max'])
        self.assertNotEqual(inst_undone['id'], new_instance_list[0]['id'])
        self.assertNotEqual(new_instance_list[0]['id'], old_id)
        self.assertTrue(new_instance_list[0]['soft_delete'])

        self.assertEqual(new_instance_list[1]['x_min'], inst1['x_min'])
        self.assertEqual(new_instance_list[1]['y_min'], inst1['y_min'])
        self.assertEqual(new_instance_list[1]['x_max'], inst1['x_max'])
        self.assertEqual(new_instance_list[1]['y_max'], inst1['y_max'])
        self.assertFalse(new_instance_list[1]['soft_delete'])

    def test_update_on_duplicate_instance_1_id_1_no_id(self):
        """
            We send 2 instances that are equal, one with an ID and the other one with no ID
            expect: Instance with ID should be existing and new instance should be ignored
        :return:
        """
        label_file = data_mocking.create_file({'project_id': self.project.id, 'type': 'label'}, self.session)
        file1 = data_mocking.create_file({'project_id': self.project.id, 'type': 'video'}, self.session)
        frame = data_mocking.create_file(
            {'project_id': self.project.id, 'type': 'frame', 'video_parent_file_id': file1.id, 'frame_number': 5},
            self.session)
        instance1 = data_mocking.create_instance(
            {'creation_ref_id': str(uuid.uuid4()), 'x_min': 1, 'x_max': 18, 'y_min': 1, 'y_max': 18,
             'file_id': file1.id, 'label_file_id': label_file.id},
            self.session
        )

        inst1 = {
            'id': instance1.id,  # This one has the ID
            'creation_ref_id': instance1.creation_ref_id,
            'x_min': instance1.x_min,
            'y_min': instance1.y_min,
            'x_max': instance1.x_max,
            'y_max': instance1.y_max,
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'box'
        }

        inst2 = {
            'creation_ref_id': str(uuid.uuid4()),
            'x_min': 1,
            'y_min': 1,
            'x_max': 18,
            'y_max': 18,
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'box'
        }

        self.project.label_dict['label_file_id_list'] = [label_file.id]
        video_data = {
            'video_mode': True,
            'video_file_id': file1.id,
            'current_frame': frame.frame_number
        }
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            video_data = video_data,
            instance_list_new = [inst1, inst2],
            file = file1,
            do_init_existing_instances = True
        )
        updated_file = ann_update.annotation_update_main()
        updated_frame_file = File.get_by_id(self.session, frame.id)

        new_instance_list = updated_frame_file.cache_dict['instance_list']
        for x in new_instance_list:
            print('instance new', x)
        deleted_instances = ann_update.new_deleted_instances
        added_instances = ann_update.new_added_instances

        self.assertEqual(len(added_instances), 1)
        self.assertEqual(len(new_instance_list), 1)
        self.assertEqual(len(deleted_instances), 0)

        self.assertEqual(new_instance_list[0]['x_min'], inst1['x_min'])
        self.assertEqual(new_instance_list[0]['y_min'], inst1['y_min'])
        self.assertEqual(new_instance_list[0]['x_max'], inst1['x_max'])
        self.assertEqual(new_instance_list[0]['y_max'], inst1['y_max'])
        self.assertFalse(new_instance_list[0]['soft_delete'])
        self.assertNotEqual(new_instance_list[0]['id'], instance1.id)

        # Test with cache regenerated too
        updated_frame_file.set_cache_key_dirty(cache_key = 'instance_list')
        regenerated_instance_list = updated_frame_file.get_with_cache(
            cache_key = 'instance_list',
            cache_miss_function = updated_frame_file.serialize_instance_list_only,
            session = self.session)

        self.assertEqual(len(regenerated_instance_list), 1)

        self.assertEqual(regenerated_instance_list[0]['x_min'], inst1['x_min'])
        self.assertEqual(regenerated_instance_list[0]['y_min'], inst1['y_min'])
        self.assertEqual(regenerated_instance_list[0]['x_max'], inst1['x_max'])
        self.assertEqual(regenerated_instance_list[0]['y_max'], inst1['y_max'])
        self.assertFalse(regenerated_instance_list[0]['soft_delete'])
        self.assertNotEqual(regenerated_instance_list[0]['id'], instance1.id)

        deleted_instance = Instance.get_by_id(session = self.session, instance_id = instance1.id)
        self.assertFalse(deleted_instance.soft_delete)

    def test_update_on_duplicate_instance_no_ids(self):
        """
            We send 2 instances that are equal and dont have ID
            expect: File cache should just have one of them, other one should be ignored
        :return:
        """
        label_file = data_mocking.create_file({'project_id': self.project.id, 'type': 'label'}, self.session)
        file1 = data_mocking.create_file({'project_id': self.project.id, 'type': 'video'}, self.session)
        frame = data_mocking.create_file(
            {'project_id': self.project.id, 'type': 'frame', 'video_parent_file_id': file1.id, 'frame_number': 5},
            self.session)
        inst1 = {
            'creation_ref_id': str(uuid.uuid4()),
            'x_min': 1,
            'y_min': 1,
            'x_max': 18,
            'y_max': 18,
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'box'
        }
        inst2 = inst1.copy()
        self.project.label_dict['label_file_id_list'] = [label_file.id]
        video_data = {
            'video_mode': True,
            'video_file_id': file1.id,
            'current_frame': frame.frame_number
        }
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            video_data = video_data,
            instance_list_new = [inst1, inst2],
            file = file1,
            do_init_existing_instances = True
        )
        updated_file = ann_update.annotation_update_main()
        updated_frame_file = File.get_by_id(self.session, frame.id)

        new_instance_list = updated_frame_file.cache_dict['instance_list']
        deleted_instances = ann_update.new_deleted_instances
        added_instances = ann_update.new_added_instances

        self.assertEqual(len(added_instances), 1)
        self.assertEqual(len(new_instance_list), 1)
        self.assertEqual(len(deleted_instances), 0)

        self.assertEqual(new_instance_list[0]['x_min'], inst1['x_min'])
        self.assertEqual(new_instance_list[0]['y_min'], inst1['y_min'])
        self.assertEqual(new_instance_list[0]['x_max'], inst1['x_max'])
        self.assertEqual(new_instance_list[0]['y_max'], inst1['y_max'])
        self.assertIsNotNone(new_instance_list[0]['id'])

        # Test with cache regenerated too
        updated_frame_file.set_cache_key_dirty(cache_key = 'instance_list')
        regenerated_instance_list = updated_frame_file.get_with_cache(
            cache_key = 'instance_list',
            cache_miss_function = updated_frame_file.serialize_instance_list_only,
            session = self.session)

        self.assertEqual(len(regenerated_instance_list), 1)

        self.assertEqual(regenerated_instance_list[0]['x_min'], inst1['x_min'])
        self.assertEqual(regenerated_instance_list[0]['y_min'], inst1['y_min'])
        self.assertEqual(regenerated_instance_list[0]['x_max'], inst1['x_max'])
        self.assertEqual(regenerated_instance_list[0]['y_max'], inst1['y_max'])

    def test_update_non_duplicate_instances_no_ids(self):
        """
            We send a list of non duplicate instances with no IDs
            expect: File cache should have all those instances with new ID's
        :return:
        """
        label_file = data_mocking.create_file({'project_id': self.project.id, 'type': 'label'}, self.session)
        file1 = data_mocking.create_file({'project_id': self.project.id, 'type': 'video'}, self.session)
        frame = data_mocking.create_file(
            {'project_id': self.project.id, 'type': 'frame', 'video_parent_file_id': file1.id, 'frame_number': 5},
            self.session)
        inst1 = {
            'creation_ref_id': str(uuid.uuid4()),
            'x_min': 1,
            'y_min': 1,
            'x_max': 18,
            'y_max': 18,
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'box'
        }
        inst2 = {
            'creation_ref_id': str(uuid.uuid4()),
            'x_min': 50,
            'y_min': 50,
            'x_max': 120,
            'y_max': 120,
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'box'
        }
        self.project.label_dict['label_file_id_list'] = [label_file.id]
        video_data = {
            'video_mode': True,
            'video_file_id': file1.id,
            'current_frame': frame.frame_number
        }
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            video_data = video_data,
            instance_list_new = [inst1, inst2],
            file = file1,
            do_init_existing_instances = True
        )
        updated_file = ann_update.annotation_update_main()
        updated_frame_file = File.get_by_id(self.session, frame.id)

        new_instance_list = updated_frame_file.cache_dict['instance_list']
        deleted_instances = ann_update.new_deleted_instances
        added_instances = ann_update.new_added_instances

        self.assertEqual(len(added_instances), 2)
        self.assertEqual(len(new_instance_list), 2)
        self.assertEqual(len(deleted_instances), 0)

        self.assertEqual(new_instance_list[0]['x_min'], inst1['x_min'])
        self.assertEqual(new_instance_list[0]['y_min'], inst1['y_min'])
        self.assertEqual(new_instance_list[0]['x_max'], inst1['x_max'])
        self.assertEqual(new_instance_list[0]['y_max'], inst1['y_max'])
        self.assertIsNotNone(new_instance_list[0]['id'])

        self.assertEqual(new_instance_list[1]['x_min'], inst2['x_min'])
        self.assertEqual(new_instance_list[1]['y_min'], inst2['y_min'])
        self.assertEqual(new_instance_list[1]['x_max'], inst2['x_max'])
        self.assertEqual(new_instance_list[1]['y_max'], inst2['y_max'])
        self.assertIsNotNone(new_instance_list[1]['id'])

    def test_detect_and_remove_collisions(self):
        label_file = data_mocking.create_file({'project_id': self.project.id, 'type': 'label'}, self.session)
        file1 = data_mocking.create_file({'project_id': self.project.id, 'type': 'video'}, self.session)
        frame = data_mocking.create_file(
            {'project_id': self.project.id, 'type': 'frame', 'video_parent_file_id': file1.id, 'frame_number': 5},
            self.session)
        instance1 = data_mocking.create_instance(
            {'x_min': 1, 'x_max': 10, 'y_min': 1, 'y_max': 10, 'file_id': file1.id, 'label_file_id': label_file.id},
            self.session
        )
        instance2 = data_mocking.create_instance(
            {'x_min': 1, 'x_max': 10, 'y_min': 1, 'y_max': 10, 'file_id': file1.id, 'label_file_id': label_file.id},
            self.session
        )
        instance3 = data_mocking.create_instance(
            {'x_min': 1, 'x_max': 10, 'y_min': 1, 'y_max': 10, 'file_id': file1.id, 'label_file_id': label_file.id},
            self.session
        )
        instance1.hash_instance()
        instance2.hash_instance()
        instance3.hash_instance()
        video_data = {
            'video_mode': True,
            'video_file_id': file1.id,
            'current_frame': frame.frame_number
        }
        inst_list = [instance1, instance2, instance3]
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            video_data = video_data,
            instance_list_new = [],
            file = file1,
            do_init_existing_instances = True
        )
        result = ann_update.detect_and_remove_collisions(inst_list)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], instance3)

    def test_update_cache_single_instance_in_list_context(self):
        """
            Test that the instance gets serialized correctly and that if the instance has no ID
            the function does not serializer anything.
        :return:
        """
        file1 = data_mocking.create_file({'project_id': self.project.id, 'type': 'video'}, self.session)
        frame = data_mocking.create_file(
            {'project_id': self.project.id, 'type': 'frame', 'video_parent_file_id': file1.id, 'frame_number': 5},
            self.session)
        label_file = data_mocking.create_file({'project_id': self.project.id, 'type': 'label'}, self.session)
        # 2 Exactly equal instances
        instance1 = data_mocking.create_instance(
            {'x_min': 1, 'x_max': 10, 'y_min': 1, 'y_max': 10, 'file_id': file1.id, 'label_file_id': label_file.id},
            self.session
        )
        instance2 = data_mocking.create_instance(
            {'x_min': 1, 'x_max': 10, 'y_min': 1, 'y_max': 10, 'file_id': file1.id, 'soft_delete': True,
             'label_file_id': label_file.id},
            self.session
        )
        self.project.label_dict['label_file_id_list'] = [label_file.id]
        inst = {
            'creation_ref_id': str(uuid.uuid4()),
            'x_min': 1,
            'y_min': 1,
            'x_max': 18,
            'y_max': 18,
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'box'
        }
        instance_data = [
            inst.copy(),
            inst.copy()
        ]
        video_data = {
            'video_mode': True,
            'video_file_id': file1.id,
            'current_frame': frame.frame_number
        }

        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            video_data = video_data,
            instance_list_new = instance_data,
            file = file1,
            do_init_existing_instances = True
        )

        with patch.object(instance1, 'serialize_with_label') as mock_1:
            ann_update.instance = instance1
            ann_update.update_cache_single_instance_in_list_context()
            mock_1.assert_called_once()

        with patch.object(instance2, 'serialize_with_label') as mock_1:
            instance2.id = None
            ann_update.instance = instance2
            ann_update.update_cache_single_instance_in_list_context()
            self.assertEqual(mock_1.call_count, 0)

    def test_append_new_instance_list_hash(self):
        file1 = data_mocking.create_file({'project_id': self.project.id, 'type': 'video'}, self.session)
        frame = data_mocking.create_file(
            {'project_id': self.project.id, 'type': 'frame', 'video_parent_file_id': file1.id, 'frame_number': 5},
            self.session)
        label_file = data_mocking.create_file({'project_id': self.project.id, 'type': 'label'}, self.session)
        # 2 Exactly equal instances
        instance1 = data_mocking.create_instance(
            {'x_min': 1, 'x_max': 10, 'y_min': 1, 'y_max': 10, 'file_id': file1.id, 'label_file_id': label_file.id},
            self.session
        )
        instance2 = data_mocking.create_instance(
            {'x_min': 1, 'x_max': 10, 'y_min': 1, 'y_max': 10, 'file_id': file1.id, 'soft_delete': True,
             'label_file_id': label_file.id},
            self.session
        )
        self.project.label_dict['label_file_id_list'] = [label_file.id]
        inst = {
            'creation_ref_id': str(uuid.uuid4()),
            'x_min': 1,
            'y_min': 1,
            'x_max': 18,
            'y_max': 18,
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'box'
        }
        instance_data = [
            inst.copy(),
            inst.copy()
        ]
        video_data = {
            'video_mode': True,
            'video_file_id': file1.id,
            'current_frame': frame.frame_number
        }

        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            video_data = video_data,
            instance_list_new = instance_data,
            file = file1,
            do_init_existing_instances = True
        )
        result = ann_update.append_new_instance_list_hash(instance = instance1)
        result2 = ann_update.append_new_instance_list_hash(instance = instance2)

        self.assertTrue(result)
        self.assertFalse(result2)

    def test_order_new_instance_list_by_date(self):
        file1 = data_mocking.create_file({'project_id': self.project.id, 'type': 'video'}, self.session)
        frame = data_mocking.create_file(
            {'project_id': self.project.id, 'type': 'frame', 'video_parent_file_id': file1.id, 'frame_number': 5},
            self.session)
        label_file = data_mocking.create_file({'project_id': self.project.id, 'type': 'label'}, self.session)
        inst1 = {
            'creation_ref_id': str(uuid.uuid4()),
            'x_min': 1,
            'y_min': 1,
            'x_max': 18,
            'y_max': 18,
            'client_created_time': datetime.datetime(2020, 1, 1),
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'box'
        }
        inst2 = {
            'creation_ref_id': str(uuid.uuid4()),
            'x_min': 1,
            'y_min': 1,
            'x_max': 18,
            'y_max': 18,
            'client_created_time': datetime.datetime(2020, 1, 2),
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'box'
        }
        inst3 = {
            'creation_ref_id': str(uuid.uuid4()),
            'x_min': 1,
            'y_min': 1,
            'x_max': 18,
            'y_max': 18,
            'client_created_time': datetime.datetime(2020, 1, 3),
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'box'
        }
        inst4 = {
            'creation_ref_id': str(uuid.uuid4()),
            'x_min': 1,
            'y_min': 1,
            'x_max': 18,
            'y_max': 18,
            'client_created_time': None,
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'box'
        }
        inst_list = [inst1, inst2, inst3, inst4]
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            video_data = None,
            instance_list_new = inst_list,
            file = file1,
            do_init_existing_instances = True
        )
        ann_update.instance_list_new = inst_list
        print('orders', ann_update.instance_list_new)
        ann_update.order_new_instances_by_date()

        self.assertEqual(ann_update.instance_list_new[0], inst3)
        self.assertEqual(ann_update.instance_list_new[1], inst2)
        self.assertEqual(ann_update.instance_list_new[2], inst1)
        self.assertEqual(ann_update.instance_list_new[3], inst4)

    def test_special__removing_duplicate_instances_in_new_instance_list(self):
        """
            This is an important test to test when the client is sending the same
            instance data twice in the payload. Not handling this can lead to unexpected results.
            Check: https://github.com/diffgram/diffgram/issues/226
        :return:
        """
        file1 = data_mocking.create_file({'project_id': self.project.id, 'type': 'video'}, self.session)
        frame = data_mocking.create_file(
            {'project_id': self.project.id, 'type': 'frame', 'video_parent_file_id': file1.id, 'frame_number': 5},
            self.session)
        label_file = data_mocking.create_file({'project_id': self.project.id, 'type': 'label'}, self.session)
        # 2 Exactly equal instances
        self.project.label_dict['label_file_id_list'] = [label_file.id]
        inst = {
            'creation_ref_id': str(uuid.uuid4()),
            'x_min': 1,
            'y_min': 1,
            'x_max': 18,
            'y_max': 18,
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'box'
        }
        instance_data = [
            inst.copy(),
            inst.copy()
        ]
        video_data = {
            'video_mode': True,
            'video_file_id': file1.id,
            'current_frame': frame.frame_number
        }

        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            video_data = video_data,
            instance_list_new = instance_data,
            file = file1,
            do_init_existing_instances = True
        )
        ann_update.main()

        deleted_instances = ann_update.new_deleted_instances
        added_instances = ann_update.new_added_instances

        self.assertEqual(len(added_instances), 1)

    def test__check_all_instances_available_in_new_instance_list(self):
        file1 = data_mocking.create_file({'project_id': self.project.id}, self.session)
        label_file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        instance1 = data_mocking.create_instance(
            {'x_min': 1, 'x_max': 10, 'y_min': 1, 'y_max': 10, 'file_id': file1.id, 'label_file_id': label_file.id},
            self.session
        )
        instance2 = data_mocking.create_instance(
            {'x_min': 2, 'x_max': 10, 'y_min': 1, 'y_max': 10, 'file_id': file1.id, 'label_file_id': label_file.id},
            self.session
        )

        instance3 = data_mocking.create_instance(
            {'x_min': 3, 'x_max': 10, 'y_min': 1, 'y_max': 10, 'file_id': file1.id, 'label_file_id': label_file.id},
            self.session
        )
        instance1.hash_instance()
        instance2.hash_instance()
        instance3.hash_instance()
        old_payload = [instance1, instance2, instance3]
        new_list_payload = [x.serialize_with_label() for x in old_payload]
        new_list_payload_wrong = [instance1.serialize_with_label()]

        # Test Case where we don't want to run verification
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            instance_list_new = new_list_payload,
            file = file1,
            do_init_existing_instances = False
        )
        result = ann_update._Annotation_Update__check_all_instances_available_in_new_instance_list()

        self.assertTrue(result)

        # Now test case with validations
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            instance_list_new = new_list_payload,
            file = file1,
            do_init_existing_instances = True
        )
        result = ann_update._Annotation_Update__check_all_instances_available_in_new_instance_list()

        self.assertTrue(result)

        # Now test case with validations and a wrong payload
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            instance_list_new = new_list_payload_wrong,
            file = file1,
            do_init_existing_instances = True
        )
        result = ann_update._Annotation_Update__check_all_instances_available_in_new_instance_list()
        print('ann_update.log', ann_update.log)
        self.assertTrue(result)
        self.assertTrue(len(ann_update.log['warning'].keys()) > 0)
        self.assertTrue('new_instance_list_missing_ids' in ann_update.log['warning'])
        self.assertTrue('information' in ann_update.log['warning'])
        self.assertTrue('missing_ids' in ann_update.log['warning'])
        self.assertTrue(instance2.id in ann_update.log['warning']['missing_ids'])
        self.assertTrue(instance3.id in ann_update.log['warning']['missing_ids'])

        # Now test case with validations and a wrong payload and some existing deleted instances
        instance4 = data_mocking.create_instance(
            {'x_min': 1, 'x_max': 10, 'y_min': 1, 'y_max': 10, 'file_id': file1.id, 'soft_delete': True,
             'label_file_id': label_file.id},
            self.session
        )
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            instance_list_new = new_list_payload_wrong,
            file = file1,
            do_init_existing_instances = True
        )
        result = ann_update._Annotation_Update__check_all_instances_available_in_new_instance_list()

        self.assertTrue(result)
        self.assertTrue(len(ann_update.log['warning'].keys()) > 0)
        self.assertTrue('new_instance_list_missing_ids' in ann_update.log['warning'])
        self.assertTrue('information' in ann_update.log['warning'])
        self.assertTrue('missing_ids' in ann_update.log['warning'])
        self.assertTrue(instance2.id in ann_update.log['warning']['missing_ids'])
        self.assertTrue(instance3.id in ann_update.log['warning']['missing_ids'])
        self.assertTrue(instance4.id not in ann_update.log['warning']['missing_ids'])
