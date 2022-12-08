# OPENCORE - ADD
from methods.regular.regular_api import *
from shared.database.report.report_template import ReportTemplate
from .report_runner import Report_Runner
from sqlalchemy.orm.session import Session


@routes.route('/api/v1/project/<string:project_string_id>/report/<int:report_template_id>', methods = ['GET'])
@General_permissions.grant_permission_for(
    Roles = ['normal_user'],
    apis_user_list = ["builder"])
def report_view_api(project_string_id: str, report_template_id: int):
    with sessionMaker.session_scope() as session:
        log = regular_log.default()
        report_template_data, log = report_view_core(
            session = session,
            project_string_id = project_string_id,
            report_template_id = report_template_id,
            log = log
        )
        if regular_log.log_has_error(log):
            return jsonify(log = log), 400

        return jsonify(log = log, report_template = report_template_data), 200


def report_view_core(session: Session,
                     project_string_id: str,
                     report_template_id: int,
                     log = regular_log.default()):
    report_template: ReportTemplate = ReportTemplate.get_by_id(session = session, id = report_template_id)
    project = Project.get_by_string_id(session, project_string_id = project_string_id)
    if not report_template:
        log['error']['report_template_id'] = 'Report template not found'
        return None, log
    if report_template.project_id == project.id:
        log['error']['report_template_id'] = f'Report does not belong to project {project_string_id}.'
        return None, log

    result = report_template.serialize()
    return result, log
