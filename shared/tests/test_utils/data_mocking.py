from shared.regular import regular_methods
from shared.database.project import Project
from shared.database import hashing_functions
from shared.database.user import User
from shared.database.source_control.working_dir import WorkingDir, WorkingDirFileLink
from shared.permissions.project_permissions import Project_permissions
from shared.database.source_control.file import File
from shared.database.annotation.instance import Instance
from shared.database.label import Label
from shared.database.event.event import Event
from shared.settings import settings
from shared.database.task.task import Task
import random
import string
from shared.database.sync_events.sync_event import SyncEvent
from shared.database.task.job.job import Job
from shared.database.system_events.system_events import SystemEvents
from shared.database.task.job.job_launch import JobLaunchQueue, JobLaunch
from shared.database.task.job.job_working_dir import JobWorkingDir
from shared.database.connection.connection import Connection
from shared.database.discussion.discussion import Discussion
from shared.database.discussion.discussion_comment import DiscussionComment
from shared.database.discussion.discussion_relation import DiscussionRelation
from shared.database.task.task_event import TaskEvent
import datetime
from shared.database.auth.member import Member
from shared.database.annotation.instance_template import InstanceTemplate
from shared.database.annotation.instance_template_relation import InstanceTemplateRelation
from shared.database.video.video import Video
from shared.database.image import Image
from shared.database.export import Export
from shared.database.video.sequence import Sequence

# This line is to prevent developers to run test in other databases or enviroments. We should rethink how to handle
# configuration data for the different deployment phases (local, testing, staging, production)
if settings.DIFFGRAM_SYSTEM_MODE != 'testing':
    raise Exception('DIFFGRAM_SYSTEM_MODE must be in "testing" mode to perform any kind of test')


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def register_member(user, session):
    new_member = Member(
        user = user
    )
    session.add(new_member)
    regular_methods.commit_with_rollback(session)
    return new_member


def register_user(user_data, session):
    """

    :param user_data:
        Example
        user_data={
            'username': 'test_user',
            'email': 'test@test.com',
            'password': 'diffgram123',
            'project_string_id': 'myproject'

        }
    :return:
    """
    # User registration
    password_hash = hashing_functions.make_password_hash(
        user_data['email'],
        user_data['password'])

    # TODO could insert logic here to attach a user to a project based on say the sigup code
    # ie signup_code.something?

    username = user_data['username']
    user_email = user_data['email']

    new_user = User(
        email = user_email,
        password_hash = password_hash,
        username = username,
        api_enabled_builder = True,
        api_enabled_trainer = True,
        security_email_verified = True,
        last_builder_or_trainer_mode = 'builder',
        permissions_general = {'general': ['normal_user']}

    )

    new_user.permissions_projects = {}  # I don't like having this here but alternative of committing object seems worse
    session.add(new_user)

    if 'project_string_id' in user_data:
        new_user.current_project_string_id = user_data['project_string_id']
        project = Project.get(session, user_data['project_string_id'])
        if project is not None:
            new_user.projects.append(project)
            new_user_working_dir = WorkingDir.new_user_working_dir(
                session,
                None,
                project,
                new_user
            )

            permission_result, permission_error = Project_permissions.add(user_data['project_string_id'],
                                                                          new_user,
                                                                          user_data['project_string_id'])
    return new_user


def create_event(event_data, session):
    event = Event(
        kind = event_data.get('kind'),
        member_id = event_data.get('member_id'),
        success = event_data.get('success'),
        error_log = event_data.get('error_log'),
        description = event_data.get('description'),
        link = event_data.get('link'),
        project_id = event_data.get('project_id'),
        task_id = event_data.get('task_id'),
        job_id = event_data.get('job_id'),
        run_time = event_data.get('run_time'),
        object_type = event_data.get('object_type'),
        input_id = event_data.get('input_id'),
        file_id = event_data.get('file_id'),
        page_name = event_data.get('page_name'),
    )
    session.add(event)
    regular_methods.commit_with_rollback(session)
    return event


