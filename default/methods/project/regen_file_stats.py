import concurrent.futures
from contextlib import contextmanager
from typing import Dict, Any, List, Union

from methods.regular.regular_api import *
from shared.database.deletion import Deletion
from shared.database.source_control.file_stats import FileStats
from sqlalchemy.orm import Session

@contextmanager
def session_scope(session_factory):
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


@routes.route('/api/v1/project/<string:project_string_id>/regen-file-stats',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=["admin"],
    apis_user_list=['api_enabled_builder', 'security_email_verified'])
@limiter.limit("20 per day")
def api_project_regen_file_stats(project_string_id):
    """
        Admin feature: regenerate file stats for dataset explorer 2.0
    :param project_string_id:
    :return:
    """
    log = regular_log.default()
    with sessionMaker.session_scope() as session:

        member = get_member(session)
        project = Project.get(session, project_string_id)

        log = project_regen_file_stats_core(
            session=session,
            project=project,
            log=log,
            member=member)

        if len(log["error"].keys()) >= 1:
            return jsonify(log=log), 400

        log['success'] = True
        return jsonify(
            log=log,
            project=project.serialize()), 200


def regen_project_file_stats(project_id: int, session: Session) -> Dict[str, Any]:
    """
        Developer feature: regenerates file stats on all the project.
        For query explorer. Usually used if user was on a previous version
        and upgraded to dataset explorer 2.0
    :param session:
    :param project_id:
    :return:
    """
    files = session.query(File).filter(File.project_id == project_id, File.state != 'removed').all()
    logger.info(f'Total Files in Project:  {len(files)}')
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(update_file_stats_data, session, file): file for file in files}
        for future in concurrent.futures.as_completed(futures):
            file = futures[future]
            try:
                future.result()
            except Exception as e:
                logger.error(f'Error updating file stats for file {file.id}: {e}')
    logger.info('Finished regenerating files successfully.')


def update_file_stats_data(session: Session, file: File) -> None:
    """
        Updates file stats data for a given file
    :param session:
    :param file:
    :return:
    """
    file_serialized = file.serialize_with_annotations(session=session)
    instance_list = file_serialized.get('instance_list')
    logger.info(f'Creating Stats for file ID: {file.id}')

    if file.project:
        FileStats.update_file_stats_data(
            session=session,
            instance_list=instance_list,
            file_id=file.id,
            project=file.project
        )
        session.commit()


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
    with session_scope(session.bind) as session_scoped:
        regen_project_file_stats(project.id, session_scoped)

    return log
