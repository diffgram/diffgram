# OPENCORE - ADD
from methods.regular.regular_api import *

from .report_runner import Report_Runner

report_view_update_api_spec = [
    {"report_template_id": {"kind": int, "required": True}},
    {"report_dashboard_id": {"kind": int, "required": False}},
]

@routes.route("/api/v1/report/view/update", methods=["POST"])
@General_permissions.grant_permission_for(
    Roles=["normal_user"], apis_user_list=["builder"]
)
def report_update_api() -> tuple[dict, int]:
    """
    Update a report view.

    security model
        assumes that validate_report_permissions_scope
        checks it / returns forbidden if not applicable.

        Not sure if we want to attach report_templates 1:1 to a dashboard
        or if we want this report_view pivot.
        Either way need report_template_id  and report_dashboard_id

    Returns:
        A dictionary containing the log of the API call and the HTTP status code.
    """

    log, input, untrusted_input = regular_input.master(
        request=request, spec_list=report_list_api_spec
    )

    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    if "report_template_id" not in input or input["report_template_id"] is None:
        return jsonify(log={"error": {"report_template_id": ["This field is required."]}}), 400

    with sessionMaker.session_scope() as session:

        report_runner = Report_Runner(
            session=session,
            report_template_id=input["report_template_id"],
            member=None,
        )

        log = report_runner.log

        if len(log["error"].keys()) >= 1:
            return jsonify(log=log), 400

        report_runner.validate_existing_report_id_permissions()

        log = report_runner.log

        if len(log["error"].keys()) >= 1:
            return jsonify(log=log), 400

        return jsonify(log=log, message="Report view updated successfully."), 200
