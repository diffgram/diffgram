# This script is part of the OpenCore project and is responsible for adding report-related APIs.
# It imports necessary modules and classes, including regular_api from methods.regular package,
# ReportTemplate and Report_Runner from shared.database.report package, and Session from
# sqlalchemy.orm.session.

# The report_view_api function is a view function for the API endpoint '/api/v1/project/<string:project_string_id>/report/<int:report_template_id>'
# It handles GET requests and checks for user permissions using General_permissions.grant_permission_for decorator.
# It takes project_string_id and report_template_id as input arguments and returns report template data in JSON format.

# The report_view_core function is the core function that retrieves report template data for the given project and report template IDs.
# It takes session, project_string_id, report_template_id, and log as input arguments and returns report template data and log.

# The report_info_api function is a view function for the API endpoint '/api/v1/report/info/<int:report_template_id>'
# It handles GET requests and retrieves report template information for the given report template ID.
# It takes report_template_id as input argument and returns report template data and log in JSON format.

# The Report_Runner class is used to run and validate report templates.
# It takes session, member, and report_template_id as input arguments and has methods to get existing report template,
# validate permissions, and serialize report template data.
