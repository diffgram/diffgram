from methods.regular.regular_api import *
from shared.database.report.report_template import ReportTemplate
from .report_runner import Report_Runner
from sqlalchemy.orm.session import Session


@routes.route('/api/v1/report/save',
              methods = ['POST'])
@General_permissions.grant_permission_for(['normal_user'])
def report_save_api():
    """
        May or may not have an ID if it's new.

        metadata meaning it's data one level removed from actual report
        ie how the report should be structured
        see report_spec for an example

    """
    spec_list = [
        {"report_template_id": {
            'kind': int,
            'required': False  # (ie for first save)
        }
        },
        {'metadata': dict}
    ]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        report_runner = Report_Runner(
            session = session,
            member = None,
            report_template_id = input['report_template_id'],
            metadata = input['metadata']
        )

        if len(report_runner.log["error"].keys()) >= 1:
            return jsonify(log = report_runner.log), 400

        # TODO abstract this check into a better function to share with running it
        if input['metadata'].get('diffgram_wide_default') is True:

            # TODO edge case of default wide === false (After
            # prior being True) is not handled yet

            user = User.get(session)
            if user is None or user.is_super_admin is not True:
                log['error']['permission'] = "'diffgram_wide_default' Invalid permission."
                return jsonify(log = log), 400
        else:
            report_runner.validate_report_permissions_scope(
                scope = input['metadata'].get('scope'),
                project_string_id = input['metadata'].get('project_string_id'),
            )

        report_runner.save()

        if len(report_runner.log["error"].keys()) >= 1:
            return jsonify(log = report_runner.log), 400

        report_runner.log['success'] = True

        return jsonify(
            log = report_runner.log,
            report_template = report_runner.report_template.serialize()), 200
