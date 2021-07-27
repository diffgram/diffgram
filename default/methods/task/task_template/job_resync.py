from methods.regular.regular_api import *
from shared.database.auth.member import Member
from shared.utils import job_dir_sync_utils
import threading


@routes.route('/api/v1/project/<string:project_string_id>/job/resync',
              methods = ['POST'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor"], apis_user_list = ["api_enabled_builder"])
def job_resync_api(project_string_id):
    """
        Checks for any missing files on the job's datasets
        and sends a resync signal to create task
        in case of missing files.
    :return: http response
    """

    spec_list = [
        {"task_template_id": {
            'required': True,
            'kind': int
        }},
    ]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        user = User.get(session)
        project = Project.get_by_string_id(session = session, project_string_id = project_string_id)
        if user:
            member = user.member
        else:
            client_id = request.authorization.get('username', None)
            auth = Auth_api.get(session, client_id)
            member = auth.member

        resync_result, log = job_resync_core(session = session,
                                             project = project,
                                             member = member,
                                             task_template_id = input['task_template_id'],
                                             log = log)
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400
        return jsonify(resync_result = resync_result, log = log), 200


def job_resync_core(session,
                    project,
                    member,
                    task_template_id,
                    log):
    """
        Given the JOB id, find all the files with no tasks attached to the job,
        and trigger events to create tasks for them.
    :param session:
    :param job_id:
    :param log:
    :return:
    """
    result = True
    task_template = Job.get_by_id(session = session, job_id = task_template_id)
    if task_template.project_id != project.id:
        log['error']['project_id'] = 'Invalid job given for project {}'.format(project.project_string_id)
        return False, log

    t = threading.Thread(
        target = threaded_job_resync,
        args = ((task_template_id, member.id)))
    t.start()

    return result, log


def threaded_job_resync(task_template_id, member_id):
    with sessionMaker.session_scope_threaded() as session:
        log = regular_log.default()
        member = Member.get_by_id(session = session, member_id = member_id)
        task_template = Job.get_by_id(session = session, job_id = task_template_id)
        attached_dirs = task_template.get_attached_dirs(session = session, sync_types = ['sync'])
        task_list = task_template.task_list(session = session)
        file_ids = [t.file_id for t in task_list]
        missing_files = []
        for directory in attached_dirs:
            files = WorkingDirFileLink.file_list(
                session = session,
                limit = None,
                working_dir_id = directory.id
            )
            for file in files:
                if file.id not in file_ids:
                    logger.info(
                        'Resyncing File {} on Job {} From Dir {}'.format(file.id, task_template_id, directory.id))
                    job_sync_dir_manger = job_dir_sync_utils.JobDirectorySyncManager(
                        session = session,
                        job = task_template,
                        log = log
                    )

                    job_sync_dir_manger.create_file_links_for_attached_dirs(
                        sync_only = True,
                        create_tasks = True,
                        file_to_link = file,
                        file_to_link_dataset = directory,
                        related_input = None,
                        member = member
                    )
                    task_template.update_file_count_statistic(session = session)
                    missing_files.append(file)

    logger.info('Resyncing on Job {} Success. {} Missing files synced'.format(task_template_id, len(missing_files)))
    return missing_files
