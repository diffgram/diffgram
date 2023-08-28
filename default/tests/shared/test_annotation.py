import uuid
import hashlib

from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.annotation import Annotation_Update
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
             'points': {'points': [{'x': 1, 'y': 1, 'figure_id': 'a'}, {'x': 2, 'y': 2, 'figure_id': 'a'},
                                   {'x': 3, 'y': 3, 'figure_id': 'b'}, {'x': 4, 'y': 4, 'figure_id': 'b'}]},
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

    def test_order_new_instances_by_date(self):
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
        ann_update.order_new_instances_by_date()

        self.assertEqual(ann_update.instance_list_new[0], inst3)
        self.assertEqual(ann_update.instance_list_new[1], inst2)
        self.assertEqual(ann_update.instance_list_new[2], inst1)
        self.assertEqual(ann_update.instance_list_new[3], inst4)

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

    def test_check_relations_id_existence(self):
        """
            Check calls to check_relations_id_existence
        :return:
        """
        file1 = data_mocking.create_file({'project_id': self.project.id, 'type': 'image'}, self.session)
        frame = data_mocking.create_file(
            {'project_id': self.project.id, 'type': 'frame', 'video_parent_file_id': file1.id, 'frame_number': 5},
            self.session)
        label_file = data_mocking.create_file({'project_id': self.project.id, 'type': 'label'}, self.session)
        # 2 Exactly equal instances
        self.project.label_dict['label_file_id_list'] = [label_file.id]
        instance1 = data_mocking.create_instance(
            {'x_min': 1,
             'x_max': 10,
             'y_min': 1,
             'y_max': 10,
             'file_id': file1.id,
             'label_file_id': label_file.id,
             'type': 'relation'
             },
            self.session
        )
        instance2 = data_mocking.create_instance(
            {'x_min': 2,
             'x_max': 15,
             'y_min': 2,
             'y_max': 15,
             'file_id': file1.id,
             'label_file_id': label_file.id,
             'type': 'box'
             },
            self.session
        )
        ann_update2 = Annotation_Update(
            session = self.session,
            project = self.project,
            instance_list_new = [],
            file = file1,
            do_init_existing_instances = True
        )

        ann_update2.instance = instance1
        # Check Error State
        ann_update2.check_relations_id_existence(None, None, None, None)
        self.assertTrue('from_id' in ann_update2.log['error'])
        # Check IDs available
        ann_update2.log['error'] = {}
        ann_update2.instance.from_instance_id = 1
        ann_update2.instance.to_instance_id = 1
        ann_update2.check_relations_id_existence(ann_update2.instance.from_instance_id,
                                                 ann_update2.instance.to_instance_id,
                                                 None,
                                                 None)
        self.assertEqual(len(ann_update2.log['error'].keys()), 0)
        self.assertEqual(len(ann_update2.new_instance_relations_list_no_ids), 0)
        # Check IDs Not available
        ann_update2.check_relations_id_existence(None,
                                                 None,
                                                 str(uuid.uuid4()),
                                                 str(uuid.uuid4()))
        self.assertEqual(len(ann_update2.log['error'].keys()), 0)
        self.assertEqual(len(ann_update2.new_instance_relations_list_no_ids), 1)

    def test_add_missing_ids_to_new_relations(self):
        """
            Tests calss to add_missing_ids_to_new_relations()
        :return:
        """
        file1 = data_mocking.create_file({'project_id': self.project.id, 'type': 'image'}, self.session)
        frame = data_mocking.create_file(
            {'project_id': self.project.id, 'type': 'frame', 'video_parent_file_id': file1.id, 'frame_number': 5},
            self.session)
        label_file = data_mocking.create_file({'project_id': self.project.id, 'type': 'label'}, self.session)
        # 2 Exactly equal instances
        self.project.label_dict['label_file_id_list'] = [label_file.id]
        instance1 = data_mocking.create_instance(
            {'x_min': 1,
             'x_max': 10,
             'y_min': 1,
             'y_max': 10,
             'file_id': file1.id,
             'label_file_id': label_file.id,
             'type': 'relation'
             },
            self.session
        )
        instance1.creation_ref_id = str(uuid.uuid4())
        instance2 = data_mocking.create_instance(
            {'x_min': 2,
             'x_max': 15,
             'y_min': 2,
             'y_max': 15,
             'file_id': file1.id,
             'label_file_id': label_file.id,
             'type': 'box'
             },
            self.session
        )
        relation = data_mocking.create_instance(
            {
                'file_id': file1.id,
                'label_file_id': None,
                'type': 'relation'
            },
            self.session
        )
        relation.hash_instance()
        old_hash = relation.hash

        instance2.creation_ref_id = str(uuid.uuid4())
        self.session.commit()
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            instance_list_new = [],
            file = file1,
            do_init_existing_instances = True
        )
        ann_update.new_added_instances = [instance1, instance2]
        ann_update.new_instance_relations_list_no_ids = [{'instance': relation,
                                                          'from_ref': instance1.creation_ref_id,
                                                          'to_ref': instance2.creation_ref_id}]
        ann_update.add_missing_ids_to_new_relations()

        self.assertEqual(relation.from_instance_id, instance1.id)
        self.assertEqual(relation.to_instance_id, instance2.id)
        self.assertNotEqual(old_hash, relation.hash)

    """
    ======================================================================================================================
    Everything below here is for large tests validation overall functionality (mainly annotation_update_main). 
    These all need to be heavily refactored, mocked and broken down.
    ======================================================================================================================
    """

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

        self.assertEqual(len(added_instances), 1)
        self.assertEqual(len(new_instance_list), 2)
        self.assertEqual(len(deleted_instances), 1)
        self.assertEqual(deleted_instances[0], newest_id)
        self.assertEqual(new_instance_list[0]['x_min'], inst_redone['x_min'])
        self.assertEqual(new_instance_list[0]['y_min'], inst_redone['y_min'])
        self.assertEqual(new_instance_list[0]['x_max'], inst_redone['x_max'])
        self.assertEqual(new_instance_list[0]['y_max'], inst_redone['y_max'])
        self.assertNotEqual(inst_redone['id'], new_instance_list[0]['id'])
        self.assertNotEqual(new_instance_list[0]['id'], deleted_id)
        self.assertFalse(new_instance_list[0]['soft_delete'])

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

    def test_create_instance_relation(self):
        """
            Tests creation of relation of type instance.
            Tests verifications of from_id to_id fields.
        :return:
        """
        file1 = data_mocking.create_file({'project_id': self.project.id, 'type': 'image'}, self.session)
        frame = data_mocking.create_file(
            {'project_id': self.project.id, 'type': 'frame', 'video_parent_file_id': file1.id, 'frame_number': 5},
            self.session)
        label_file = data_mocking.create_file({'project_id': self.project.id, 'type': 'label'}, self.session)
        # 2 Exactly equal instances
        self.project.label_dict['label_file_id_list'] = [label_file.id]
        ref1 = str(uuid.uuid4())
        ref2 = str(uuid.uuid4())
        inst1 = {
            'creation_ref_id': ref1,
            'x_min': 1,
            'y_min': 1,
            'x_max': 18,
            'y_max': 18,
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'box'
        }
        inst2 = {
            'creation_ref_id': ref2,
            'x_min': 1,
            'y_min': 1,
            'x_max': 54,
            'y_max': 54,
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'box'
        }
        relation = {
            'from_creation_ref': ref1,
            'to_creation_ref': ref2,
            'creation_ref_id': str(uuid.uuid4()),
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'relation'
        }
        instance_list = [inst1, inst2, relation]
        ann_update2 = Annotation_Update(
            session = self.session,
            project = self.project,
            instance_list_new = instance_list,
            file = file1,
            do_init_existing_instances = True
        )
        ann_update2.main()
        self.session.commit()
        new_instances = ann_update2.new_added_instances
        self.assertEqual(len(new_instances), 3)
        self.assertEqual(len(ann_update2.new_instance_relations_list_no_ids), 1)
        self.assertEqual(new_instances[2].type, 'relation')
        self.assertEqual(new_instances[2].from_instance_id, new_instances[0].id)
        self.assertEqual(new_instances[2].to_instance_id, new_instances[1].id)
        ## Test Adding Instances With IDs
        relation2 = {
            'from_instance_id': new_instances[1].id,
            'to_instance_id': new_instances[0].id,
            'creation_ref_id': str(uuid.uuid4()),
            'soft_delete': False,
            'label_file_id': label_file.id,
            'type': 'relation'
        }
        self.session.commit()
        instance_list = [new_instances[0].serialize_with_label(),
                         new_instances[1].serialize_with_label(),
                         new_instances[2].serialize_with_label(),
                         relation2]
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            instance_list_new = instance_list,
            file = file1,
            do_init_existing_instances = True
        )
        ann_update.main()
        new_instances2 = ann_update.new_added_instances
        self.assertEqual(len(new_instances2), 1)
        self.assertEqual(len(ann_update.new_instance_relations_list_no_ids), 0)
        self.assertEqual(new_instances2[0].type, 'relation')
        self.assertEqual(new_instances2[0].from_instance_id, new_instances[1].id)
        self.assertEqual(new_instances2[0].to_instance_id, new_instances[0].id)


    def test__saving_untouched_instance_list_does_not_restore(self):
        """
            We had a bug that whenever we resaved an instance and there where no changes
            we would mark the instance as restored even though we were not restoring anything.

            This was because we were not checking the is_new_instance flag in the
            __validate_user_deletion() function of shared/annotation.py

            This regression test case covers this bug
        :return:
        """
        """
            Sometimes default values can make the hash change after
            saving to DB. This test checks that is not happening.
        :return:
        """
        file1 = data_mocking.create_file({'project_id': self.project.id}, self.session)
        label_file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        self.project.label_dict['label_file_id_list'] = [label_file.id]
        # 1. Initial State 1 Unsaved Instance
        inst1 = {'type': 'box',
                 'file_id': file1.id,
                 'label_file_id': label_file.id,
                 'soft_delete': False,
                 'x_min': 10,
                 'y_min': 10,
                 'x_max': 28,
                 'y_max': 28,
                 'deletion_type': None,
                 'created_time': '2022-01-12T18:31:59.530816',
                 'action_type': 'created',
                 'deleted_time': None,
                 'change_source': None,
                 'p1': None,
                 'p2': None,
                 'cp': None,
                 'center_x': None,
                 'center_y': None,
                 'creation_ref_id': '10460e33-c02b-459d-a412-ab7b4512gdghf',
                 'number': None,
                 'interpolated': False,
                 'machine_made': False,
                 'model_id': None,
                 'model_run_id': None,
                 'sequence_id': None,
                 'front_face': None,
                 'rear_face': None,
                 'rating': None,
                 'attribute_groups': None,
                 'member_created_id': None,
                 'previous_id': None,
                 'next_id': None,
                 'root_id': 1,
                 'version': 1,
                 'nodes': [],
                 'edges': [],
                 'pause_object': None,
                 'label_file': {'id': 2, 'hash': None, 'type': 'image', 'state': 'added',
                                'created_time': '2022-01-12T18:31:59.508361', 'time_last_updated': None,
                                'ann_is_complete': None, 'original_filename': 'ykzwdu', 'video_id': None,
                                'video_parent_file_id': None, 'count_instances_changed': None,
                                'image': {'original_filename': None, 'width': None, 'height': None,
                                          'soft_delete': False, 'url_signed': None, 'url_signed_thumb': None,
                                          'annotation_status': None}}
                 }
        instance_list = [inst1]

        # 2. save the instance.
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            instance_list_new = instance_list,
            file = file1,
            do_init_existing_instances = True
        )
        ann_update.main()

        new_instance_list = [x.serialize_with_label() for x in ann_update.new_added_instances]
        self.session.commit()

        session2 = sessionMaker.session_factory()
        new_instance_list[0]['x_min'] += 10
        new_instance_list[0]['x_max'] += 10
        new_instance_list[0]['y_max'] += 10
        new_instance_list[0]['y_min'] += 10

        # 3. Move the instance and resave
        ann_update2 = Annotation_Update(
            session = session2,
            project = self.project,
            instance_list_new = new_instance_list,
            file = file1,
            do_init_existing_instances = True
        )
        ann_update2.main()
        self.assertEqual(len(ann_update2.new_added_instances), 1)

        instance_list_result = ann_update2.file.instance_list
        new_instance_list = [x.serialize_with_label() for x in instance_list_result]
        session2.commit()
        # 4. Resave with no changes
        ann_update2 = Annotation_Update(
            session = session2,
            project = self.project,
            instance_list_new = new_instance_list,
            file = file1,
            do_init_existing_instances = True
        )
        ann_update2.main()
        instance_list_result = ann_update2.file.instance_list

        self.assertEqual(len(instance_list_result), 2)
        self.assertEqual(len(ann_update2.new_added_instances), 0)
        self.assertNotEqual(instance_list_result[1].action_type, 'undeleted')

    def test_create_relation_no_ids(self):
        """
            Tests creating a relations with no IDS and only ref ids on the payload.
        :return:
        """
        file1 = data_mocking.create_file({'project_id': self.project.id, 'type': 'image'}, self.session)
        frame = data_mocking.create_file(
            {'project_id': self.project.id, 'type': 'frame', 'video_parent_file_id': file1.id, 'frame_number': 5},
            self.session)
        label_file = data_mocking.create_file({'project_id': self.project.id, 'type': 'label'}, self.session)
        self.project.label_dict['label_file_id_list'] = [label_file.id]

        instance_list = [
            {
                "id": None,
                "creation_ref_id": "b246ba1b-07fa-4680-9398-de7d323ee650",
                "label_file_id": label_file.id,
                "selected": False,
                "type": "text_token",
                "points": [],
                "soft_delete": False,
                "start_token": 72,
                "end_token": 72,
                "initialized": True,
                "text_tokenizer": "nltk"
            },
            {
                "id": None,
                "creation_ref_id": "221eea70-e0ba-433a-a5c5-851213b6ae66",
                "label_file_id": label_file.id,
                "type": "text_token",
                "points": [],
                "soft_delete": False,
                "start_token": 76,
                "end_token": 76,
                "initialized": True,
                "text_tokenizer": "nltk"
            },
            {
                "id": None,
                "creation_ref_id": "bb32076e-91bd-4d70-ac57-c1c115e6e43b",
                "label_file_id": label_file.id,
                "selected": False,
                "number": None,
                "type": "relation",
                "points": [],
                "sequence_id": None,
                "soft_delete": False,
                "from_instance_id": None,
                "to_instance_id": None,
                "initialized": True,
                "text_tokenizer": "nltk",
                "from_creation_ref": "b246ba1b-07fa-4680-9398-de7d323ee650",
                "to_creation_ref": "221eea70-e0ba-433a-a5c5-851213b6ae66"
            }
        ]

        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            instance_list_new = instance_list,
            file = file1,
            do_init_existing_instances = True
        )

        ann_update.main()

        self.assertEqual(len(ann_update.log['error'].keys()), 0)

    """
    Next 2 methods below are for testing hashing functionality
    """
    def test_hashing_algorithm_changes(self):
        """
            This case handles when the instance.hash() function changes, ie we add or remove
            an element for the hash creation. We check things like:

            - Avoid tracking this hash change and marking it as a system event.
            - Making sure this change is not attached to the user who saved the file
            - Avoiding the "restored" state on the instance history.
            - Checking overall instance history is valid.
        :return:
        """
        file1 = data_mocking.create_file({'project_id': self.project.id}, self.session)
        label_file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        self.project.label_dict['label_file_id_list'] = [label_file.id]
        # 1. Initial State 2 Saved Instances
        instance1 = data_mocking.create_instance(
            {'x_min': 1,
             'x_max': 10,
             'y_min': 1,
             'y_max': 10,
             'file_id': file1.id,
             'label_file_id': label_file.id,
             'type': 'box'
             },
            self.session
        )
        instance2 = data_mocking.create_instance(
            {'x_min': 2,
             'x_max': 15,
             'y_min': 2,
             'y_max': 15,
             'file_id': file1.id,
             'label_file_id': label_file.id,
             'type': 'box'
             },
            self.session
        )
        instance1.hash_instance()
        instance2.hash_instance()
        self.session.commit()
        instance_list = [x.serialize_with_label() for x in [instance1, instance2]]

        # 2. We Edit One Instance, the other one stays the same
        instance_list[1]['x_max'] = 25
        instance_list[1]['y_max'] = 25

        # 3. We change the hashing algorithm (with a mock)
        def dummy_hashing_algorithm(instance):
            hash_data = [
                instance.x_min,
                instance.x_max,
                instance.y_min,
                instance.y_max,
            ]

            instance.hash = hashlib.sha256(json.dumps(hash_data,
                                                      sort_keys = True).encode('utf-8')).hexdigest()

        with patch.object(Instance, 'hash_instance', dummy_hashing_algorithm):
            # 4. Re-save the instance.
            ann_update = Annotation_Update(
                session = self.session,
                project = self.project,
                instance_list_new = instance_list,
                file = file1,
                do_init_existing_instances = True
            )
            ann_update.main()
        # 5. Expect just one changed instance (Even though hasing algo changed, it was not a user edit).
        self.assertEqual(len(ann_update.new_added_instances), 1)

    def test_no_changes_in_hashes_by_default_values(self):
        """
            Sometimes default values can make the hash change after
            saving to DB. This test checks that is not happening.
        :return:
        """
        file1 = data_mocking.create_file({'project_id': self.project.id}, self.session)
        label_file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        self.project.label_dict['label_file_id_list'] = [label_file.id]
        # 1. Initial State 1 Unsaved Instance
        inst1 = {'id': 1,
                 'type': 'box',
                 'file_id': 1,
                 'label_file_id': 2,
                 'soft_delete': False,
                 'x_min': 10,
                 'y_min': 10,
                 'x_max': 28,
                 'y_max': 28,
                 'deletion_type': None,
                 'created_time': '2022-01-12T18:31:59.530816',
                 'action_type': 'created',
                 'deleted_time': None,
                 'change_source': None,
                 'p1': None,
                 'p2': None,
                 'cp': None,
                 'center_x': None,
                 'center_y': None,
                 'creation_ref_id': '10460e33-c02b-459d-a412-ab7b4512cc7c',
                 'width': 18,
                 'height': 18,
                 'number': None,
                 'interpolated': False,
                 'machine_made': False,
                 'model_id': None,
                 'model_run_id': None,
                 'sequence_id': None,
                 'front_face': None,
                 'rear_face': None,
                 'rating': None,
                 'attribute_groups': None,
                 'member_created_id': None,
                 'previous_id': None,
                 'next_id': None,
                 'root_id': 1,
                 'version': 1,
                 'nodes': [],
                 'edges': [],
                 'pause_object': None,
                 'label_file': {'id': 2, 'hash': None, 'type': 'image', 'state': 'added',
                                'created_time': '2022-01-12T18:31:59.508361', 'time_last_updated': None,
                                'ann_is_complete': None, 'original_filename': 'ykzwdu', 'video_id': None,
                                'video_parent_file_id': None, 'count_instances_changed': None,
                                'image': {'original_filename': None, 'width': None, 'height': None,
                                          'soft_delete': False, 'url_signed': None, 'url_signed_thumb': None,
                                          'annotation_status': None}}
                 }
        instance_list = [inst1]

        # 2. save the instance.
        ann_update = Annotation_Update(
            session = self.session,
            project = self.project,
            instance_list_new = instance_list,
            file = file1,
            do_init_existing_instances = True
        )
        ann_update.main()

        new_instance_list = [x.serialize_with_label() for x in ann_update.new_added_instances]
        self.session.commit()
        session2 = sessionMaker.session_factory()

        # 3. Re save with no changes
        ann_update2 = Annotation_Update(
            session = session2,
            project = self.project,
            instance_list_new = new_instance_list,
            file = file1,
            do_init_existing_instances = True
        )
        ann_update2.main()
        self.assertEqual(len(ann_update2.system_upgrade_hash_changes), 0)

    