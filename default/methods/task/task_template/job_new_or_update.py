try:
    from methods.regular.regular_api import *

except:
    from default.methods.regular.regular_api import *
from shared.utils.job_launch_utils import task_template_label_attach
from shared.database.source_control.working_dir import WorkingDirFileLink
from shared.database.task.job.job import Job
from shared.utils.task import task_file_observers
from shared.database.userscript.userscript import UserScript


job_new_spec_list = [
    {"name": {
        'default': str(time.time()),
        'kind': str
        }
    },
    {"default_userscript_id": {
        'default': None,
        'kind': int
        }
    },
    {"share": {
        'default': "project",
        'kind': str
    }
    },
    {"instance_type": {
        'default': "box",
        'kind': str
    }
    },
    {"permission": {
        'default': "all_secure_users",
        'kind': str
    }
    },
    {"label_mode": {
        'default': "closed_all_available",
        'kind': str
    }
    },
    {"passes_per_file": {
        'default': 1,
        'kind': int
    }
    },
    {"type": {
        'default': "Normal",
        'kind': str,
    }
    },
    {"review_by_human_freqeuncy": {
        'default': "None",
        'kind': str
    }
    },
    {"category": {
        'default': "visual",
        'kind': str
    }
    },
    {"td_api_trainer_basic_training": {
        'default': False,
        'kind': bool,
    }
    },
    {"launch_datetime": {
        'default': None,
        'kind': "datetime"
    }
    },
    {"interface_connection_id": {
        'default': None,
        'kind': int
    }
    },
    {"file_count": {
        'default': None,
        'kind': int
    }
    },
    {"label_file_list": {
        'default': None,
        'kind': list
        }
    },
    {"file_handling": {
        'default': "use_existing",
        'valid_values_list': [None, "use_existing", "isolate"],
        'kind': str
        }
    },
    {"member_list_ids": {
        'default': None,
        'allow_empty': True,
        'kind': list,
        'required': False
        }
    },
    {"pro_network": {
        'default': False,
        'kind': bool,
        'required': False
        }
    },
    {"attached_directories_dict": {
        'kind': dict,
        'required': False
    }},
]

"""
We have strong defaults for a new job
but not for updating? So keep this seperate for not?

But we want to validate the kind
"""

update_job_spec_list = [
    {"job_id": {
        'kind': int
    }},
    {"attached_directories_dict": {
        'kind': dict
    }},
    {"completion_directory_id": {
        'kind': int
    }},
    {"output_dir_action": {
        'kind': str
    }},
    {"name": {
        'kind': str,
        'default': None
    }
    },
    {"default_userscript_id": {
        'kind': int
        }
    },
    {"share_type": {
        'kind': str,
        'default': None
    }
    },
    {"file_handling": {
        'kind': str,
        'default': None
    }
    },
    {"instance_type": {
        'kind': str,
        'default': None
    }
    },
    {"permission": {
        'kind': str,
        'default': None
    }
    },
    {"label_mode": {
        'kind': str,
        'default': None
    }
    },
    {"passes_per_file": {
        'kind': int,
        'default': None
    }
    },
    {"type": {
        'kind': str,
        'default': None
    }
    },
    {"review_by_human_freqeuncy": {
        'kind': str,
        'default': None
    }
    },
    {"interface_connection_id": {
        'kind': int,
        'default': None
    }
    },
    {"category": {
        'kind': str,
        'default': None
    }
    },
    {"launch_datetime": {
        'kind': "datetime",
        'default': None,
    }
    },
    {"file_count": {
        'kind': int,
        'default': None
    }
    },
    {"label_file_list": {
        'default': None,
        'kind': list
        }
    },
    {"member_list_ids": {
        'default': None,
        'kind': list,
        'allow_empty': True,
        'required': False
        }
    },
    {"pro_network": {
        'kind': bool,
        'required': False
        }
    }
]


# note this is just for "label" at time of writing

@routes.route('/api/v1/project/<string:project_string_id>' +
              '/job/update',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=["api_enabled_builder"])
def job_update_api(project_string_id):
    """
    Do we want a different spec list here...

    """
    log, input, untrusted_input = regular_input.master(
        request=request,
        spec_list=update_job_spec_list)

    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:
        project = Project.get(session, project_string_id)

        job = Job.get_by_id(session, input['job_id'])

        if job is None:
            log['error']['job'] = "No job found"
            return jsonify(log=log), 400

        Job_permissions.check_job_after_project_already_valid(
            job=job,
            project=project)

        job, log = job_update_core(session, job, project, input, log)
        if len(log['error'].keys()) > 1:
            return jsonify(log=log), 400
        log['success'] = True
        out = jsonify(job=job.serialize_new(),
                      log=log)
        return out, 200


