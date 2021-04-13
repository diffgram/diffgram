# OPENCORE - ADD
from methods.regular.regular_api import *

from shared.database.user import UserbaseProject

from shared.database.task.job.job import Job
from shared.database.task.job.job_working_dir import JobWorkingDir

"""

Attach files to a jobs directory
Could also edit / remove?

"""


@routes.route('/api/v1/project/<string:project_string_id>' +
              '/job/dir/attach',
              methods=['POST'])
@limiter.limit("20 per day")
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=['api_enabled_builder', 'security_email_verified'])
def update_dirs_to_job_api(project_string_id):
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
        {"directory_list":
             {'kind': list, 'allow_empty': True}
         },
        {"job_id":
             {'kind': int}
         },
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

        directory_list = input['directory_list']
        # Do nothing for emptry dir list.
        if len(directory_list) == 0:
            return jsonify(
                log=log,
                job=job.serialize_builder_info_edit(session)), 200

        directory = job.directory

        ## TODO review how we are getting user's directory
        user = User.get(session)

        session.add(job)
        dir_ids = [x['directory_id'] for x in directory_list]

        # Check that all directories exist and belong to current project,
        selected_dirs = session.query(WorkingDir).filter(WorkingDir.id.in_(dir_ids))
        for dir in selected_dirs:
            if dir.project_id != project.id:
                log['error']['directory_list'] = 'Provide only directories belonging to the project.'

        if len(log["error"].keys()) >= 1:
            return jsonify(log=log), 400
        # Update directories
        job.update_attached_directories(session, directory_list, delete_existing=True)
        job.set_cache_key_dirty(cache_key="attached_directories_dict")
        user_email = None
        member_id = None
        if user:
            user_email = user.email
            member_id = user.member_id

        Event.new(
            kind="job_attached_directories_update",
            session=session,
            member_id=member_id,
            success=True,
            email=user_email
        )

        log['success'] = True
        return jsonify(
            log=log,
            job=job.serialize_builder_info_edit(session)), 200
