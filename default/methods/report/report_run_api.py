from methods.regular.regular_api import *
from shared.database.report.report_template import ReportTemplate
from .report_runner import Report_Runner
from sqlalchemy.orm.session import Session


@routes.route('/api/v1/report/run',
              methods = ['POST'])
@General_permissions.grant_permission_for(['normal_user'])
def run_report_api():

    spec_list = [
        {"report_template_id": {
            'kind': int,
            'required': False
        }
        },
        {"report_template_data": {
            'kind': dict,
            'required': False
        }
        },
        {"project_string_id": {
            'kind': str,
            'default': None,
            'required': False
        }
        }
    ]

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = spec_list)

    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400
    if input.get('report_template_id') is None and input.get('report_template_data') is None:
        log['error']['report_template'] = 'Provide report_template_id or report_template_data'
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        report_runner = Report_Runner(
            session = session,
            member = None,
            report_template_id = input['report_template_id'],
            report_template_data = input['report_template_data'],
            project_string_id = input['project_string_id']
        )

        if len(report_runner.log["error"].keys()) >= 1:
            return jsonify(log = report_runner.log), 400

        report_runner.get_existing_report_template(input['report_template_id'])

        """
        For Diffgram wide reports, they only need to validate the project string id
        BUT if it's not, then the project_string_id should match too.
        """
        if report_runner.report_template is not None:
            if report_runner.report_template.diffgram_wide_default is True:
                report_runner.validate_existing_report_id_permissions(
                    project_string_id = input['project_string_id'])
            else:
                # This assume project based...
                # this should be part of that other permission scope validation.
                if report_runner.report_template.project.project_string_id != input['project_string_id']:
                    raise Forbidden("No access to this project.")

                report_runner.validate_existing_report_id_permissions(
                    project_string_id = input['project_string_id'])
        else:
            # Case where not report_template_id is provided (only report_template_data)
            Project_permissions.user_has_project(Roles = ["admin", "Editor", "Viewer"])
        results = report_runner.run()

        if len(report_runner.log["error"].keys()) >= 1:
            return jsonify(log = report_runner.log), 400

        log['success'] = True
        return jsonify(log = report_runner.log,
                       report_template = report_runner.report_template.serialize(),
                       report = results,
                       stats = results), 200
