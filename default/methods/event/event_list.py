# OPENCORE - ADD
from methods.regular.regular_api import *

@routes.route('/api/v1/project/<string:project_string_id>' +
			  '/event/list',
			  methods = ['POST'])
@Project_permissions.user_has_project(["admin", "Editor", "Viewer"])
def api_event_list(project_string_id):
	"""

	"""
	spec_list = [ 
		{"limit": {
			'kind': int,
			'default': 50
			}
		},
		{"kind": {
			'kind': str,
			'default': None
			}
		},
		{"date_from": {	
			'kind': 'date',
			'default': None,
			'required': False
			}
		},
		{"date_to": {	
			'kind': 'date',
			'default': None,
			'required': False
			}
		},
		{"file_id": {	
			'kind': int,
			'default': None,
			'required': False
			}
		},
		{"member_id": {	
			'kind': int,
			'default': None,
			'required': False
			}
		},
	]

	log, input, untrusted_input = regular_input.master(request=request,
													   spec_list=spec_list)
	if len(log["error"].keys()) >= 1:
		return jsonify(log=log), 400


	with sessionMaker.session_scope() as session:

		project = Project.get(session, project_string_id)		
		### MAIN
		
		event_list = Event.list(
			session = session,
			project_id = project.id,
			limit = input['limit'],
			kind = input['kind'],
			date_from_string = input['date_from'],
			date_to_string = input['date_to'],
			file_id = input['file_id'],
			member_id = input['member_id']
		    )

		event_list_serialized = []
		if event_list:
			for event in event_list:
				event_list_serialized.append(event.serialize())
		####

	return jsonify(success = True,
				   event_list = event_list_serialized), 200


