# OPENCORE - ADD
# Caution this file may be different from default service

import sys
import time
import json
import datetime

from dataclasses import dataclass, field
from typing import Any

from flask import jsonify
from flask import request

from shared.settings import settings

try:
	from methods import routes
except:
	from walrus.methods import routes

from shared.helpers import sessionMaker
from shared.helpers.security import limiter

from sqlalchemy.orm.attributes import flag_modified

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

from werkzeug.exceptions import Forbidden

from sqlalchemy import or_

from shared.database.event.event import Event

from shared.database.project_directory_list import Project_Directory_List
from shared.database.auth.api import Auth_api

from memory_profiler import profile

from shared.database.task.job.job import Job
from shared.database.task.task import Task

from shared.utils.logging import DiffgramLogger

walrus_abstract_logger = DiffgramLogger('walrus')
walrus_abstract_logger.configure_concrete_logger(
	system_mode = settings.DIFFGRAM_SYSTEM_MODE)
logger = walrus_abstract_logger.get_concrete_logger()

