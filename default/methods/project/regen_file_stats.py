from methods.regular.regular_api import *
from shared.database.deletion import Deletion
from threading import Thread
from shared.database.source_control.file_stats import FileStats


@routes.route('/api/v1/project/<string:project_string_id>/regen-file-stats',
              methods = ['POST'])
@Project_permissions.user_has_project(
    Roles = ["admin"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
@limiter.limit("20 per day")
def api_project_regen_file_stats(project_string_id):
    """
        Admin feature: regenerate file stats for dataset explorer 2.0
    :param project_string_id:
    :return:
    """
    log = regular_log.default()
    with sessionMaker.session_scope() as session:

        user = User.get(session = session)
        project = Project.get(session, project_string_id)

        log = project_regen_file_stats_core(
            session = session,
            project = project,
            log = log,
            member = user.member)

        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        log['success'] = True
        return jsonify(
            log = log,
            project = project.serialize()), 200


def regen_project_file_stats(project_id: int):
    with sessionMaker.session_scope_threaded() as session:
        files = session.query(File.id).filter(File.project_id == project_id, File.state != 'removed').all()
        logger.info(f'Total Files in Project:  {len(files)}')
        for file_elm in files:

            file_id = file_elm[0]

            file = File.get_by_id(session, file_id = file_id)
            file_serialized = file.serialize_with_annotations(session = session)
            instance_list = file_serialized.get('instance_list')
            logger.info(f'Creating Stats for file ID: {file_id}')

            if file.project:
                FileStats.update_file_stats_data(
                    session = session,
                    instance_list = instance_list,
                    file_id = file_id,
                    project = file.project
                )
                session.commit()
        logger.info('Finished regenerating files successfully.')


def project_regen_file_stats_core(session,
                                  project,
                                  log,
                                  member):
    """
        Developer feature: regenerates file stats on all the project.
        For query explorer. Usually used if user was on a previous version
        and upgraded to dataset explorer 2.0
    :param session:
    :param project:
    :param log:
    :param member:
    :return:
    """

    t = Thread(
        target = regen_project_file_stats,
        args = ((project.id,)))
    t.start()

    return log
