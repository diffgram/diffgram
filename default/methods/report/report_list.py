# Import necessary modules and classes
from methods.regular.regular_api import *
from .report_runner import Report_Runner

# Define the specification for the report list API, including validation for input parameters
report_list_api_spec = [
    {
        'scope': {
            'default': 'project',
            'kind': str,
            'required': False,
            'valid_values_list': ['project']
        }
    },
    {
        'project_string_id': {
            'kind': str,
            'required': False
        }
    },
    {
        'report_dashboard_id': {
            'kind': int,
            'required': False
        }
    },
    {
        'only_is_visible_on_report_dashboard': {
            'kind': bool,
            'default': None
        }
    }
]

# Define the API route and its corresponding HTTP method
@routes.route('/api/v1/report/template/list', methods=['POST'])

# Grant permission to specific roles and users for this API
@General_permissions.grant_permission_for(
    Roles=['normal_user'],
    apis_user_list=["api_enabled_builder"]
)
def report_list_api():
    """
    This function is the API endpoint for retrieving a list of report templates based on the provided input parameters.

    It first validates and sanitizes the input using the `regular_input.master()` function. If there are any errors during input validation, it returns a bad request response with the error log.

    Then, it creates a session and initializes the Report_Runner class to interact with the database and perform necessary operations. If there are any errors during this process, it returns a bad request response with the error log.

    Next, it validates the report permissions scope based on the input parameters.

    After that, it retrieves the list of report templates based on the report dashboard ID and whether the report is only visible on the report dashboard.

    It then serializes the report templates into a list of dictionaries and adds a success flag to the log.

    Finally, it returns the report template list and the log as a JSON response with a 200 status code.

    """
    log, input, untrusted_input = regular_input.master(
        request=request,
        spec_list=report_list_api_spec)

    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:
        report_runner = Report_Runner(
            session=session,
            member=None
        )

        if len(report_runner.log["error"].keys()) >= 1:
            return jsonify(log=report_runner.log), 400

        report_runner.validate_report_permissions_scope(
            scope=input.get('scope'),
            project_string_id=input.get('project_string_id')
        )

        report_template_list = report_runner.report_template_list(
            report_dashboard_id=input.get('report_dashboard_id'),
            only_is_visible_on_report_dashboard=input.get(
                'only_is_visible_on_report_dashboard')
        )

        report_template_list_serialized = []
        for report_template in report_template_list:
            report_template_list_serialized.append(report_template.serialize())

        log['success'] = True

        return jsonify(report_template_list=report_template_list_serialized,
                        log=report_runner.log), 200
