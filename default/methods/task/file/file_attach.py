# OPENCORE - ADD
from methods.regular.regular_api import *

from shared.database.user import UserbaseProject

from shared.database.task.job.job import Job

"""

Attach files to a jobs directory
Could also edit / remove?

"""


@routes.route('/api/v1/project/<string:project_string_id>' +
              '/job/file/attach',
              methods=['POST'])
@limiter.limit("20 per day")
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=['api_enabled_builder', 'security_email_verified'])
def add_files_to_job_api(project_string_id):
    """
    Method adds files to a job. Used in the job creation section when attaching files.

    Still need a method for individual file selection so start with this

    Adds selected files to a job

    Assumes the job already has a directory created

    For each file creates a pointer

    Assumption here is we are attaching files directly...
    ie we don't have to check latest version or how that's happening...

    Security for checking files are in directory...

    """

    # get / declare file list...

    # Maybe instead of passing literal file list, we pass the search criteria?
    # But limit of this is a user may select specific files...

    # TODO a lot of this feels like generic stuff for
    # Adding or removing to a directory

    spec_list = [
        {"file_list_selected":
             {'kind': list}
         },
        {"job_id":
             {'kind': int}
         },
        {"add_or_remove":
             {'kind': str}
         },
        {"directory_id":
             {'default': None}
         },
        {"select_from_metadata":  # WIP NOT yet implemented
             {'default': False,
              'kind': bool}
         },
        {"metadata_proposed":  # WIP NOT yet implemented
             {'default': None,
              'kind': dict}
         }
    ]

    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)

    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)

        job = Job.get_by_id(session, input['job_id'])

        Job_permissions.check_job_after_project_already_valid(
            job=job,
            project=project)

        add_or_remove = input['add_or_remove']
        file_list_selected = input['file_list_selected']

        directory = job.directory

        ## TODO review how we are getting user's directory
        user = User.get(session)

        directory_id = untrusted_input.get('directory_id', None)

        incoming_directory = WorkingDir.get_with_fallback(
            session=session,
            directory_id=directory_id,
            project=project)

        if incoming_directory is False:
            log['error']['directory'] = "No directory found"
            return jsonify(log=log), 400

        session.add(job)

        result, count_changed = file_list_to_directory(
            session=session,
            add_or_remove=add_or_remove,
            log=log,
            directory=directory,
            file_list=file_list_selected,
            incoming_directory=incoming_directory,
            job=job
        )

        # Context of not wanting to show
        # Success when there are "sub errors"
        # Not clear on optimal way to handle this
        # Maybe ideally show success / errors on a per file basis

        if len(log["error"].keys()) >= 1:
            return jsonify(log=log), 400

        # updates file_count_statistic
        job.update_file_count_statistic(session=session)

        user_email = None
        member_id = None
        if user:
            user_email = user.email
            member_id = user.member_id

        Event.new(
            kind="job_file_update",
            session=session,
            member_id=member_id,
            success=True,
            email=user_email
        )

        log['success'] = True
        return jsonify(
            log=log,
            job=job.serialize_builder_info_edit(session)), 200


def file_list_to_directory(
        session,
        add_or_remove,
        log,
        directory,
        file_list,
        incoming_directory,
        job
) -> (bool, int):
    """
    We track the count here
    BUT not using it yet. may be useful in future for stats
    forgot had update_file_count_statistic() already

    Optionally we could optimize this by setting the count directly
    instead of calling that / those methods could work together.
    Also could be helpful for testing

    Manual test case
        Select some files and try attaching them
    """

    count = 0

    for file_dict in file_list:

        # TODO this blindly trusts id is in file_dict

        result, log = WorkingDirFileLink.file_link_update(
            session=session,
            add_or_remove=add_or_remove,
            incoming_directory=incoming_directory,
            directory=directory,
            file_id=file_dict.get('id'),
            job=job,
            log=log
        )

        if result == False:
            continue

        if add_or_remove == "add":
            count += 1
        elif add_or_remove == "remove":
            count -= 1

    return True, count
