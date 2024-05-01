from flask import Flask, jsonify, request, abort
from flask_restplus import Resource, Namespace
from typing import Dict, List, Union, Optional
from datetime import datetime
from your_module.methods.regular.regular_api import get_member, Project_permissions
from your_module.shared.database.userscript.userscript import UserScript, Project
from your_module.shared.database.session import sessionMaker

app = Flask(__name__)
api = Namespace('userscript', description='Operations related to userscript')

@api.route('/new/<string:project_string_id>')
class UserscriptNewAPI(Resource):
    @api.doc('create_userscript')
    @Project_permissions.user_has_project(
        Roles=["admin", "Editor"],
        apis_user_list=["api_enabled_builder"])
    def post(self, project_string_id):
        """Create a new userscript for the given project"""
        userscript_new_spec_list = [
            {"name": {
                'default': str(time.time()),
                'kind': str
                }
            },
            {"code": {
                'default': None,
                'kind': str,
                'allow_empty': True
                }
            },
            {"language": {
                'default': None,
              
