try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *

from shared.database.ui_schema.ui_schema import UI_Schema

ui_schema_button_spec_list = [
    {"visible": {
        'default': True,
        'kind': bool
    }
    },
    {"style": {
        'default': None,
        'kind': str,
        'required': False
    }
    },
    {"allowed_instance_types": {
        'default': None,
        'kind': dict,
        'required': False
    }
    }
]

ui_schema_logo_spec_list = [
    {"url": {
        'default': None,
        'kind': str,
        'required': False
    }
    }
]

ui_schema_logo_spec_list.extend(ui_schema_button_spec_list)

all_ui_schema_specs = {
    'logo': ui_schema_logo_spec_list,

    'global_theme': ui_schema_button_spec_list,
    'home': ui_schema_button_spec_list,
    'undo': ui_schema_button_spec_list,
    'redo': ui_schema_button_spec_list,
    'complete': ui_schema_button_spec_list,
    'defer': ui_schema_button_spec_list,
    'zoom': ui_schema_button_spec_list,
    'label_selector': ui_schema_button_spec_list,
    'instance_selector': ui_schema_button_spec_list,
    'edit_instance_template': ui_schema_button_spec_list,
    'draw_edit': ui_schema_button_spec_list,
    'save': ui_schema_button_spec_list,
    'next_task': ui_schema_button_spec_list,
    'previous_task': ui_schema_button_spec_list,
    'guide': ui_schema_button_spec_list,
    'brightness_contrast_filters': ui_schema_button_spec_list,
    'hotkeys': ui_schema_button_spec_list,
    'overflow_menu': ui_schema_button_spec_list,
    'settings': ui_schema_button_spec_list,

    'attributes': ui_schema_button_spec_list,
    'instances': ui_schema_button_spec_list,
    'userscripts': ui_schema_button_spec_list,
    'nav_bar': ui_schema_button_spec_list,
    'left_bar': ui_schema_button_spec_list,

    'main_canvas': ui_schema_button_spec_list,

    'label_settings': ui_schema_button_spec_list,

    'allow_actions': ui_schema_button_spec_list,
    'block_actions': ui_schema_button_spec_list,
    'time_tracking': ui_schema_button_spec_list,

}


@routes.route('/api/v1/project/<string:project_string_id>/ui_schema/new',
              methods = ['POST'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor"],
    apis_user_list = ["api_enabled_builder"])
def ui_schema_new_api(project_string_id):
    ui_schema_new_spec_list = [
        {"name": {
            'default': str(time.time()),
            'kind': str
        }
        },
        {"client_created_time": {
            'default': None,
            'kind': datetime,
        }
        },
        {"client_creation_ref_id": {
            'default': None,
            'kind': str,
        }
        }
    ]
    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = ui_schema_new_spec_list)
    if regular_log.log_has_error(log): return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        ui_schema = __ui_schema_new(
            session = session,
            input = input,
            project_string_id = project_string_id)

        log['success'] = True

        return jsonify(
            ui_schema = ui_schema.serialize(),
            log = log), 200


def __ui_schema_new(
    session,
    input,
    project_string_id,
    do_add_to_session = True):
    ui_schema = UI_Schema.new(
        member_created = get_member(session),
        project = Project.get(session, project_string_id),
        client_created_time = input['client_created_time'],
        creation_ref_id = input['client_creation_ref_id'],
        name = input['name']
    )

    if do_add_to_session is True:
        session.add(ui_schema)
        session.flush()  # For ID

    return ui_schema


@routes.route('/api/v1/project/<string:project_string_id>/ui_schema/update',
              methods = ['POST'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor"],
    apis_user_list = ["api_enabled_builder"])
def ui_schema_update_api(project_string_id):
    ui_schema_update_spec_list = [
        {"id": {
            'kind': int,
            'required': True
        }
        },

        {"name": {
            'kind': str,
            'required': False
        }
        },
        {"archived": {
            'required': False,
            'kind': bool
        }
        },
        {"is_visible": {
            'required': False,
            'kind': bool
        }
        },
        {"is_public": {
            'required': False,
            'kind': bool,
        }
        }
    ]
    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = ui_schema_update_spec_list)
    if len(log["error"].keys()) >= 1: return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        log, ui_schema = __ui_schema_update(
            session = session,
            input = input,
            untrusted_input = untrusted_input,
            log = log,
            project_string_id = project_string_id)

        if regular_log.log_has_error(log): return jsonify(log = log), 400

        log['success'] = True

        return jsonify(
            ui_schema = ui_schema.serialize(),
            log = log), 200


def __ui_schema_update(
    session,
    input,
    untrusted_input,
    project_string_id,
    log,
    do_add_to_session = True):
    ui_schema = UI_Schema.get_by_id(
        session = session,
        id = input['id'])

    if ui_schema is None:
        log['error']['id'] = "Does not exist"
        return log, False

    # Now update or add the rest of the fields
    fields_to_process = {
        'name': input['name'],
        'archived': input['archived'],
        'is_visible': input['is_visible']
    }

    for key, value in all_ui_schema_specs.items():
        if untrusted_input.get(key):

            log, result = regular_input.input_check_many(
                spec_list = value,
                log = log,
                untrusted_input = untrusted_input[key])

            if regular_log.log_has_error(log):
                return log, False

            fields_to_process[key] = result

    user = User.get(session)
    if user and user.is_super_admin is True:
        fields_to_process['is_public'] = input['is_public']

    for field_key, field_val in fields_to_process.items():

        if getattr(ui_schema, field_key) != field_val:
            setattr(ui_schema, field_key, field_val)
            log['info'][field_key] = "Updated {}".format(field_key)

    if do_add_to_session is True:
        session.add(ui_schema)

    return log, ui_schema


@routes.route('/api/v1/project/<string:project_string_id>' +
              '/ui_schema/list',
              methods = ['POST'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor", "Viewer", "allow_if_project_is_public"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
def list_ui_schema_api(project_string_id):
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

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = spec_list)
    if regular_log.log_has_error(log): return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)

        ui_schema_list = UI_Schema.list(
            session = session,
            project_id = project.id,
            limit = input['limit'],
            date_from_string = input['date_from'],
            date_to_string = input['date_to'],
            name = input['name'],
            order_by_class_and_attribute = UI_Schema.last_updated_time,
            archived = input['archived'],
            public_only = False
        )

        public_list = UI_Schema.list(
            session = session,
            public_only = True,
            order_by_class_and_attribute = UI_Schema.last_updated_time,
            archived = False
        )

        ui_schema_list.extend(public_list)

        ui_schema_list_serialized = []
        if ui_schema_list:
            for ui_schema in ui_schema_list:
                ui_schema_list_serialized.append(ui_schema.serialize())

        log['success'] = True

        out = jsonify(log = log,
                      ui_schema_list = ui_schema_list_serialized)
        return out, 200
