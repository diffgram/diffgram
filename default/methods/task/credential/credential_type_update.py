from methods.regular.regular_api import *

import tempfile
import os
from werkzeug.utils import secure_filename

from shared.database.task.credential.credential_type import Credential_Type

from methods.images.images_core import process_image_generic


@routes.route('/api/v1/project/<string:project_string_id>' +
              '/credential_type/edit',
              methods = ['POST'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
def credential_type_edit_api(project_string_id):
    """
    Permissions checked by project matching
    Not to sure about "edit" wording vs "update"...

    Also, we are sort of deprecating description_markdown ...
    """

    with sessionMaker.session_scope() as session:

        spec_list = [{"name": str},
                     {"description_markdown": str},
                     {"id": int},
                     {"mode": str}  # defaults to UPDATE
                     ]

        log, input, untrusted_input = regular_input.master(request = request,
                                                           spec_list = spec_list)
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        with sessionMaker.session_scope() as session:

            credential_type = Credential_Type.get_by_id(
                session = session,
                credential_type_id = input['id'])

            if credential_type is None:
                log["error"]["id"] = "Bad ID"
                return jsonify(log = log), 400

            if credential_type.project.project_string_id != project_string_id:
                log["error"]["id"] = "Permissions Issue - Bad ID"
                return jsonify(log = log), 400

            credential_type_update_core(
                session = session,
                credential_type = credential_type,
                mode = input['mode'],
                name = input['name'],
                description_markdown = input['description_markdown']
            )

            return jsonify(log = log,
                           credential_type = credential_type.serialize_for_list_view()), 200


def credential_type_update_core(
    session,
    credential_type,
    mode,
    name,
    description_markdown):
    # Default
    if mode is None or mode == "UPDATE":
        credential_type.history_cache = {
            'time_updated': str(credential_type.time_updated),
            'member_updated_id': credential_type.member_updated_id,
            'name': credential_type.name,
            'description_markdown': credential_type.description_markdown
        }

        credential_type.description_markdown = description_markdown
        credential_type.name = name

        member = get_member(session = session)
        credential_type.member_updated = member

        session.add(credential_type)

    if mode == "ARCHIVE":
        credential_type.archived = True
        session.add(credential_type)


# TODO merge with user profile route

images_allowed_file_names = [".jpg", ".jpeg", ".png"]


@routes.route('/api/v1/project/<string:project_string_id>' +
              '/credential/update/image',
              methods = ['POST'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
@limiter.limit("6 per day")
def update_credential_type_image_api(project_string_id):
    file = request.files.get('file')
    if not file:
        return "No file", 400

    log = regular_log.default_api_log()

    extension = os.path.splitext(file.filename)[1].lower()
    if extension in images_allowed_file_names:

        file.filename = secure_filename(
            file.filename)  # http://flask.pocoo.org/docs/0.12/patterns/fileuploads/
        temp_dir = tempfile.mkdtemp()
        file_name = temp_dir + "/" + file.filename
        file.save(file_name)

        credential_type_id = request.headers.get('credential_type_id')
        if credential_type_id is None:
            return "error", 400

        with sessionMaker.session_scope() as session:

            credential_type = Credential_Type.get_by_id(
                session = session,
                credential_type_id = credential_type_id)

            if credential_type is None:
                log["error"]["id"] = "Bad ID"
                return jsonify(log = log), 400

            if credential_type.project.project_string_id != project_string_id:
                log["error"]["id"] = "Permissions Issue - Bad ID"
                return jsonify(log = log), 400

            with open(file_name, "rb") as file:

                content_type = "image/" + str(extension)
                short_file_name = os.path.split(file_name)[1]

                user = User.get(session = session)

                image = process_image_generic(
                    session = session,
                    file = file,
                    file_name = short_file_name,
                    blob_base = "credentials/images/",
                    content_type = content_type,
                    extension = extension)

                credential_type.image_id = image.id
                session.add(credential_type)

            return jsonify(success = True,
                           credential_type = credential_type.serialize_for_list_view()), 200

    return jsonify(success = False), 400
