# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *


def provision_root_tasks(session,
                         job,
                         mode = 'default'):
    if not job:
        return False

    if mode == 'default':
        directory_id = job.directory_id

    """
    # WIP
    if mode == 'from_parent':
        directory = job.parent.directory_id
    """

    # TODO clarify image / video file types
    file_list = WorkingDirFileLink.file_list(
        session = session,
        working_dir_id = directory_id,
        limit = None,
        order_by_class_and_attribute = File.input_id
    )

    # TODO move to route where we collect this info and store integer
    # in case we want to use it somewhere else
    review_freqeuncy_map = {
        'every_pass': 1,
        'every_3rd_pass': 3,
        'every_10th_pass': 10,
    }
    review_frequncy = review_freqeuncy_map.get(
        job.review_by_human_freqeuncy, None)

    #
    #  option Hard code review frequency to None while working out bugs
    # There was something strange with the way it "pushed" the reviewed
    # file during testing. Not to mention review interface itself
    review_frequncy = None

    session.add(job)
    job.stat_count_tasks = 0

    for index, file in enumerate(file_list):

        root_task = root_task_new(session = session,
                                  job = job,
                                  file = file,
                                  guide_id = job.guide_default_id)

        if review_frequncy:
            if (index + 1) % review_frequncy == 0:
                review_task = create_review_sub_task(
                    session = session,
                    job = job,
                    root_task = root_task,
                    guide_id = job.guide_review_id)

    return True


def root_task_new(session,
                  job,
                  file,
                  guide_id):
    """
    Create a new root task

    Depending on conditions ...

    Should we always consider the root task to be a "system" level task?
    or is that unnessary... don't want to over complicate it

    How do we know which root tasks have been created / files addressed?
    Unless we somehow track that? Maybe are we better off just creating all
    the root tasks upfront?

    Do we create the review tasks upfront? or does that simply
    get done "one demand" ie a flag to crete a new xyz task upon completion...
    or maybe both...

    future looking at a
        job.copy_instance_list

    because "copying" a video file requires new sequence creation

    And also this may be something we want as "feature"

    """

    if job.file_handling == "isolate":
        new_file = copy_file(session = session,
                             directory = job.directory,
                             completion_directory_id = job.completion_directory_id,
                             file = file,
                             copy_instance_list = False)
    else:  # assume use existing
        new_file = file
        new_file.ann_is_complete = False
        session.add(new_file)

    new_file.job_id = job.id
    # We assume this only works for the "root" file
    # ie for video, for the video file itself
    # We assign job id here in advance since functions like export depend on it

    # TODO number of passes
    # TODO advaned label options

    # TODO this is confusing to call it "file_original_id" when it's a copy??

    task = task_new(session = session,
                    job = job,
                    file_id = new_file.id,
                    file_original_id = file.id,
                    guide_id = guide_id,
                    label_dict = job.label_dict,
                    incoming_directory = job.directory)

    task.is_root = True

    session.flush()
    new_file.task_id_root = task.id

    return task


def task_new(session,
             job,
             file_id,
             guide_id,
             label_dict,
             file_original_id,
             kind = 'human',
             task_type = 'draw',
             incoming_directory = None):
    """

    Core new task creation, shared with root tasks and sub tasks...

    """

    return Task.new(
        session = session,
        job = job,
        file_id = file_id,
        guide_id = guide_id,
        label_dict = label_dict,
        file_original_id = file_original_id,
        kind = kind,
        task_type = task_type,
        incoming_directory = incoming_directory
    )


def copy_file(session,
              directory,
              completion_directory_id,
              file,
              copy_instance_list = False
              ):
    """
    CAUTION Assumes completion_directory_id is orginal_directory_id

    Create copy of file for task
    """
    # TODO handle file "parent / child linking stuff

    new_file = File.copy_file_from_existing(
        session = session,
        working_dir = directory,
        existing_file = file,
        copy_instance_list = copy_instance_list,
        add_link = False,
        remove_link = False,
        orginal_directory_id = completion_directory_id,
        deep_copy = True,
        ann_is_complete_reset = True
    )

    assert new_file != file

    return new_file


def create_review_sub_task(session,
                           job,
                           root_task,
                           guide_id,
                           create_new_file = False):
    """

    Assumes job has already been added to session

    """

    # Copy shared data from root task / job

    # Full access to labels?

    task = task_new(session = session,
                    job = job,
                    file_id = root_task.file_id,
                    file_original_id = root_task.file_original_id,
                    guide_id = guide_id,
                    label_dict = job.label_dict,
                    task_type = 'review'
                    )

    # Declare what's different about this task

    # TODO handling difference between
    # root and parent for future tasks further down the graph
    session.flush()

    # We don't move to available until first task is done
    task.status = 'created'
    task.parent_id = root_task.id
    task.root_id = root_task.id
    root_task.child_primary_id = task.id

    job.stat_count_tasks += 1

    # Caution!!! does not fully support video yet. See sequence thing.
    if create_new_file is True:
        task.file = File.copy_file_from_existing(
            session = session,
            working_dir = None,
            existing_file = root_task.file,
            copy_instance_list = True,
            add_link = False,
            remove_link = False,
            deep_copy = True
        )
        session.add(task)

    return task

# In what cases need/want to assign child id?


# Other completion rules
