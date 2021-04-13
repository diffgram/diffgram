# OPENCORE - ADD
from methods.regular.regular_api import *

@routes.route('/api/v1/project/<string:project_string_id>' +
              '/directory/list',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor", "Viewer"],
    apis_user_list=['api_enabled_builder', 'security_email_verified'])
def list_directory_api(project_string_id):
    """
    Keeping with directory convention until we do bulk name to
    "dataset"

    """
    spec_list = [       
        	{"nickname": {
			'kind': str,
            'required': False
			}
		},
        	{"limit": {
			'kind': int,
			'default': 100
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
		}
    ]

    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)

        directory_list = WorkingDir.list(
            session = session,
            project_id = project.id,
            limit = input['limit'],
            	date_from_string = input['date_from'],
			date_to_string = input['date_to'],
            nickname = input['nickname'],
            order_by_class_and_attribute = WorkingDir.created_time
            )

        directory_list_serialized = []
        if directory_list:
            for directory in directory_list:
                directory_list_serialized.append(directory.serialize())

        log['success'] = True

        out = jsonify(log=log,
                      directory_list = directory_list_serialized)
        return out, 200

