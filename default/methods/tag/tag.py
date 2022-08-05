# OPENCORE - ADD

from methods import routes
from flask import request
from flask import jsonify
from shared.database.user import User
from shared.database.project import Project
from shared.database.project import ProjectStar
from shared.database.project import Tag
from shared.database.source_control.working_dir import WorkingDir
from shared.database.task.job.job import Job

import logging
import sys
import json
from shared.helpers import sessionMaker, query_val
from shared.helpers.permissions import LoggedIn, defaultRedirect, getUserID

from shared.permissions.general import General_permissions
from shared.permissions.project_permissions import Project_permissions
from shared.regular import regular_input



@routes.route('/api/project/<string:project_string_id>/tag/update', 
			  methods=['POST'])
@Project_permissions.user_has_project(["admin", "Editor"])
def update_tags(project_string_id):
    
    update_tags_specification = [
        {"name": {
            'default': str(time.time()),
            'kind': str
            }
        }
    ]

    log, input, untrusted_input = regular_input.master(
        request=request,
        spec_list=update_job_spec_list)

    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:
        project = Project.get(session, project_string_id)

        """
        Update tag name
        Remove a tag from system
        """


        job = Job.get_by_id(session, input['job_id'])

        out = jsonify(job=job.serialize_new(),
                      log=log)

        return out, 200


@routes.route('/api/v1/project/<string:project_string_id>/tag/new', 
			  methods=['POST'])
@Project_permissions.user_has_project(["admin", "Editor"])
def new_tag_api(project_string_id):
    
    new_tag_specification = [
        {"name": {
            'kind': str,
            'required': True
            }
        }
    ]

    log, input, untrusted_input = regular_input.master(
        request=request,
        spec_list=new_tag_specification)

    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:
        project = Project.get(session, project_string_id)

        tag = Tag.get_or_new(
            name = input.get('name'),
            project_id = project.id,
            session = session)

        if tag.id is None:
            session.add(tag)
            session.flush()

        out = jsonify(tag=tag.serialize(),
                      log=log)

        return out, 200



@routes.route('/api/v1/project/<string:project_string_id>/tag/apply', 
			  methods=['POST'])
@Project_permissions.user_has_project(["admin", "Editor"])
def apply_tag_to_object_api(project_string_id):
    
    update_tags_specification = [
        {"tag_name": {
            'kind': str,
            'required': True
            }
        },
        {"object_id": {
            'kind': int,
            'required': True
            }
        },
        {"object_type": {
            'kind': str,
            'required': True
            }
        }
    ]

    log, input, untrusted_input = regular_input.master(
        request=request,
        spec_list=update_tags_specification)

    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:
        project = Project.get(session, project_string_id)

        if input['object_type'] == 'dataset':
            dataset = WorkingDir.get(session, input['object_id'], project.id)
            log = dataset.add_tags(
                tag_list = [tag_name], session=session, project=project, log=log)

        if input['object_type'] == 'job':
            job = Job.get(session, input['object_id'], project.id)

        out = jsonify(log=log)

        return out, 200



@routes.route('/api/v1/project/<string:project_string_id>/tags/list', 
			  methods=['GET'])
@Project_permissions.user_has_project(["allow_if_project_is_public",
									   "admin", 
									   "Editor", 
									   "Viewer"])
def tag_view_by_project(project_string_id):        

	with sessionMaker.session_scope() as session:

		project = Project.get_project(session, project_string_id)
		
		tag_list = Tag.get_by_project(
            session = session,
            project_id = project.id)

		tag_list_serailized = []
		for tag in tag_list:
		    tag_list_serailized.append(tag.serialize())

		out = jsonify(	success=True,
						tag_list=tag_list_serailized)

		return out, 200, {'ContentType':'application/json'}

