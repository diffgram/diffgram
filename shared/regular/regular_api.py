import sys
import time
import json
import datetime

from dataclasses import dataclass, field
from typing import Any

from shared.settings import settings
from shared.helpers import sessionMaker

from shared.database.auth.member import Member
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

from shared.database.labels.label_schema import LabelSchema
from shared.utils.logging import DiffgramLogger

abstract_logger = DiffgramLogger('shared')
abstract_logger.configure_concrete_logger(
	system_mode = settings.DIFFGRAM_SYSTEM_MODE)
logger = abstract_logger.get_concrete_logger()