def create_sequence(sequence_data, session):
    sequence = Sequence(
        label_file_id = sequence_data.get('label_file_id'),
        has_changes = sequence_data.get('has_changes'),
        single_frame = sequence_data.get('single_frame'),
        keyframe_list = sequence_data.get('keyframe_list'),
        video_file_id = sequence_data.get('video_file_id'),
        number = sequence_data.get('number'),
        instance_preview_cache = sequence_data.get('instance_preview_cache'),
        cache_expiry = sequence_data.get('cache_expiry'),
        archived = sequence_data.get('archived'),
    )
    session.add(sequence)
    regular_methods.commit_with_rollback(session)
    return sequence


def create_userscript(event_data, session):
    from shared.database.userscript.userscript import UserScript
    event = UserScript.new(
        member = event_data.get('member'),
        project = event_data.get('project'),
        client_created_time = event_data.get('client_created_time'),
        client_creation_ref_id = event_data.get('client_creation_ref_id'),
        name = event_data.get('name'),
        code = event_data.get('code'),
        external_src_list = event_data.get('external_src_list'),
        use_instructions = event_data.get('use_instructions'),
        language = event_data.get('language')
    )
    session.add(event)
    regular_methods.commit_with_rollback(session)
    return event


def create_task_event(task_event_data: dict, session: 'Session'):
    task_event = TaskEvent(
        project_id = task_event_data.get('project_id'),
        job_id = task_event_data.get('job_id'),
        task_id = task_event_data.get('task_id'),
        event_type = task_event_data.get('event_type'),
        member_created_id = task_event_data.get('member_created_id'),
    )
    session.add(task_event)
    regular_methods.commit_with_rollback(session)
    return task_event


def create_directory(dir_data, session):
    working_dir = WorkingDir()
    working_dir.user_id = dir_data['user'].id
    working_dir.project_id = dir_data['project'].id
    if dir_data.get('jobs_to_sync'):
        working_dir.jobs_to_sync = dir_data.get('jobs_to_sync')
    session.add(working_dir)
    regular_methods.commit_with_rollback(session)
    if dir_data.get('files'):
        file_list = dir_data.get('files')
        for file in file_list:
            WorkingDirFileLink.add(session, working_dir.id, file)
    regular_methods.commit_with_rollback(session)
    return working_dir


def create_instance_template(instance_template_data, session):
    instance_template = InstanceTemplate(
        name = instance_template_data.get('name', ''),
        project_id = instance_template_data.get('project_id'),
        status = instance_template_data.get('status')
    )
    session.add(instance_template)
    regular_methods.commit_with_rollback(session)
    if instance_template_data.get('instance_list', None):
        for instance in instance_template_data.get('instance_list'):
            new_instance = create_instance(
                instance_data = instance,
                session = session
            )
            rel = InstanceTemplateRelation(
                instance_template_id = instance_template.id,
                instance_id = new_instance.id
            )
            session.add(rel)
    regular_methods.commit_with_rollback(session)
    return instance_template


def create_file(file_data, session):
    file = File(
        project_id = file_data.get('project_id'),
        job_id = file_data.get('job_id'),
        original_filename = file_data.get('original_filename', get_random_string(6)),
        type = file_data.get('type', 'image'),
        state = file_data.get('state', 'added'),
        frame_number = file_data.get('frame_number'),
        video_parent_file_id = file_data.get('video_parent_file_id'),
    )
    file.type = file_data.get('type', 'image')
    if file.type == 'video':
        video = Video(
            filename = file_data.get('video', {'name': 'test video'}).get('name'),
            frame_rate = file_data.get('video', {'frame_rate': 60}).get('frame_rate'),
            frame_count = file_data.get('video', {'frame_count': 100}).get('frame_count'),
            width = file_data.get('video', {'width': 800}).get('width'),
            height = file_data.get('video', {'height': 800}).get('height'),
            parent_video_split_duration = 30,
            root_blob_path_to_frames = '/test/',
        )
        session.add(video)
        regular_methods.commit_with_rollback(session)
        file.video = video
        file.video_parent_file_id = video.id
    elif file.type in ['image', 'frame']:
        image = Image()
        session.add(image)
        regular_methods.commit_with_rollback(session)
        file.image = image
        file.image_id = image.id
    session.add(file)
    regular_methods.commit_with_rollback(session)
    return file


