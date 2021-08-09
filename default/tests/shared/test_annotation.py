from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.annotation import Annotation_Update


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

    def test__check_all_instances_available_in_new_instance_list(self):
        file1 = data_mocking.create_file({'project_id': self.project.id}, self.session)
        label_file = data_mocking.create_file({'project_id': self.project.id}, self.session)
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

        self.assertFalse(result)
        self.assertTrue(len(ann_update.log['error'].keys()) > 0)
        self.assertTrue('new_instance_list_missing_ids' in ann_update.log['error'])
        self.assertTrue('information' in ann_update.log['error'])
        self.assertTrue('missing_ids' in ann_update.log['error'])
        self.assertTrue(instance2.id in ann_update.log['error']['missing_ids'])
        self.assertTrue(instance3.id in ann_update.log['error']['missing_ids'])


        # Now test case with validations and a wrong payload and some existing deleted instances
        instance4 = data_mocking.create_instance(
            {'x_min': 1, 'x_max': 10, 'y_min': 1, 'y_max': 10, 'file_id': file1.id, 'soft_delete': True, 'label_file_id': label_file.id},
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

        self.assertFalse(result)
        self.assertTrue(len(ann_update.log['error'].keys()) > 0)
        self.assertTrue('new_instance_list_missing_ids' in ann_update.log['error'])
        self.assertTrue('information' in ann_update.log['error'])
        self.assertTrue('missing_ids' in ann_update.log['error'])
        self.assertTrue(instance2.id in ann_update.log['error']['missing_ids'])
        self.assertTrue(instance3.id in ann_update.log['error']['missing_ids'])
        self.assertTrue(instance4.id not in ann_update.log['error']['missing_ids'])
