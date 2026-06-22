# OPENCORE - ADD
import sys
import time
import json
import datetime
from dataclasses import dataclass, field
from typing import Any

from flask import Flask, request, jsonify
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import or_

import shared.settings as settings
from shared.helpers import sessionMaker
from shared.helpers.security import limiter

from shared.database.user import User
from shared.database.project import Project
from shared.database.source_control.working_dir import WorkingDir
from shared.database.source_control.working_dir import WorkingDirFileLink

from shared.database.source_control.file import File
from shared.database.annotation.instance import Instance

from shared.regular import regular_input
from shared.regular import regular_log
from shared.regular import regular_methods
from shared.regular.regular_member import get_member

from shared.communicate.email import communicate_via_email

from shared.permissions.project_permissions import Project_permissions
from shared.permissions.job_permissions import Job_permissions
from shared.permissions.task_permissions import Permission_Task
from shared.permissions.general import General_permissions
from shared.permissions.task_or_project_permissions import PermissionTaskOrProject

from shared.database.task.job.job import Job
from shared.database.task.task import Task

from shared.database.auth.api import Auth_api

from werkzeug.exceptions import Forbidden

from shared.database.event.event import Event

from shared.database.project_directory_list import Project_Directory_List


app = Flask(__name__)

# Add routes here
__all__ = [
    "routes",
]

@app.before_request
def before_request():
    if not request.path.startswith("/static"):
        limiter.check(request.remote_addr)

@app.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "Hello, World!"})

if __name__ == "__main__":
    app.run(debug=True)