def create_job_launch(job_launch_data, session):
    job_launch = JobLaunch()
    job_launch.job_id = job_launch_data['job_id']
    session.add(job_launch)
    regular_methods.commit_with_rollback(session)
    return job_launch


def create_job_launch_queue_element(job_launch_queue_data, session):
    job_launch_queue = JobLaunchQueue()
    job_launch_queue.job_launch_id = job_launch_queue_data['job_launch_id']
    session.add(job_launch_queue)
    regular_methods.commit_with_rollback(session)
    return job_launch_queue


def create_connection(connection_data, session):
    connection = Connection()
    connection.name = connection_data['name']
    connection.integration_name = connection_data['integration_name']
    connection.project_id = connection_data['project_id']
    session.add(connection)
    regular_methods.commit_with_rollback(session)
    return connection


def new_system_event(system_event_data, session):
    system_event = SystemEvents(
        kind = system_event_data.get('kind'),
        description = system_event_data.get('description'),
        install_fingerprint = system_event_data.get('install_fingerprint'),
        previous_version = system_event_data.get('previous_version'),
        diffgram_version = system_event_data.get('diffgram_version'),
        host_os = system_event_data.get('host_os'),
        storage_backend = system_event_data.get('storage_backend'),
        service_name = system_event_data.get('service_name'),
        startup_time = system_event_data.get('startup_time'),
        shut_down_time = system_event_data.get('shut_down_time'),
        created_date = system_event_data.get('created_date'),
    )
    session.add(system_event)
    session.commit()
    return system_event


def create_job(job_data, session):
    """
        The function will create a Job object for testing purposes. You can supply you own
        project if there is one in specific that has to be attached, if not the function will
        also mock a project for you. The idea is that new developer don't have to worry about the
        relations between object in order to mock faster.
        For example: "I want to create a Job, but I don't really care about the project."
            - Then I should not worry about the details of mocking a project.

        TODO:
        More data mocks are still pending, like members, labels, etc...
        For now, this is sufficient for the current tests we're writing.
    :param job_data:
    :param session:
    :return:
    """
    if job_data.get('project'):
        job = Job(member_created = None, project = job_data.get('project'))
    else:
        project_string_id = '{}-job-project'.format(get_random_string(8))
        project_context = {
            'project_string_id': project_string_id,
            'project_name': '{}-job-project'.format(project_string_id),
            'users': [
                {'username': '{}-job-user'.format(get_random_string(5)),
                 'email': 'test@test.com',
                 'password': 'diffgram123',
                 'project_string_id': project_string_id
                 }
            ]
        }
        project_data = create_project_with_context(project_context, session)
        job = Job(member_created = None, project = project_data.get('project'),
                  project_id = project_data.get('project').id)
    session.add(job)

    # TODO: support mocking labels.
    job.label_dict = job_data.get('label_dict', {})
    job.type = job_data.get('type', 'draft')
    job.status = job_data.get('status', 'draft')
    job.label_dict['label_file_list'] = job_data.get('label_file_list', [])
    job.name = job_data.get('name', None)
    job.output_dir_action = job_data.get('output_dir_action', 'nothing')
    job.share_type = job_data.get('name', 'project')

    job.share_type = job.share_type.lower()

    job.launch_datetime = datetime.datetime.now()

    if job.launch_datetime is not None:
        job.waiting_to_be_launched = True

    job.interface_connection_id = job_data.get('interface_connection_id')
    job.file_count = job_data.get('file_count', 0)  # note this is user set

    job.permission = job_data.get('file_count', 'all_secure_users')
    job.label_mode = job_data.get('label_mode', 'open')
    job.passes_per_file = job_data.get('passes_per_file', 1)
    job.instance_type = job_data.get('instance_type', 'box')
    job.file_handling = job_data.get('file_handling', 'use_existing')
    job.stat_count_tasks = job_data.get('stat_count_tasks', 0)
    job.completion_directory_id = job_data.get('completion_directory_id', None)

    directory = WorkingDir.new_blank_directory(session = session)
    session.add(directory)
    job.directory = directory

    # if job.share_type == "market":
    #     bid_new_core(
    #         session=session,
    #         job=job,
    #     )
    regular_methods.commit_with_rollback(session)

    for dir in job_data.get('attached_directories', []):
        rel = JobWorkingDir()
        rel.sync_type = 'sync'
        rel.job_id = job.id
        rel.working_dir_id = dir.id
        session.add(rel)
    regular_methods.commit_with_rollback(session)
    session.add(job)
    session.commit()
    return job


