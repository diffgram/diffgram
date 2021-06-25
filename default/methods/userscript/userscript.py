try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *

from shared.database.userscript.userscript import UserScript


"""
Assumption about is_public
1) We don't save it on new
2) On update, we check if user is super admin before saving it
"""


@routes.route('/api/v1/project/<string:project_string_id>/userscript/new', 
              methods = ['POST'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor"], 
    apis_user_list = ["api_enabled_builder"])
def userscript_new_api(project_string_id):
    
    userscript_new_spec_list = [
        {"name" : {
		    'default': str(time.time()),
		    'kind': str
		    }
	    },

        {"code" : {
		    'default': None,
		    'kind': str,
            'allow_empty': True
		    }
	    },

        {"language" : {
		    'default': None,
		    'kind': str,
            'valid_values_list': ['javascript']
		    }
	    },
        {"external_src_list" : {
		    'default': None,
		    'kind': list,
            'allow_empty': True
		    }
	    },
        {"client_created_time" : {
		    'default': None,
		    'kind': datetime,
		    }
	    },
        {"client_creation_ref_id" : {
		    'default': None,
		    'kind': str,
		    }
	    }
    ]
    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = userscript_new_spec_list)
    if len(log["error"].keys()) >= 1: return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        userscript = __userscript_new(
            session = session, 
            input = input,
            project_string_id = project_string_id)

        log['success'] = True

        return jsonify(
            userscript = userscript.serialize(),
            log = log), 200


def __userscript_new(
        session,
        input,
        project_string_id,
        do_add_to_session = True):

    userscript = UserScript.new(
        member = get_member(session),
        project = Project.get(session, project_string_id),
        client_created_time = input['client_created_time'],
        client_creation_ref_id = input['client_creation_ref_id'],
        name = input['name'],
        code = input['code'],
        external_src_list = input['external_src_list'],
        language = input['language']
        )

    if do_add_to_session is True:
        session.add(userscript)
        session.flush() # For ID

    return userscript



@routes.route('/api/v1/project/<string:project_string_id>/userscript/update', 
              methods = ['POST'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor"], 
    apis_user_list = ["api_enabled_builder"])
def userscript_update_api(project_string_id):
    
    userscript_update_spec_list = [
        {"id" : {
		    'kind': int,
            'required': True
		    }
	    },

        {"name" : {
		    'kind': str,
            'required': False
		    }
	    },

        {"code" : {
		    'kind': str,
            'required': False,
            'default': None,
            'allow_empty': True
		    }
	    },

        {"language" : {
		    'kind': str,
            'valid_values_list': ['javascript'],
            'required': False
		    }
	    },
        {"external_src_list" : {
		    'required': False,
		    'kind': list,
            'allow_empty': True
		    }
	    },
        {"archived" : {
		    'required': False,
		    'kind': bool
		    }
	    },
        {"is_visible" : {
		    'required': False,
		    'kind': bool
		    }
	    },
        {"is_public" : {
		    'required': False,
		    'kind': bool,
		    }
	    }
    ]
    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = userscript_update_spec_list)
    if len(log["error"].keys()) >= 1: return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        log, userscript = __userscript_update(
            session = session, 
            input = input,
            log = log,
            project_string_id = project_string_id)

        if len(log["error"].keys()) >= 1: return jsonify(log = log), 400

        log['success'] = True

        return jsonify(
            userscript = userscript.serialize(), 
            log = log), 200


def __userscript_update(
        session,
        input,
        project_string_id,
        log,
        do_add_to_session = True):

    userscript = UserScript.get_by_id(
        session = session,
        id = input['id'])

    if userscript is None:
        log['error']['id'] = "Does not exist"
        return log, False

    # Now update or add the rest of the fields
    fields_to_process = {
        'name': input['name'],
        'code': input['code'],
        'external_src_list': input['external_src_list'],
        'archived': input['archived'],
        'is_visible': input['is_visible'],
        'language': input['language'],
    }

    user = User.get(session)
    if user and user.is_super_admin is True:
        fields_to_process['is_public'] = input['is_public']


    for field_key, field_val in fields_to_process.items():

        if getattr(userscript, field_key) != field_val:
            setattr(userscript, field_key, field_val)
            log['info'][field_key] = "Updated {}".format(field_key)

    if do_add_to_session is True:
        session.add(userscript)

    return log, userscript



@routes.route('/api/v1/project/<string:project_string_id>' +
              '/userscript/list',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor", "Viewer"],
    apis_user_list=['api_enabled_builder', 'security_email_verified', 'allow_if_project_is_public'])
def list_userscript_api(project_string_id):
    """

    """
    spec_list = [       
        	{"name": {
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
		},
        	{"archived": {	
			'kind': bool,
			'default': False,
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

        userscript_list = UserScript.list(
            session = session,
            project_id = project.id,
            limit = input['limit'],
            	date_from_string = input['date_from'],
			date_to_string = input['date_to'],
            name = input['name'],
            order_by_class_and_attribute = UserScript.time_updated,
            archived = input['archived'],
            public_only = False
            )
     
        public_list = UserScript.list(
            session = session,
            public_only = True,
            order_by_class_and_attribute = UserScript.time_updated,
            archived = False
            )

        userscript_list.extend(public_list)

        userscript_list_serialized = []
        if userscript_list:
            for userscript in userscript_list:
                userscript_list_serialized.append(userscript.serialize())

        log['success'] = True

        out = jsonify(log=log,
                      userscript_list = userscript_list_serialized)
        return out, 200