@routes.route('/api/v1/project/<string:project_string_id>' +
              '/job/set-output-dir',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=["api_enabled_builder"])
def job_output_dir_update(project_string_id):
    """
    Do we want a different spec list here...

    """
    output_job_spec = [
        {"job_id": {
            'kind': int
        }
        },
        {"output_dir": {
            'kind': str,
            'default': None,
            'required': False
        }},
        {
            "output_dir_action": {
                'kind': str,
                'default': None

            }
        }
    ]
    log, input, untrusted_input = regular_input.master(
        request=request,
        spec_list=output_job_spec)

    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:
        project = Project.get(session, project_string_id)

        job = Job.get_by_id(session, input['job_id'])

        if job is None:
            log['error']['job'] = "No job found"
            return jsonify(log=log), 400

        Job_permissions.check_job_after_project_already_valid(
            job=job,
            project=project)

        job, log = update_output_dir_actions(session, job, project, input, log)

        if len(log['error'].keys()) > 1:
            return jsonify(log=log), 400
        log['success'] = True
        out = jsonify(job=job.serialize_new(),
                      log=log)
        return out, 200


def update_output_dir_actions(session, job, project, input_data, log):
    if input_data['output_dir_action'] == 'nothing':
        job.output_dir_action = input_data['output_dir_action']
        session.add(job)
        return job, log

    directory = WorkingDir.get(session=session, directory_id=input_data['output_dir'], project_id=project.id)

    if directory is None:
        log['error']['output_dir'] = "No directory found"
        return None, log

    if input_data['output_dir_action'] not in ['copy', 'move', 'nothing']:
        log['error']['output_dir'] = 'output_dir  must be "copy", "move" or "nothing".'
        return None, log
    job_observable = task_file_observers.JobObservable(session=session, log=log, job=job)
    job.output_dir_action = input_data['output_dir_action']
    directory_observer = task_file_observers.DirectoryJobObserver(session=session,
                                                                  log=log,
                                                                  directory=directory,
                                                                  job_observable=job_observable)
    job_observable.add_new_directory_observer(directory_observer)
    return job, log


"""
TODO consider an update class object here
"""


def job_update_core(session, job, project, input: dict, log: dict):
    """
    Assumptions
        Main one is that if there are no updates the value will be
        empty. For example update name and not label file list...

        Main distinction is between things that touch the
        *tasks* and things that just touch the *job*
    """
    if job.status == 'draft':
        job, log = new_or_update_core(
            session=session,
            log=log,
            member=job.member_created,
            project=project,
            name=input.get('name'),
            share=input.get('share_type'),
            permission=input.get('permission'),
            label_mode=input.get('label_mode'),
            passes_per_file=input.get('passes_per_file'),
            instance_type=input.get('instance_type'),
            launch_datetime=input.get('launch_datetime'),
            file_count=input.get('file_count'),
            label_file_list=input.get('label_file_list'),
            file_handling=input.get('file_handling'),
            attached_directories_dict=input.get('attached_directories_dict'),
            output_dir_action=input.get('output_dir_action'),
            completion_directory_id=input.get('completion_directory_id'),
            interface_connection_id=input.get('interface_connection_id'),
            job_type=input['type'],
            member_list_ids=input['member_list_ids'],
            default_userscript_id=input.get('default_userscript_id'),
            job=job
        )
        return job, log
    else:
        # Trending towards anything touching the tasks
        if input['label_file_list']:
            job.label_dict['label_file_list'] = build_label_file_list(
                input['label_file_list'], session, project)

            """
            The build label file list just does the raw IDs
            job_label_attach does all the other magic
            ie color maps, and also in future expansion the
            label mode handling (like the "closed all availble")
            """
            task_template_label_attach(session, job)

            session.add(job)

            # print(len(job.label_dict['label_file_list']))

            log = update_tasks(job, session, log)

        if input['name']:
            job.name = input['name']
            session.add(job)
            log['info']['name'] = "Updated Name"

    return job, log


def update_tasks(job, session, log):
    task_list = job.task_list(
        session=session)

    for task in task_list:
        task.label_dict = job.label_dict
        session.add(task)

    log['info']['task_count'] = "Updated " + str(len(task_list)) + " tasks."
    return log


@routes.route('/api/v1/project/<string:project_string_id>' +
              '/job/new',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=["api_enabled_builder"])
