# OPENCORE - ADD
from methods.regular.regular_api import *
from shared.database.source_control.working_dir import WorkingDir
from dataclasses import dataclass
from shared.database.task.job.job_working_dir import JobWorkingDir
from sqlalchemy.orm import Session
from methods.input.packet import enqueue_packet
from shared.database.input import Input
from shared.database.label import Label
from methods.input.process_media import Process_Media
from shared.utils.job_dir_sync_utils import JobDirectorySyncManager
from shared.regular.regular_methods import commit_with_rollback
from shared.utils.job_launch_utils import task_template_label_attach
from shared.utils.source_control.file.file_transfer_core import file_transfer_core
import random
import uuid
import uuid
from shared.regular import regular_log

data_gen_spec_list = [
    {
        'data_type': {
            'default': 'dataset',
            'kind': str,
            'required': False
        },

    },
    {
        'dataset_id': {
            'default': None,
            'kind': int,
            'required': False
        },
    },
    {
        'structure': {
            'default': None,
            'kind': str,
            'required': False,
            'valid_values_list': ['1_pass', '2_pass', '2_input_1_output']
        }
    },
    {
        'num_files': {
            'default': 3,
            'kind': int,
            'required': False
        }
    },
    {
        'reviews': {
            'allow_reviews': {
                'kind': bool,
                'default': False,
                'required': False
            },
            'review_chance': {
                'kind': float,
                'default': 0,
                'required': False
            }
        }
    }
]

@routes.route('/api/walrus/v1/project/<string:project_string_id>/gen-data', 
              methods=['POST'])
@Project_permissions.user_has_project(["admin", "Editor"])
def generate_data_api(project_string_id):

    log, input, untrusted_input = regular_input.master(
        request=request, spec_list=data_gen_spec_list)
    if regular_log.log_has_error(log): return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        project = Project.get(session, project_string_id)
        shared_data_gen(session, project, input)

    return jsonify({'message': 'OK.'})



@routes.route('/api/walrus/v1/new_project/gen-data', 
              methods=['POST'])
@General_permissions.grant_permission_for(
    Roles=['normal_user'],
    apis_user_list=["builder_or_trainer"])
def generate_data_new_project_api():

    with sessionMaker.session_scope() as session:
        user = User.get(session=session)
        data_mocker.generate_sample_project(user=user)
    return jsonify({'message': 'OK.'})



@routes.route('/api/walrus/test/gen-data', methods = ['POST'])
def mock_generate_data_api():
    if settings.DIFFGRAM_SYSTEM_MODE not in ['testing_e2e', 'testing', 'sandbox']:
        return jsonify(message='Invalid System Mode'), 403

    log, input, untrusted_input = regular_input.master(
        request=request, spec_list=data_gen_spec_list)
    if regular_log.log_has_error(log): return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        project = Project.get(session, "diffgram-testing-e2e")
        shared_data_gen(session, project, input)

        out = jsonify(success = True)

        return out, 200


def shared_data_gen(session, project, input):
    data_mocker = DiffgramDataMocker(session=session)
    if input['data_type'] == 'dataset':
        dataset = WorkingDir.get(session=session,
                                    directory_id=input['dataset_id'], 
                                    project_id=project.id)
        data_mocker.generate_test_data_on_dataset(dataset=dataset)
        
    elif input['data_type'] == 'label':
        data_mocker.generate_sample_label_files(project=project)

    elif input['data_type'] == 'task_template':
        data_mocker.generate_test_data_for_task_templates(
            project=project, structure=input.get('structure'), num_files=input.get('num_files'), reviews=input.get('reviews'), member=get_member(session))
        
    elif input['data_type'] == 'annotations':
        task_list = Task.list(session = session, project_id=project.id, limit_count=100)
        label_file_list = WorkingDirFileLink.file_list(
            session=session,
            working_dir_id=project.directory_default_id,
            limit=1,
            type="label"
        )
        data_mocker.generate_instance_many(task_list, label_file_list, member_created_id = get_member(session).id)


