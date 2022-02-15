# OPENCORE - ADD
from methods.regular.regular_api import *

from .report_runner import Report_Runner

"""

"""
report_view_update_api_spec = [
    {'report_template_id': {
        'kind': int,
        'required': True
    }
    },
    {'report_dashboard_id': {
        'kind': int,
        'required': False
    }
    }
]


@routes.route('/api/v1/report/view/update',
              methods = ['POST'])
@General_permissions.grant_permission_for(
    Roles = ['normal_user'],
    apis_user_list = ["builder"])
def report_view_update_api():
    """
    security model
        assumes that validate_report_permissions_scope
        checks it / returns forbidden if not applicable.


        Not sure if we want to attach report_templates 1:1 to a dashboard
        or if we want this report_view pivot.
        Either way need report_template_id  and report_dashboard_id

    """

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = report_list_api_spec)

    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        ### MAIN ###
        report_runner = Report_Runner(
            session = session,
            report_template_id = input.get('report_template_id'),
            member = None
        )

        if len(report_runner.log["error"].keys()) >= 1:
            return jsonify(log = report_runner.log), 400

        report_runner.validate_existing_report_id_permissions()

        return jsonify(log = report_runner.log), 200