def create_label(label_data, session):
    existing_label = Label.get_by_name(session = session, label_name = label_data.get('name'))
    if existing_label:
        return existing_label
    label = Label()
    label.name = label_data.get('name')
    session.add(label)
    regular_methods.commit_with_rollback(session)
    return label


def create_label_file(label_file_data, session):
    label_file = File()
    label_file.label = label_file_data.get('label')
    label_file.label_id = label_file_data.get('label').id
    label_file.project_id = label_file_data['project_id']
    label_file.state = label_file_data.get('state', 'added')
    label_file.type = 'label'
    session.add(label_file)
    regular_methods.commit_with_rollback(session)
    project = Project.get_by_id(session, label_file.project_id)
    if project:
        WorkingDirFileLink.add(session, project.directory_default_id, label_file)
        project.refresh_label_dict(session)
    session.add(label_file)
    regular_methods.commit_with_rollback(session)
    return label_file


def create_export(export_data, session):
    export = Export(
        type = export_data.get('type'),
        kind = export_data.get('kind'),
        archived = export_data.get('archived'),
        masks = export_data.get('masks'),
        source = export_data.get('source'),
        status = export_data.get('status'),
        status_text = export_data.get('status_text'),
        percent_complete = export_data.get('percent_complete'),
        file_comparison_mode = export_data.get('file_comparison_mode'),
        file_list_length = export_data.get('file_list_length'),
        description = export_data.get('description'),
        working_dir_id = export_data.get('working_dir_id'),
        project_id = export_data.get('project_id'),
        user_id = export_data.get('user_id'),
        job_id = export_data.get('job_id'),
        task_id = export_data.get('task_id'),
        yaml_blob_name = export_data.get('yaml_blob_name'),
        json_blob_name = export_data.get('json_blob_name'),
        tf_records_blob_name = export_data.get('tf_records_blob_name'),
        ann_is_complete = export_data.get('ann_is_complete'),

    )
    session.add(export)
    regular_methods.commit_with_rollback(session)
    return export


def create_discussion_comment(discussion_comment_data, session):
    issue_comment = DiscussionComment(
        discussion_id = discussion_comment_data.get('discussion_id'),
        user_id = discussion_comment_data.get('user_id'),
        member_created_id = discussion_comment_data.get('member_created_id'),
        project_id = discussion_comment_data.get('project_id'),
        content = discussion_comment_data.get('content'),

    )
    session.add(issue_comment)
    regular_methods.commit_with_rollback(session)
    return issue_comment


