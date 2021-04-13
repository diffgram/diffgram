# OPENCORE - ADD
from methods.regular.regular_api import *


@routes.route('/api/v1/project/<string:project_string_id>/event/create',
              methods = ['POST'])
@Project_permissions.user_has_project(["admin", "Editor", "Viewer"])
def api_event_create(project_string_id):
    """

    """
    spec_list = [
        {"file_id": {
            'kind': int,
            'default': None,
            'required': False
        }
        },
        {"object_type": {
            'kind': str,
            'default': None,
            'required': True
        }
        },
        {"kind": {
            'kind': str,
            'default': None,
            'required': True
        }
        },
        {"page_name": {
            'kind': str,
            'default': None,
            'required': True
        }
        },
        {"task_id": {
            'kind': int,
            'default': None,
            'required': False
        }
        },
        {"task_template_id": {
            'kind': int,
            'default': None,
            'required': False
        }
        },
    ]

    log, input, untrusted_input = regular_input.master(request = request, spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        member = get_member(session=session)
        project = Project.get(session, project_string_id)
        event_serialized = event_create_core(
            session = session,
            task_id = input.get('task_id'),
            project = project,
            file_id = input.get('file_id'),
            member = member,
            object_type = input.get('object_type'),
            page_name = input.get('page_name'),
            kind = input.get('kind'),
            task_template_id = input.get('task_template_id'),
        )

    ####

    return jsonify(success = True,
                   created_event = event_serialized), 200


def event_create_core(session,
                      task_id = None,
                      member = None,
                      project = None,
                      object_type = None,
                      kind = None,
                      page_name = None,
                      task_template_id = None,
                      file_id = None):

    event = Event.new(
        session = session,
        task_id = task_id,
        job_id = task_template_id,
        file_id = file_id,
        kind = kind,
        member = member,
        object_type = object_type,
        project_id = project.id,
        page_name = page_name
    )
    return event.serialize()