@limiter.limit("40 per day")
def new_web(project_string_id):
    """
    Create "partial" task so that it can be saved as draft?

    Returns job id if possible
    That way we can save the job as a draft

    """
    log, input, untrusted_input = regular_input.master(
        request=request,
        spec_list=job_new_spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    # What defaults are we using here?
    category = None
    type = None

    with sessionMaker.session_scope() as session:

        ### MAIN

        is_live = True

        # TODO usew new generic member thing...generic method to get member
        # But this users the "is_live" thing so check that...

        # We can't use this yet since the "is_live" is coming from auth.
        # member = get_member(session)

        user = User.get(session)
        if user:
            member = user.member
        else:
            client_id = request.authorization.get('username', None)
            auth = Auth_api.get(session, client_id)
            member = auth.member
            is_live = auth.is_live

        # careful this users user stuff not member
        # TODO standard lower() method ie for Exam?
        input['share'] = input['share'].lower()

        if input['share'] == "market" and input['type'] == "Exam":

            # We only want Diffgram admins to be able to create this type
            if not user or user.is_super_admin is not True:
                log['error']['job'] = "Invalid permission. Try share 'project' or 'org'."
                return jsonify(log=log), 400

        if input['td_api_trainer_basic_training'] is True:

            if not user or user.is_super_admin is not True:
                log['error']['job'] = "Invalid permission. Try share 'project' or 'org'."
                return jsonify(log=log), 400

        project = Project.get(session, project_string_id)

        job, log = new_or_update_core(
            session=session,
            log=log,
            member=member,
            project=project,
            name=input['name'],
            share=input['share'],
            permission=input['permission'],
            label_mode=input['label_mode'],
            passes_per_file=input['passes_per_file'],
            instance_type=input['instance_type'],
            launch_datetime=input['launch_datetime'],
            file_count=input['file_count'],
            label_file_list=input['label_file_list'],
            file_handling=input['file_handling'],
            job_type=input['type'],
            interface_connection_id=input.get('interface_connection_id'),
            member_list_ids=input['member_list_ids'],
            attached_directories_dict=input['attached_directories_dict'],
            pro_network=input['pro_network'],         
            default_userscript_id=input['default_userscript_id']
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log=log), 400

        # Not happy about core method thing yet
        job.is_live = is_live
        # TODO: might need to move this inside new_or_update_core
        job.review_by_human_freqeuncy = input['review_by_human_freqeuncy']
        job.category = input['category']
        job.td_api_trainer_basic_training = input['td_api_trainer_basic_training']

        log['success'] = True

        out = jsonify(job=job.serialize_new(),
                      log=log)
        logger.info('Created Job succesfully.')
        return out, 200


def build_label_file_list(label_file_list,
                          session,
                          project) -> list:
    """
    Expects label_file_list to be of the form where
    it's a list of dicts ie [{id: 1}, {id: 2}]

    CAUTION this is JUST the label file list
    (not the color map or serialized thing)

    The overal label dict may be of the form of
    label_file_colour_map: {722716: {a: 1, hex: "#1BFC8C", hex8: "#1BFC8CFF",…},…}
    label_file_list: [722716, 726664, 726665]
    label_file_list_serialized: [{ann_is_complete: nul ...

    Updates " label_file_list: [722716, 726664, 726665]  " only.
    See job_label_attach() for specifics there...


    """

    if label_file_list:
        return File.validate_file_list(
            session=session,
            project_id=project.id,
            file_list=label_file_list)

    # Defaults if no list is provided.
    file_list = WorkingDirFileLink.file_list(
        session=session,
        working_dir_id=project.directory_default_id,
        # prefer to use self. for project here once this is a class
        limit=25,
        type="label")

    return [file.id for file in file_list]


def new_or_update_core(session,
                       log,
                       member,
                       project,
                       name,
                       share,
                       permission,
                       label_mode,
                       passes_per_file,
                       instance_type,
                       launch_datetime,
                       file_count,
                       label_file_list,
                       file_handling,
                       attached_directories_dict=None,
                       output_dir_action='nothing',
                       completion_directory_id=None,
                       interface_connection_id=None,
                       job_type=None,
                       job=None,
                       member_list_ids=None,
                       pro_network=False,
                       default_userscript_id=None):
    """

    Even if the user wants to copy an existing directory exactly
    for the job for isolation we create a new directory and pointers to it

    Allows selection of a a subset of the directory (ie only non-completed images)
    Assumption is data “flows”
    We expect more data to be added to a user’s original directory after job is created
    Can merge files fairly easily in theory but can’t go back in time and undo if it doesn’t exist in the first place

    """

    # Limits on "Created" time... ie only create once every 3 seconds

    # CAUTION some of the stuff is outside of core right now
    # needs to be reviewed (see API function above)
    is_updating = False
    if job is None:
        job = Job(member_created=member,
                  project=project)
        session.add(job)
    else:
        is_updating = True


    log = job.update_member_list(
        member_list_ids = member_list_ids,
        session = session,
        log = log)

    if default_userscript_id:
        default_userscript = UserScript.get(
            session = session,
            id = default_userscript_id,
            project_id = project.id)

        if default_userscript is None:
            log['error']['default_userscript_id'] = "Not found. Check ID or Project combo."
            return None, log

        job.default_userscript_id = default_userscript.id

    # First update fields with special concerns (i.e label_dict, share_type, launch_datetime,dir.)
    job.label_dict['label_file_list'] = build_label_file_list(label_file_list, session, project)
    if is_updating:
        # Recreate labels information dict an update all tasks accordingly
        """
        The build label file list just does the raw IDs
        job_label_attach does all the other magic
        ie color maps, and also in future expansion the
        label mode handling (like the "closed all availble")

        """
        # Not really sure if tasks can exist while in draft mode but might be good idea to update anyways.
        task_template_label_attach(session, job)
        log = update_tasks(job, session, log)

    if is_updating and job.share_type != share:
        job.share_type = share
        if not job.share_type: job.share_type = 'project'
        job.share_type = job.share_type.lower()
        log['info']['share_type'] = "Updated share_type"
    else:
        # TODO: need to finish implementation and consider cases like: when updating a job, what happens to the bid?
        job.share_type = share
        job.share_type = job.share_type.lower()

    if job.share_type not in ["market", "org", "project"]:
        log['error']['kind'] = "Invalid share_type, valid options are: ['market', 'org', 'project']"
        return False, log

    # What about validation on other inputs???
    # Look at actions or other part of system for options here...

    job.launch_datetime = launch_datetime
    # We expect this to be a valid datetime object,
    # but otherwise don't validate, ie a date in the past
    # just means "launch now"

    if job.launch_datetime is not None:
        job.waiting_to_be_launched = True

    if not is_updating:
        directory = WorkingDir.new_blank_directory(session=session)
        job.directory = directory

    job.type = job_type
    if job.type == "Exam":
        job.is_template = True
    else:
        job.is_template = False

    # Now update or add the rest of the fields
    fields_to_process = {
        'name': name,
        'file_count': file_count,
        'type': job_type,
        'permission': permission,
        'label_mode': label_mode,
        'passes_per_file': passes_per_file,
        'instance_type': instance_type,
        'file_handling': file_handling,
        'output_dir_action': output_dir_action,
        'interface_connection_id': interface_connection_id,
        'pro_network': pro_network
    }
    print('fields_to_process', fields_to_process)
    for field_key, field_val in fields_to_process.items():
        if is_updating and getattr(job, field_key) != field_val:
            setattr(job, field_key, field_val)
            log['info'][field_key] = "Updated {}".format(field_key)
        else:
            setattr(job, field_key, field_val)

    if job.pro_network is True:
        try:
            email_about_new_pro_job(
                job = job,
                user = member.user)
        except:
            logger.info("Failed to email about new pro job")

    # Update sync dirs and completion directory ID
    if isinstance(attached_directories_dict, dict):
        job.update_attached_directories(session,
                                        attached_directories_dict.get('attached_directories_list'),
                                        delete_existing=True)
        job.set_cache_key_dirty(cache_key="attached_directories_dict")
    if completion_directory_id:
        job.completion_directory_id = completion_directory_id

    if is_updating:
        Event.new(
            kind="update_job",
            session=session,
            member=member,
            success=True
        )
    else:
        Event.new(
            kind="new_job",
            session=session,
            member=member,
            success=True
        )
    return job, log



def email_about_new_pro_job(job, user):

    subject = "New Draft Pro Job: " + job.name

    message = []

    message.append(job.name)
    message.append("\n")
    message.append("ID: " + str(job.id))
    message.append("\n")
    message.append("file_count_statistic " + str(job.file_count_statistic))
    message.append("\n")

    if user:
        message.append("\n")
        message.append("User: " + user.first_name + " " + user.last_name)
        message.append("\n")
        message.append("Email:" + str(user.email))
    else:
        message.append("\n No Member.user")

    communicate_via_email.send(
	    email = "",
	    subject = subject,
	    message = "".join(message)
		)