def create_instance(instance_data, session):
    instance = Instance(
        project_id = instance_data.get('project_id'),
        task_id = instance_data.get('task_id'),
        type = instance_data.get('type'),
        hash = instance_data.get('hash'),
        status = instance_data.get('status'),
        start_sentence = instance_data.get('start_sentence'),
        end_sentence = instance_data.get('end_sentence'),
        start_token = instance_data.get('start_token'),
        end_token = instance_data.get('end_token'),
        start_char = instance_data.get('start_char'),
        end_char = instance_data.get('end_char'),
        sentence = instance_data.get('sentence'),
        sequence_id = instance_data.get('sequence_id'),
        number = instance_data.get('number'),
        frame_number = instance_data.get('frame_number'),
        global_frame_number = instance_data.get('global_frame_number'),
        machine_made = instance_data.get('machine_made'),
        interpolated = instance_data.get('interpolated'),
        fan_made = instance_data.get('fan_made'),
        verified = instance_data.get('verified'),
        occluded = instance_data.get('occluded'),
        soft_delete = instance_data.get('soft_delete', False),
        label_file_id = instance_data.get('label_file_id'),
        file_id = instance_data.get('file_id'),
        points = instance_data.get('points'),
        mask_url = instance_data.get('mask_url'),
        mask_blob_dir = instance_data.get('mask_blob_dir'),
        mask_url_expiry = instance_data.get('mask_url_expiry'),
        x_min = instance_data.get('x_min'),
        y_min = instance_data.get('y_min'),
        x_max = instance_data.get('x_max'),
        y_max = instance_data.get('y_max'),
        width = instance_data.get('width'),
        height = instance_data.get('height'),
        preview_image_url = instance_data.get('preview_image_url'),
        preview_image_blob_dir = instance_data.get('preview_image_blob_dir'),
        preview_image_url_expiry = instance_data.get('preview_image_url_expiry'),
        rating = instance_data.get('rating'),
        rating_comment = instance_data.get('rating_comment'),
        attribute_groups = instance_data.get('attribute_groups'),
        member_created_id = instance_data.get('member_created_id'),
        nodes = {'nodes': instance_data.get('nodes')},
        edges = {'edges': instance_data.get('edges')},
        previous_id = instance_data.get('previous_id'),
        root_id = instance_data.get('root_id')
    )
    session.add(instance)
    regular_methods.commit_with_rollback(session)
    return instance


def create_discussion_relation(discussion_relation, session):
    rel = DiscussionRelation(
        discussion_id = discussion_relation.get('discussion_id'),
        instance_id = discussion_relation.get('instance_id'),
        file_id = discussion_relation.get('file_id'),
        job_id = discussion_relation.get('job_id'),
        task_id = discussion_relation.get('task_id'),

    )
    session.add(rel)
    regular_methods.commit_with_rollback(session)
    return rel


def create_discussion(discussion_data, session):
    issue = Discussion(
        title = discussion_data.get('title'),
        description = discussion_data.get('description'),
        member_created_id = discussion_data.get('member_created_id'),
        project_id = discussion_data.get('project_id'),
        status = discussion_data.get('status', 'open'),
    )

    session.add(issue)
    regular_methods.commit_with_rollback(session)
    issue.attach_element(session, {'type': 'project', 'id': discussion_data.get('project_id')})
    regular_methods.commit_with_rollback(session)
    return issue


def create_task(task_data, session):
    task = Task()
    session.add(task)

    task.is_live = task_data.get('is_live', True)

    # # #
    if 'job' not in task_data:
        job = create_job({'name': 'jobtest:{}'.format(task_data.get('name'))}, session)
    else:
        job = task_data.get('job')
    task.job_id = job.id
    task.job = job
    if 'file' not in task_data:
        # TODO: add file create mock.
        file_id = None
    else:
        file_id = task_data.get('file').id
    task.file_id = file_id
    task.file = task_data.get('file')
    # TODO: might need to create mock functions for the following relations
    task.guide_id = task_data.get('guide_id', None)

    task.label_dict = task_data.get('label_dict', {})
    task.file_original_id = task_data.get('file_original_id', None)
    task.file_original = task_data.get('file_original', None)
    task.completion_directory_id = task_data.get('completion_directory_id', None)
    task.incoming_directory_id = task_data.get('incoming_directory_id', None)
    task.task_type = task_data.get('task_type', 'draw')

    if task.task_type == 'draw':
        # Set draw tasks to be available instead of
        # default of created
        task.status = 'available'

        # Cache from job
    task.status = task_data.get('status', 'available')
    task.project_id = job.project_id
    task.job_type = job.type
    task.label_mode = job.label_mode

    # Have defaults
    task.kind = task.task_type = task_data.get('kind', 'human')
    regular_methods.commit_with_rollback(session)

    return task


