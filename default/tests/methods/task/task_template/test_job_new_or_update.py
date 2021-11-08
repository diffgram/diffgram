from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from unittest.mock import patch
from methods.task.task_template import job_new_or_update


class TestJobNewUpdate(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestJobNewUpdate, self).setUp()
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
        self.auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        self.member = self.auth_api.member
        self.member.user = data_mocking.register_user({
            'username': 'test_user',
            'email': 'test@test.com',
            'password': 'diffgram123',
            'project_string_id': self.project.project_string_id,
            'member_id': self.member.id
        }, self.session)
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project,
            'allow_reviews': True
        }, self.session)

    def test_job_update_api(self):
        # Create mock job.
        job = data_mocking.create_job({
            'name': 'my-test-job'
        }, self.session)
        file = data_mocking.create_file({'project_id': job.project.id, 'job_id': job.id}, self.session)
        request_data = {
            'name': 'new name',
            'instance_type': 'polygon',
            'share_type': 'project',
            'reviewer_list_ids': [self.member.id],
            'type': 'exam',
            'label_file_list': [{'id': file.id}],
            'file_handling': 'isolate',
            'job_id': job.id,
        }

        endpoint = "/api/v1/project/" + job.project.project_string_id + "/job/update"
        credentials = b64encode("{}:{}".format(self.auth_api.client_id, self.auth_api.client_secret).encode()).decode('utf-8')
        response = self.client.post(
            endpoint,
            data=json.dumps(request_data),
            headers={
                'directory_id': str(job.project.directory_default_id),
                'Authorization': 'Basic {}'.format(credentials)
            }
        )
        self.assertEqual(response.status_code, 200)
        new_session = sessionMaker.session_factory()
        updated_job = Job.get_by_id(new_session, job.id)
        self.assertEqual(updated_job.name, request_data['name'])
        self.assertEqual(updated_job.instance_type, request_data['instance_type'])
        self.assertEqual(updated_job.share_type, request_data['share_type'])
        self.assertEqual(updated_job.type, request_data['type'])
        self.assertEqual(updated_job.file_handling, request_data['file_handling'])

    def test_new_web(self):
        # Create mock project/job.
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
        project = project_data['project']
        user = project_data['users'][0]
        file = data_mocking.create_file({'project_id': project.id}, self.session)
        request_data = {
            'name': 'new name',
            'instance_type': 'polygon',
            'share_type': 'project',
            'type': 'exam',
            'label_file_list': [{'id': file.id}],
            'file_handling': 'isolate',
            'member_list_ids': [user.member.id],
        }

        endpoint = "/api/v1/project/{}/job/new".format(project.project_string_id)
        auth_api = common_actions.create_project_auth(project=project, session=self.session)
        credentials = b64encode("{}:{}".format(auth_api.client_id, auth_api.client_secret).encode()).decode('utf-8')
        response = self.client.post(
            endpoint,
            data=json.dumps(request_data),
            headers={
                'directory_id': str(project.directory_default_id),
                'Authorization': 'Basic {}'.format(credentials)
            }
        )
        print(response.data)
        self.assertEqual(response.status_code, 200)
        new_session = sessionMaker.session_factory()
        updated_job = Job.get_by_id(new_session, response.json['job']['id'])
        self.assertEqual(updated_job.name, request_data['name'])
        self.assertEqual(updated_job.instance_type, request_data['instance_type'])
        self.assertEqual(updated_job.share_type, request_data['share_type'])
        self.assertEqual(updated_job.type, request_data['type'])
        self.assertEqual(updated_job.file_handling, request_data['file_handling'])

    def test_job_update_core(self):
        # Create mock job.
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
        project = project_data['project']
        job = data_mocking.create_job({
            'name': 'my-test-job',
            'project_id': project.id
        }, self.session)
        user = project_data['users'][0]
        input_data = {'name': 'my_new_name',
                      'share_type': 'project',
                      'permission': [],
                      'label_mode': '',
                      'passes_per_file': 1,
                      'instance_type': 'box',
                      'launch_datetime': datetime.datetime.now(),
                      'file_count': 0,
                      'file_handling': 0,
                      'label_file_list': [],
                      'member_list_ids': [user.member.id],
                      'type': '',
                      }
        log = {'error': {}, 'info': {}}
        with patch('methods.task.task_template.job_new_or_update.new_or_update_core',
                   return_value=('called!', {})) as mock_method:
            job.status = 'draft'
            job_new_or_update.job_update_core(
                self.session,
                job,
                job.project,
                input_data,
                log
            )
            mock_method.assert_called_once()
        job.status = 'launched'
        job_new_or_update.job_update_core(
            self.session,
            job,
            job.project,
            input_data,
            log
        )
        new_session = sessionMaker.session_factory()
        updated_job = Job.get_by_id(self.session, job.id)
        self.assertEqual(updated_job.name, input_data['name'])
        self.assertEqual(updated_job.label_dict['label_file_list'], input_data['label_file_list'])

    def test_update_tasks(self):
        job = data_mocking.create_job({
            'name': 'my-test-job'
        }, self.session)
        task_1 = data_mocking.create_task({
            'name': 'task1',
            'job': job
        }, self.session)
        task_2 = data_mocking.create_task({
            'name': 'task2',
            'job': job
        }, self.session)
        self.session.commit()
        test_dict = {
            'test': {},
            'test_2': {},
            'test_3': {},
        }
        job.label_dict = test_dict
        log = {'error': {}, 'info': {}}
        job_new_or_update.update_tasks(job, self.session, log)
        self.session.commit()
        task1_updated = Task.get_by_id(self.session, task_1.id)
        task2_updated = Task.get_by_id(self.session, task_2.id)
        self.assertEqual(task1_updated.label_dict, test_dict)
        self.assertEqual(task2_updated.label_dict, test_dict)

    def test_build_label_file_list(self):
        project_data1 = data_mocking.create_project_with_context(
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
        project1 = project_data1['project']
        project_data2 = data_mocking.create_project_with_context(
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
        project2 = project_data2['project']

        file = data_mocking.create_file({
            'project_id': project1.id
        }, self.session)
        with self.assertRaises(Forbidden):
            job_new_or_update.build_label_file_list(
                [{'id': file.id}],
                self.session,
                project2
            )
        file_ids = job_new_or_update.build_label_file_list(
            [{'id': file.id}],
            self.session,
            project1
        )
        self.assertEqual(file_ids, [file.id])

    def test_new_or_update_core(self):
        log = {'error': {}, 'info': {}}
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
        project = project_data['project']
        job_name = data_mocking.get_random_string(8)
        now = datetime.datetime.now()
        # Testing job creation
        new_job, log_result = job_new_or_update.new_or_update_core(
            self.session,
            log=log,
            member=None,
            project=project,
            name=job_name,
            share='project',
            permission='all_secure_users',
            label_mode='closed_all_available',
            passes_per_file=1,
            instance_type='box',
            launch_datetime=now,
            file_count=0,
            label_file_list=[],
            file_handling='isolate',
            job_type='exam',
            job=None
        )
        self.assertEqual(new_job.project, project)
        self.assertEqual(new_job.name, job_name)
        self.assertEqual(new_job.share_type, 'project')
        self.assertEqual(new_job.permission, 'all_secure_users')
        self.assertEqual(new_job.label_mode, 'closed_all_available')
        self.assertEqual(new_job.passes_per_file, 1)
        self.assertEqual(new_job.instance_type, 'box')
        self.assertEqual(new_job.launch_datetime, now)
        self.assertEqual(new_job.file_count, 0)
        self.assertEqual(new_job.label_dict['label_file_list'], [])
        self.assertEqual(new_job.file_handling, 'isolate')
        self.assertEqual(new_job.type, 'exam')
        # Now testing job update
        new_name = 'a new name'
        file = data_mocking.create_file({
            'project_id': project.id
        }, self.session)
        updated_job, log_result = job_new_or_update.new_or_update_core(
            self.session,
            log=log,
            member=None,
            project=project,
            name=new_name,
            share='market',
            permission='Only me',
            label_mode='closed_and_split_one_label_per_task',
            passes_per_file=859,
            instance_type='polygon',
            launch_datetime=now,
            file_count=23,
            label_file_list=[{'id': file.id}],
            file_handling='use_existing',
            job_type='normal',
            job=new_job
        )
        self.assertEqual(updated_job.project, project)
        self.assertEqual(updated_job.name, new_name)
        self.assertEqual(updated_job.share_type, 'market')
        self.assertEqual(updated_job.permission, 'Only me')
        self.assertEqual(updated_job.label_mode, 'closed_and_split_one_label_per_task')
        self.assertEqual(updated_job.passes_per_file, 859)
        self.assertEqual(updated_job.instance_type, 'polygon')
        self.assertEqual(updated_job.launch_datetime, now)
        self.assertEqual(updated_job.file_count, 23)
        self.assertEqual(updated_job.label_dict['label_file_list'], [file.id])
        self.assertEqual(updated_job.file_handling, 'use_existing')
        self.assertEqual(updated_job.type, 'normal')
        self.assertTrue('task_count' in log_result['info'])
        self.assertTrue('share_type' in log_result['info'])
        self.assertTrue('name' in log_result['info'])
        self.assertTrue('file_count' in log_result['info'])
        self.assertTrue('permission' in log_result['info'])
        self.assertTrue('label_mode' in log_result['info'])
        self.assertTrue('passes_per_file' in log_result['info'])
        self.assertTrue('instance_type' in log_result['info'])
        self.assertTrue('file_handling' in log_result['info'])
        self.assertTrue('file_handling' in log_result['info'])

    def test_update_output_dir_actions(self):
        # Create mock job.
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
        project = project_data['project']
        job = data_mocking.create_job({
            'name': 'my-test-job',
            'project': project
        }, self.session)

        directory = data_mocking.create_directory({
            'project': project,
            'user': project_data['users'][0],
        }, self.session)
        input_data = {'output_dir': directory.id,
                      'output_dir_action': 'copy',
                      'job_id': job.id,
                      }
        log = {'error': {}, 'info': {}}
        updated_job, log = job_new_or_update.update_output_dir_actions(
            self.session,
            job,
            job.project,
            input_data,
            log
        )
        self.session.commit()
        self.session.flush()
        self.assertEqual(updated_job.output_dir_action, input_data['output_dir_action'])
        self.assertEqual(updated_job.completion_directory_id, input_data['output_dir'])

    def test_job_output_dir_update(self):
        # Create mock job.
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
        project = project_data['project']
        job = data_mocking.create_job({
            'name': 'my-test-job',
            'project': project
        }, self.session)
        directory = data_mocking.create_directory({
            'project': project,
            'user': project_data['users'][0],
        }, self.session)
        file = data_mocking.create_file({'project_id': job.project.id, 'job_id': job.id}, self.session)
        request_data = {
            'output_dir': str(directory.id),
            'output_dir_action': 'copy',
            'job_id': job.id,
        }

        endpoint = "/api/v1/project/" + job.project.project_string_id + "/job/set-output-dir"
        auth_api = common_actions.create_project_auth(project=job.project, session=self.session)
        credentials = b64encode("{}:{}".format(auth_api.client_id, auth_api.client_secret).encode()).decode('utf-8')
        response = self.client.post(
            endpoint,
            data=json.dumps(request_data),
            headers={
                'directory_id': str(job.project.directory_default_id),
                'Authorization': 'Basic {}'.format(credentials)
            }
        )
        self.assertEqual(response.status_code, 200)
        new_session = sessionMaker.session_factory()
        updated_job = Job.get_by_id(new_session, job.id)
        self.assertEqual(updated_job.output_dir_action, request_data['output_dir_action'])
        self.assertEqual(str(updated_job.completion_directory_id), request_data['output_dir'])
        # Now test a wrong action
        request_data_error = {
            'output_dir': 58,
            'output_dir_action': 'a_wrong_action',
            'job_id': job.id,
        }
        response_error = self.client.post(
            endpoint,
            data=json.dumps(request_data_error),
            headers={
                'directory_id': str(job.project.directory_default_id),
                'Authorization': 'Basic {}'.format(credentials)
            }
        )
        self.assertEqual(response_error.status_code, 400)
