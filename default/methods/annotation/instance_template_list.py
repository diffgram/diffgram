from typing import List, Dict, Union, Optional
from flask import jsonify, request, Blueprint
from flask_restplus import Namespace, Resource
from sqlalchemy.orm import Session
from sqlalchemy import or_
from shared.database.project import Project
from shared.database.labels.label_schema import LabelSchema
from shared.database.annotation.instance_template import InstanceTemplate
from shared.annotation import Annotation_Update
from shared.database.annotation.instance_template_relation import InstanceTemplateRelation

app = Blueprint('api', __name__)
api = Namespace('api', description='API namespace')

@app.route('/api/v1/project/<string:project_string_id>/instance-template/list', methods=['POST'])
@Project_permissions.user_has_project(roles=["admin", "Editor", "Viewer", "allow_if_project_is_public", "annotator"],
                                      apis_user_list=["api_enabled_builder"])
class ListInstanceTemplateAPI(Resource):
    """
    Fetch the list of instance templates in the project.
    """

    @api.expect({'schema_id': {'required': True, 'type': 'integer'}})
    @api.response(200, 'List of instance templates returned.')
    @api.response(400, 'Bad request.')
    def post(self, project_string_id):
        schema_id = request.json['schema_id']

        with Session() as session:
            project = Project.get_by_string_id(session, project_string_id)
            instance_template_data, log = self.list_instance_templates_core(session, project, schema_id)
            if log:
                return jsonify(log=log), 400

            return jsonify(instance_template_list=instance_template_data), 200

    def list_instance_templates_core(self, session: Session, project: Project, schema_id: int) -> Optional[List[Dict]]:
        """
        Returns a list of serialized instances templates matching the given project.
        """
        success = True
        log: Dict[str, Union[str, Dict]] = {}
        schema = LabelSchema.get_by_id(session, schema_id, project.id)
        if schema.project_id != project.id:
            log['error'] = {'schema_id': 'Schema does not belong to project'}
            success = False
        else:
            instance_template_list = InstanceTemplate.list(session=session, project=project, schema=schema)
            if instance_template_list:
                instance_template_data = [template.serialize(session) for template in instance_template_list]
            else:
                instance_template_data = []
                log['warning'] = {'instance_template_list': 'No instance templates found.'}
                success = False

        if not success:
            return None, log
        return instance_template_data, log
