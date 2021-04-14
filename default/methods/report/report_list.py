# OPENCORE - ADD
from methods.regular.regular_api import *

from .report_runner import Report_Runner


"""
Some of these can be similar to what's in report runner
But here just getting existing ones.
The only thing needed is one of the report scopes, otherwise
rest we can add on later as future filtering options.
"""
report_list_api_spec = [
	{'scope' : {
		'default': 'project',
		'kind': str,
		'required': False,
		'valid_values_list': ['project']
		}
	},
	{'project_string_id' : {
		'kind': str,
		'required': False
		}
	},
	{'report_dashboard_id' : {
		'kind': int,
		'required': False
		}
	},
	{'only_is_visible_on_report_dashboard' : {
		'kind': bool,
		'default': None
		}
	}
	
	]

@routes.route('/api/v1/report/template/list', 
			  methods=['POST'])
@General_permissions.grant_permission_for(
	Roles = ['normal_user'],
	apis_user_list = ["api_enabled_builder"])
def report_list_api():
	"""

	security model assumes that validate_report_permissions_scope
	checks it / returns forbidden if not applicable.

	"""

	log, input, untrusted_input = regular_input.master(
		request=request,
		spec_list=report_list_api_spec)

	if len(log["error"].keys()) >= 1:
		return jsonify(log=log), 400

	with sessionMaker.session_scope() as session:  
	    	
		### MAIN ###
		report_runner = Report_Runner(
			session = session,
			member = None
			)

		if len(report_runner.log["error"].keys()) >= 1:
			return jsonify(log=report_runner.log), 400

		# In the future we could have additional
		# items passed here, but makes sense to reuse this.
		report_runner.validate_report_permissions_scope(
			scope = input.get('scope'),
			project_string_id = input.get('project_string_id')
			)

		# TODO caching

		report_template_list = report_runner.report_template_list(
			report_dashboard_id = input.get('report_dashboard_id'),
			only_is_visible_on_report_dashboard = input.get(
				'only_is_visible_on_report_dashboard') )

		report_template_list_serialized = []
		for report_template in report_template_list:
			report_template_list_serialized.append(report_template.serialize())
		
		log['success'] = True

		return jsonify( report_template_list = report_template_list_serialized, 
						log = report_runner.log), 200



# future, could have a list of dashboards here 
# (result is dashboards not report templates)
# if we end up support multiple dashboards
#@routes.route('/api/v1/report/dashboard/list', 