def create_sync_event(sync_event_data, session):
    dataset_source = sync_event_data.get('dataset_source', None)
    dataset_source_id = sync_event_data.get('dataset_source_id', None)
    dataset_destination = sync_event_data.get('dataset_destination', None)
    dataset_destination_id = sync_event_data.get('dataset_destination_id', None)
    description = sync_event_data.get('description', None)
    file = sync_event_data.get('file', None)
    job = sync_event_data.get('job', None)
    job_id = sync_event_data.get('job_id', None)
    input_id = sync_event_data.get('input_id', None)
    project = sync_event_data.get('project', None)
    created_task = sync_event_data.get('created_task', None)
    completed_task = sync_event_data.get('completed_task', None)
    new_file_copy = sync_event_data.get('new_file_copy', None)
    transfer_action = sync_event_data.get('transfer_action', None)
    event_effect_type = sync_event_data.get('event_effect_type', None)
    event_trigger_type = sync_event_data.get('event_trigger_type', None)
    processing_deferred = sync_event_data.get('processing_deferred', None)
    member_created = sync_event_data.get('member_created', None)
    member_updated = sync_event_data.get('member_updated', None)
    status = sync_event_data.get('status', None)

    created_date = datetime.datetime.now()
    sync_event = SyncEvent(
        dataset_source_id = dataset_source_id,
        dataset_destination_id = dataset_destination_id,
        description = description,
        file = file,
        input_id = input_id,
        job_id = job_id,
        project = project,
        created_task = created_task,
        completed_task = completed_task,
        new_file_copy = new_file_copy,
        transfer_action = transfer_action,
        event_effect_type = event_effect_type,
        event_trigger_type = event_trigger_type,
        processing_deferred = processing_deferred,
        member_created = member_created,
        member_updated = member_updated,
        created_date = created_date,
        status = status
    )
    session.add(sync_event)
    regular_methods.commit_with_rollback(session)
    return sync_event


def create_project_with_context(context_data, session):
    """
    This function will create mock data for a project and all the necessary context for any unit testing
    to be performed.
    context_data will be a dictionary with all the context for creating the project.
    The idea is that you'll be able to specify users, labels, tasks, etc... and the function will make sure all the
    data is mocked properly.

    Example: For my test I need a project with 2 users, 1 admin and another with view permissions. I also need 3 labels.
    The context_data should look something like this:
    {
    'project_name': 'My test project',
    'users': [
        {'name': 'john', permissions: 'admin'}
        {'name': 'maria', permissions: 'view'}
    },
    'labels': [
        {'name': 'catlabel', 'type': 'box'}
        {'name': 'dogabel2', 'type': 'box'}
    ]

    The function will return a similar data structure with the ID's on the test database for further querying
    inside the test cases.

    :param context_data:
    :return:
    """

    random_name = get_random_string(8)
    project_string_id = context_data.get('project_string_id', random_name)
    project_name = context_data.get('project_name', random_name)

    default_project_limit = 10
    user = register_user(
        {'username': 'project_owner_{}'.format(project_string_id),
         'email': 'test{}@test.com'.format(project_string_id),
         'password': 'diffgram123'},
        session
    )
    member = Member(kind = 'human')
    session.add(member)
    session.flush()
    user.member = member

    project = Project.new(
        session = session,
        name = project_name,
        project_string_id = project_string_id,
        goal = 'Test stuff',
        member_created = None,
        user = user
    )
    user_list = []
    for user in context_data['users']:
        if user.get('project_string_id') is None:
            user['project_string_id'] = random_name
        new_user = register_user(user, session)
        member = Member(kind = 'human')
        session.add(member)
        session.flush()
        new_user.member = member
        new_user.member_id = member.id
        session.add(new_user)
        user_list.append(new_user)
    regular_methods.commit_with_rollback(session)
    return {
        'project': project,
        'users': user_list
    }
