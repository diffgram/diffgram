# OPENCORE - ADD
# This module is responsible for adding files to a job's directory.

from methods.regular.regular_api import *  # Import necessary methods from the regular API

from shared.database.user import UserbaseProject  # Import UserbaseProject class

from shared.database.task.job.job import Job  # Import Job class
from shared.database.task.job.job_working_dir import JobWorkingDir  # Import JobWorkingDir class

"""

Attach files to a jobs directory
Could also edit / remove?

"""

# The decorators for the API route and rate limiting
@routes.route('/api/v1/project/<string:project_string_id>' +
              '/job/dir/attach',
              methods=['POST'])
@limiter.limit("20 per day")

# Project permissions decorator to check if the user has the required permissions
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

    # Input validation and parsing
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
        # If there are errors in the input, return a 400 Bad Request response
        return jsonify(log=log), 400

    # Database session setup
    with sessionMaker.session_scope() as session:

        # Fetch the project and job using their IDs
        project = Project.get(session, project_string_id)
        job = Job.get_by_id(session, input['job_id'])

        # Check if the user has the required permissions for the job
        Job_permissions.check_job_after_project_already_valid(
            job=job,
            project=project)

        # Get the list of directories to be attached
        directory_list = input['directory_list']

        # If the directory list is empty, return a 200 OK response with the job details
        if len(directory_list) == 0:
            return jsonify(
                log=log,
                job=job.serialize_builder_info_edit(session)), 200

        # Fetch the job's directory
        directory = job.directory

        # Get the current user
        user = User.get(session)

        # Add the job to the session
        session.add(job)

        # Extract the directory IDs from the directory list
        dir_ids = [x['directory_id'] for x in directory_list]

        # Check if all directories exist and belong to the current project
        selected_dirs = session.query(WorkingDir).filter(WorkingDir.id.in_(dir_ids))
        for dir in selected_dirs:
            if dir.project_id != project.id:
                log['error']['directory_list'] = 'Provide only directories belonging to the project.'

        # If there are errors in the input, return a 400 Bad Request response
        if len(log["error"].keys()) >= 1:
            return jsonify(log=log), 400

        # Update the job's attached directories
        job.update_attached_directories(session, directory_list, delete_existing=True)
        job.set_cache_key_dirty(cache_key="attached_directories_dict")

        # Prepare event data for logging
        user_email = None
        member_id = None
        if user:
            user_email = user.email
            member_id = user.member_id

        # Log the event
        Event.new(
            kind="job_attached_directories_update",
            session=session,
            member_id=member_id,
            success=True,
            email=user_email
        )

        # Set the response log and job details
        log['success'] = True
        return jsonify(
            log=log,
            job=job.serialize_builder_info_edit(session)), 200
