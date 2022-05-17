import sys


from shared.helpers import sessionMaker
from shared.database.project import Project
from methods import routes

from shared.machine_learning.semantic_segmentation_data_prep import Semantic_segmentation_data_prep
from shared.permissions.project_permissions import Project_permissions




from shared.data_tools_core import Data_tools

data_tools = Data_tools().data_tools


@routes.route('/api/walrus/project/<string:project_string_id>/data/masks/generate',
              methods = ['GET'])
@Project_permissions.user_has_project(["admin"])
def generate_mask_by_project_id(project_string_id):
    # TODO use a thread, this is a long running process

    semantic_segmentation_data_prep = Semantic_segmentation_data_prep()

    with sessionMaker.session_scope() as session:
        project = Project.get(session, project_string_id)
        type = "joint"
        # type = "binary"
        semantic_segmentation_data_prep.generate_mask_core(
            session, project, type)

    return "ok", 200, {'ContentType': 'application/json'}



