# OPENCORE - ADD
from methods.regular.regular_api import *


@routes.route('/api/project/<string:project_string_id>' +
              '/user/<string:username>' +
              '/working_dir/view',
              methods = ['get'])
@Project_permissions.user_has_project(["admin", "Editor"])
def view_working_dir_web(project_string_id, username):
    """
    Strictly viewing the stats / info for working dir NOT files

    CAUTION uses project.directory_default
    """

    with sessionMaker.session_scope() as session:

        if project_string_id is None:
            return "no project string id", 400

        project = Project.get(session, project_string_id)

        working_dir_name = request.args.get('name')
        working_dir_id = request.args.get('working_dir_id')
        working_dir_ids = request.args.getlist('working_dir_ids[]')

        if working_dir_id or working_dir_name:
            logger.debug('Fetching single directory')

            query = session.query(WorkingDir)

            if working_dir_name:
                query = query.filter(WorkingDir.nickname == working_dir_name)
            if project:
                query = query.filter(WorkingDir.project_id == project.id)

            if working_dir_id:
                query = query.filter(WorkingDir.id == working_dir_id)

            working_dir = query.first()

            if working_dir is None:
                logger.warning('Warning request did not find any directories from given input')
                return "Dataset not found", 400
            if working_dir.project_id != project.id:
                return "Dataset not in project", 400
            out = jsonify(success = True,
                          working_dir = working_dir.serialize())
        elif working_dir_ids:
            logger.info(f"Fetching multiple directories {str(working_dir_ids)}")
            working_dirs = session.query(WorkingDir).filter(WorkingDir.id.in_(working_dir_ids)).all()

            if working_dirs is None:
                logger.warning('Warning request did not find any directories from given input')
                return "Dataset not found", 400
            projec_in_dir_conditions = [x.project_id == project.id for x in working_dirs]
            if not all(projec_in_dir_conditions):
                return "Dataset not in project", 400
            out = jsonify(success = True,
                          working_dir = [working_dir.serialize() for working_dir in working_dirs])
        else:
            working_dir = project.directory_default

            out = jsonify(success = True,
                          working_dir = working_dir.serialize())
        return out, 200, {'ContentType': 'application/json'}