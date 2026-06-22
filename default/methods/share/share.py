# OPENCORE - ADD
from methods.regular.regular_api import regular_input
from shared.database.user import Signup_code, UserbaseProject, User
from shared.database.user import Member, Project_permissions
from shared.database.auth.api import Auth_api
from shared.database.deletion import Deletion
from shared.feature_flags.feature_checker import FeatureChecker
from shared.regular.regular_log import log_has_error
from shared.database.project_perms import ProjectDefaultRoles, ProjectRolesPermissions
from shared.database.permissions.roles import RoleMemberObject, ValidObjectTypes, Role
from flask import jsonify, request, sessionMaker
from typing import Dict, List, Union
import settings
from shared.communication import communicate_via_email


@routes.route('/api/project/<string:project_string_id>/share', methods=['POST'])
@Project_permissions.user_has_project(["admin"])
def share_member_project_api(project_string_id) -> jsonify:
    """
    Adds a user to a project
    Checks
    1. User adding has permission to add user to project (ie is admin)
    