@dataclass
class DiffgramDataMocker:
    session: Session

    NUM_IMAGES = 3

    def generate_test_data_on_dataset(self, dataset, num_files=NUM_IMAGES):
        inputs_data = []
        for i in range(0, num_files):
            diffgram_input = enqueue_packet(
                project_string_id=dataset.project.project_string_id,
                session=self.session,
                media_url='https://picsum.photos/1000',
                media_type='image',
                original_filename="example.jpg",
                directory_id=dataset.id,
                commit_input=True,
                task_id=None,
                type='from_url',
                task_action=None,
                external_map_id=None,
                external_map_action=None,
                enqueue_immediately=True,
                mode=None,
                allow_duplicates=True)

            inputs_data.append(diffgram_input)
        return inputs_data



    def generate_instance_many(self, task_list, label_file_list, member_created_id=1, count_per_task=100):

        label_file_id = label_file_list[0].id

        print(len(task_list))
        for task in task_list:
            print(task.id, task.project_id)
            for i in range(count_per_task):
                self.generate_instance(task, member_created_id, instance_type="box", label_file_id=label_file_id)

        print("Complete")

    def generate_instance(self, task, member_created_id, instance_type, label_file_id):

        new_instance = Instance(
            file_id=task.file_id,
            sequence_id=None,   #  Different
            project_id=task.project_id,
            task_id=task.id,
            member_created_id=member_created_id,
            x_min=random.randint(0, 100),
            y_min=random.randint(0, 100),
            x_max=random.randint(200, 300),
            y_max=random.randint(200, 400),
            width=None,
            height=None,
            label_file_id=label_file_id,
            hash=None,
            type=instance_type,
            number=None,
            frame_number=None,
            global_frame_number = None,
            machine_made=None,
            points=None,
            soft_delete=False,
            center_x = None,
            center_y = None,
            angle = None,
            p1 = None,
            p2 = None,
            cp = None,
            interpolated = None,
            front_face = None,
            rear_face = None,
            creation_ref_id = None
        )
        self.session.add(new_instance)

    def generate_test_data_on_dataset_copy_file(self, dataset, num_files=NUM_IMAGES):

        mock_dir_name = '$$_diffgram_working_dir_mock_dataset'
        mock_dataset = self.session.query(WorkingDir).filter(
            WorkingDir.nickname == mock_dir_name
        ).first()
        if mock_dataset is None:
            project = Project()
            self.session.add(project)
            self.session.flush()
            print(project)
            mock_dataset = WorkingDir.new_blank_directory(
                self.session, project_id=project.id, nickname=mock_dir_name)
            self.generate_test_data_on_dataset(dataset=mock_dataset, num_files=num_files)

        elif num_files > self.NUM_IMAGES:
            print("gen new ones")
            self.generate_test_data_on_dataset(dataset=mock_dataset, num_files=num_files)

        files_list = WorkingDirFileLink.file_list(
            self.session,
            working_dir_id=mock_dataset.id,
            root_files_only=True,
            limit=num_files,
        )

        for file in files_list:
            new_file = file_transfer_core(
                session=self.session,
                source_directory=mock_dataset,
                destination_directory=dataset,
                transfer_action='copy',
                copy_instances=False,
                update_project_for_copy=True,
                file=file,
                log=regular_log.default(),
                sync_event_manager=None,
                log_sync_events=False,
                defer_copy = False
            )
            # Change the file project to the new project of the mock dataset
            file_id = new_file['info']['new_file'][0]['id']
            file = File.get_by_id(self.session, file_id)
            file.project = dataset.project
            self.session.add(file)


    def generate_sample_label_files(self, project):
        NUM_LABELS = 3
        label_files = []
        default_dir = self.session.query(WorkingDir).filter(WorkingDir.nickname == 'Default',
                                                            WorkingDir.project_id == project.id).first()
        if default_dir is None:
            # Fallback to default directory on project.
            default_dir = project.directory_default

        rand_int_0_255 = lambda: random.randint(0, 255)
        for i in range(0, NUM_LABELS):
            r = rand_int_0_255()    # red
            g = rand_int_0_255()    # green
            b = rand_int_0_255()    # blue
            random_color = '#%02X%02X%02X' % (r, g, b)
            colour = {
                "a": 1,
                "hex": random_color,
                "rgba" : {
                    'r' : r,
                    'g' : g,
                    'b' : b,
                    'a' : 1     # alpha
                    }
            }

            label_name = 'Diffgram Sample Label {}'.format(i + 1)
            label = self.session.query(Label).filter(
                Label.name == label_name,
                Label.default_sequences_to_single_frame == False
            ).first()
            if label:
                existing_label_file = self.session.query(File).join(WorkingDirFileLink).filter(
                    File.type == "label",
                    WorkingDirFileLink. working_dir_id == default_dir.id,
                    File.label_id == label.id,
                    File.project_id == project.id,
                    File.state != 'removed'
                ).first()
                if existing_label_file:
                    label_files.append(existing_label_file)
                    continue
            label_file = File.new_label_file(
                session=self.session,
                working_dir_id=default_dir.id,
                name=label_name,
                colour=colour,
                project=project
            )

            if project.directory_default.label_file_colour_map is None:
                project.directory_default.label_file_colour_map = {}

            project.directory_default.label_file_colour_map[label_file.id] = colour

            label_files.append(label_file)
        return label_files

    def generate_sample_dataset(self, nickname, project):
        existing_dir = self.session.query(WorkingDir).filter(
            WorkingDir.nickname == nickname,
            WorkingDir.project_id == project.id
        ).first()
        if existing_dir:
            return existing_dir, True
        
        # Reusing new blank directory.
        working_dir = WorkingDir.new_blank_directory(
            session = self.session,
            project = project,
            project_id=project.id,
            nickname=nickname
        )

        self.session.add(working_dir)
        self.session.flush()

        Project_Directory_List.add(
            session=self.session,
            working_dir_id=working_dir.id,
            project_id=project.id,
            nickname=nickname
        )

        project.set_cache_key_dirty('directory_list')
        self.session.add(project)

        return working_dir, False

    def generate_sample_files_for_dataset(self, dataset):
        NUM_IMAGES = 3
        NUM_VIDEOS = 3
        files_list_count = WorkingDirFileLink.file_list(
            self.session,
            working_dir_id=dataset.id,
            root_files_only=True,  # TODO do we need to get child files too?
            limit=None,
            counts_only=True,
            type=['image', 'video']
        )
        if files_list_count >= NUM_IMAGES:
            return
        for i in range(0, NUM_IMAGES):
            diffgram_input = Input(
                project_id=dataset.project_id,
                url='https://picsum.photos/1000',
                media_type='image',
                directory_id=dataset.id,
                type='from_url'

            )
            self.session.add(diffgram_input)
            self.session.flush()
            process_media = Process_Media(
                session=self.session,
                input_id=diffgram_input.id,
                input=diffgram_input,
                item=None
            )
            process_media.main_entry()
        # Commit right away for future querying.
        commit_with_rollback(self.session)

    def create_tasks_for_sample_task_template(self, task_template, attached_dir=None, files=None):
        if not files:
            files = WorkingDirFileLink.file_list(
                self.session,
                working_dir_id=attached_dir.id,
                root_files_only=True,  # TODO do we need to get child files too?
                limit=None,
                type='image'
            )

        job_sync_manager = JobDirectorySyncManager(
            session=self.session,
            job=task_template,
            log=regular_log.default(),
            directory = attached_dir
        )

        job_sync_manager.create_file_links_for_attached_dirs(create_tasks=True)
        return files

    def __create_sample_task_template(self, name, project, reviews, member = None):
        user = None
        if member:
            user = User.get_by_member_id(self.session, member_id = member.id)
        task_template = Job()
        task_template.name = name
        task_template.permission = 'all_secure_users'
        task_template.project_id = project.id
        task_template.instance_type = 'box'
        task_template.stat_count_tasks = 0
        task_template.label_mode = 'closed_all_available'
        task_template.stat_count_complete = 0
        task_template.allow_reviews = reviews['allow_reviews']
        task_template.review_chance = reviews['review_chance']
        directory = WorkingDir.new_blank_directory(session=self.session)
        task_template.directory = directory
        label_files = self.generate_sample_label_files(project=project)
        task_template.label_dict = {
            'label_file_list': [x.serialize_with_label_and_colour(self.session)['id'] for x in label_files]
        }
        if user:
            task_template.update_reviewer_list(session = self.session, reviewer_list_ids = [user.id], log = regular_log.default())
            task_template.update_member_list(session = self.session, member_list_ids = [user.id], log = regular_log.default())

        task_template.status = 'active'
        self.session.add(task_template)
        self.session.flush()
        task_template_label_attach(self.session, task_template)
        return task_template

    def generate_sample_project(self, user=None):
        n = str(uuid.uuid4())
        project = Project.new(session=self.session,
                              name='Diffgram Sample Project',
                              project_string_id='sample_project_{}'.format(n),
                              goal='testing',
                              user=user,
                              member_created=user.member,
                              )
        self.generate_test_data_for_task_templates(project, structure='1_pass')


    def generate_test_data_for_task_templates(self, project, structure='1_pass', num_files=NUM_IMAGES, reviews={
            "allow_reviews": False,
            "review_chance": 0
        }, member = None):

        if structure == '1_pass':
            task_template = self.__create_sample_task_template('Sample Task Template [Diffgram]', project, reviews, member)
            # Try to get the default dataset.
            input_dir, input_dir_exists = self.generate_sample_dataset('Pending [1st pass] ' + str(time.time())[-5:], project=project)

            if not input_dir_exists:
                self.generate_test_data_on_dataset_copy_file(input_dir, num_files)

            output_dir, output_dir_exists = self.generate_sample_dataset('Completed [1st pass]', project=project)
            task_template.output_dir_action = 'copy'
            task_template.completion_directory = output_dir
            rel_input = JobWorkingDir(
                working_dir_id=input_dir.id,
                job_id=task_template.id
            )
            self.session.add(task_template)
            self.session.add(rel_input)
            self.session.flush()
            self.create_tasks_for_sample_task_template(task_template, attached_dir=input_dir)
        elif structure == '2_pass':
            for i in range(0, 2):
                task_template = self.__create_sample_task_template('Sample Task Template {} pass'.format(i + 1),
                                                                   project, reviews, member)
                # Try to get the default dataset.
                if i == 0:
                    input_dir, input_dir_exists = self.generate_sample_dataset('Pending [{} pass]'.format(i + 1),
                                                                               project=project)
                    if not input_dir_exists:
                        self.generate_test_data_on_dataset_copy_file(input_dir)
                else:
                    input_dir, input_dir_exists = self.generate_sample_dataset('Completed [{} pass]'.format(i),
                                                                               project=project)

                output_dir, output_dir_exists = self.generate_sample_dataset('Completed [{} pass]'.format(i + 1),
                                                                             project=project)
                task_template.output_dir_action = 'copy'
                task_template.completion_directory = output_dir
                rel_input = JobWorkingDir(
                    working_dir_id=input_dir.id,
                    job_id=task_template.id
                )
                self.session.add(task_template)
                self.session.add(rel_input)
                self.session.flush()
                self.create_tasks_for_sample_task_template(task_template, attached_dir=input_dir)
        elif structure == '2_input_1_output':
            task_template = self.__create_sample_task_template('Sample 2 Input Task Template', project, reviews, member)
            # Try to get the default dataset.
            input_dir, input_dir_exists = self.generate_sample_dataset('Input Dataset 1', project=project)
            input2_dir, input2_dir_exists = self.generate_sample_dataset('Input Dataset 2', project=project)
            if not input_dir_exists:
                self.generate_test_data_on_dataset_copy_file(input_dir)
            if not input2_dir_exists:
                self.generate_test_data_on_dataset_copy_file(input2_dir)

            output_dir, output_dir_exists = self.generate_sample_dataset('Completed', project=project)
            task_template.output_dir_action = 'copy'
            task_template.completion_directory = output_dir
            rel_input = JobWorkingDir(
                working_dir_id=input_dir.id,
                job_id=task_template.id
            )
            rel_input2 = JobWorkingDir(
                working_dir_id=input2_dir.id,
                job_id=task_template.id
            )
            self.session.add(task_template)
            self.session.add(rel_input)
            self.session.add(rel_input2)
            self.session.flush()
            self.create_tasks_for_sample_task_template(task_template, attached_dir=input_dir)
        else:
            raise Exception('Invalid structure name')
