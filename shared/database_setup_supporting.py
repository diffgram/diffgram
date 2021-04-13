# OPEN CORE - ADD
from shared.database.discussion.discussion_comment import DiscussionComment
from shared.database.discussion.discussion import Discussion

from shared.database.project_directory_list import Project_Directory_List

from shared.database.event.event import Event

from shared.database.deletion import Deletion

from shared.database.auth.member import Member
from shared.database.auth.api import Auth_api

from shared.database.task.guide import Guide
from shared.database.task.job.job import Job
from shared.database.task.task import Task

from shared.database.text_file import TextFile

from shared.database.source_control.file import File

from shared.database.source_control.working_dir import WorkingDir

from shared.database.video.video import Video
from shared.database.video.sequence import Sequence

from shared.database.project import Project
from shared.database.user import User
from shared.database.label import Label
from shared.database.image import Image


from shared.database.annotation.instance import Instance
from shared.database.input import Input

from shared.database.export import Export


from shared.database.attribute.attribute_template import Attribute_Template
from shared.database.attribute.attribute_template_group import Attribute_Template_Group
from shared.database.attribute.attribute_template_group_to_file import Attribute_Template_Group_to_File

from shared.database.report.report_template import ReportTemplate
from shared.database.report.report_dashboard import ReportDashboard


from shared.database.sync_events.sync_event import SyncEvent
from shared.database.connection.connection import Connection
from shared.database.external.external import ExternalMap

from shared.database.task.job.job_launch import JobLaunch, JobLaunchQueue
from shared.database.task.job.job_working_dir import JobWorkingDir
from shared.database.sync_events.sync_action_queue import SyncActionsQueue

from shared.database.notifications.notification import  Notification
from shared.database.notifications.notification_user import NotificationUser
from shared.database.notifications.notification_relation import NotificationRelation

from shared.database.batch.batch import InputBatch

from shared.database.annotation.instance_template import InstanceTemplate
from shared.database.annotation.instance_template_relation import InstanceTemplateRelation
from shared.database.userscript.userscript import UserScript
