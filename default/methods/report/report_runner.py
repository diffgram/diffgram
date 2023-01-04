try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *

from sqlalchemy import func
import datetime
import threading

from methods.report.custom_reports.TimeSpentReport import TimeSpentReport
from methods.report.custom_reports.AnnotatorPerformanceReport import AnnotatorPerformanceReport
from methods.report.custom_reports.TaskReportRejectRatioReport import TaskReportRejectRatioReport
from shared.database.annotation.instance import Instance
from shared.database.source_control.file import File
from shared.database.task.task_event import TaskEvent
from shared.database.task.task_time_tracking import TaskTimeTracking

from shared.permissions.super_admin_only import Super_Admin
from shared.database.report.report_template import ReportTemplate
from shared.database.report.report_dashboard import ReportDashboard
from shared.database.auth.member import Member


class InitQuery:
    base: None
    group_by : None
    group_by_str : str
    second_group_by : None
    second_group_by_str : str
    distinct : bool

    def __init__(self):
        self.distinct = False
        self.second_group_by = None     # SQLAlchemy statements don't have good bool check so use _str instead
        self.group_by = None
        self.second_group_by_str = None
        self.group_by_str = None

report_spec_list = [

    {'name': {
        'default': 'My Report',
        'kind': str,
        'required': False
    }
    },

    {'member_list': {
        'default': [],
        'kind': list,
        'allow_empty': True,
        'required': False
    }
    },

    # Continue pattern of using project_string_id (instead of id)
    # Can use project for permissions to
    # That's why neither is required
    {'project_string_id': {
        'kind': str,
        'required': False
    }
    },
    {'item_of_interest': {
        'kind': str,
        'required': True,
        'valid_values_list': ['instance', 'file', 'event', 'task', 'time_spent_task', 'annotator_performance']
    }
    },

    {'scope': {
        'default': 'project',
        'kind': str,
        'required': False,
        'valid_values_list': ['project', 'Project']
    }
    },

    {'date_from': {
        'kind': str,
        'required': False
    }
    },
    {'date_to': {
        'kind': str,
        'required': False
    }
    },
    {"period": {
        'kind': str,
        'required': False
    }
    },

    {"date_period_unit": {
        'kind': str,
        'required': False
    }
    },

    {"compare_to_previous_period": {
        'default': False,
        'kind': bool,
        'required': False
    }
    },

    {"second_group_by": {
        'kind': str,
        'required': False
    }
    },

    {"job_id": {
        'default': None,
        'kind': int,
        'required': False
    }
    },

    {"archived": {
        'default': False,
        'kind': bool,
        'required': False
    }
    },

    {"label_file_id_list": {
        'default': None,
        'kind': list,
        'required': False
    }
        # TODO assert list contains ints?
        # ie we expect [123, 123]
    },
    {"group_by": {
        'default': 'date',
        'kind': str,
        'required': False,
        'valid_values_list': ['date', 'label', 'user', 'task', None, 'file', 'task_status'],
    }
    },
    {"task_event_type": {
        'default': 'date',
        'kind': str,
        'required': False,
        'valid_values_list': ['all', 'task_created', 'task_completed', 'task_request_changes', 'task_review_start', 'task_review_complete'],
    }
    },
    {"directory_id_list": {
        'default': None,
        'kind': list,
        'required': False
    }
    },
    {"view_type": {
        'default': 'count',
        'kind': str,
        'valid_values_list': ['count', 'rows', 'chart']
    }
    },
    {"view_sub_type": {
        'default': 'bar',
        'kind': str,
        'valid_values_list': ['bar', 'line']
    }
    },
    {"diffgram_wide_default": {
        'default': False,
        'kind': bool,
    }
    },
    {"is_visible_on_report_dashboard": {
        'default': False,
        'kind': bool,
    }
    },
    {"job_id": {
        'default': None,
        'kind': int,
    }
    },
    {"task_id": {
        'default': None,
        'kind': int,
    }
    }
    # See update_report_template () for where metadata get loaded
]



class Report_Runner():

    def __init__(
        self,
        session,
        report_template_id: int = None,
        report_template_data: dict = None,
        metadata: dict = None,
        member = None,
        project_string_id = None

    ):

        self.session = session
        self.report_template_id = report_template_id
        self.report_template_data = report_template_data

        self.time_created_normalized = None

        self.metadata_untrusted = metadata
        self.member = member

        self.project_string_id = project_string_id
        self.project = Project.get_by_string_id(self.session, self.project_string_id)

        self.log = regular_log.default()

        # Context of say report list or something else...
        if not self.metadata_untrusted:
            return

        self.metadata = self.validate_report_spec(
            metadata_untrusted = self.metadata_untrusted)
        if len(self.log["error"].keys()) >= 1:
            return

        if 'all' in self.metadata.get('member_list', []):
            project = Project.get_by_string_id(session, self.metadata['project_string_id'])
            users = project.users
            member_ids = [u.member_id for u in users]
            self.metadata['member_list'] = member_ids

    @staticmethod
    def string_to_class(item_of_interest: str):
        """
        We assume that item_of_interest has been
        converted to lower case already here

        more general approach - more scale
            get_class = lambda x: globals()[x]
            form_class = get_class(report.customization_forms.form_class_name)
        """

        class_dict = {
            'instance': Instance,
            'user': User,
            'file': File,
            'task': TaskEvent,
            'task_event': TaskEvent,
            'event': Event,
            'time_spent_task': TaskTimeTracking,
            'annotator_performance': 'custom_report',
            'approval_reject_ratio': 'custom_report'
        }
        return class_dict.get(item_of_interest)


    def get_existing_report_template(self, report_template_id):

        self.report_template = ReportTemplate.get_by_id(
            session = self.session,
            id = report_template_id)


    def validate_existing_report_id_permissions(
        self,
        project_string_id: str = None):
        """
        Concept that for existing reports
        we could still get or run permissions
        from the project  scope ie below?
        validate_report_permissions_scope

        Assumes self.report_template is set, ie
        by calling get_existing_report_template()

        We are always checking the project id regardless,
        so the concern is not so much that the project id is related to
        the template, ie in the case of diffgram wide reports

            But need to think about implications for editing this a bit here

        Careful, there's a strong potential to bypass the permissions
        by mistake here. better to still check the permissions as expected here...
            (context of trying to use the "built" in project_string_id for
            defaults, but that defeats the point)

        """
        if self.report_template is None:
            raise Forbidden("Not Found")

        self.validate_report_permissions_scope(
            scope = self.report_template.scope,
            project_string_id = project_string_id,
        )

    def validate_report_permissions_scope(self,
                                          scope: str,
                                          project_string_id: str = None,
                                          ):
        """

        Then do we treat updating project
        as seperate from updating other attributes...

        We use project string id here because that's pattern
        with permissions thing.

        We expect this to raise if there are issues.
        This function could actually be generic to other things that
        may need to validate / store at different scope levels

        Like for example sharing guides among projects...

        Assumptions

            For now this assumes that scope has been validated
            so a scope != to one of these shouldn't be possible.
            But could have a forbidden here...

            We don't call this at init, since this is primarily for a
            user / (member more generically in future),
            where as we may want to run report runner internally
            for other things

        It's almost like the only question is if for some reason
        this doesn't match the existing report right?

        Case of new report:
            Check this (from user) and it's fine

        Case of updating a report:
            Check this (from user)
            AND
            in the update case, I feel like
            there's an extra check
            that it needs to run this on the existing report ALSO
            to make sure the person could update it in first place
            More of a data integretity concern that I can only
            modify reports in my scope.

        Case of running a report (/ reading a report)
            Check this (from our database) and it's fine?

        """

        scope = scope.lower()

        self.scope = scope

        if scope == "project":
      
            project_role_list = ["admin", "Editor"]

            Project_permissions.check_permissions(
                session = self.session,
                project_string_id = project_string_id,
                Roles = project_role_list)

            # then if it passes can use project
            # careful, for diffgram wide reports this is NOT
            # a project attached to the template (since it dynamically fills it in here)
            self.project = Project.get(self.session, project_string_id)
            return

        raise Forbidden("Scope is invalid")


    def normalize_class_defintions(self):

        if self.item_of_interest in ['user', 'instance', 'file']:
            self.time_created_normalized = self.base_class.created_time

        if self.item_of_interest in ['task', 'event', 'task_event', 'time_spent_task']:
            self.time_created_normalized = self.base_class.time_created

        if self.time_created_normalized is None:
            raise Exception(f"self.item_of_interest: '{self.item_of_interest}' has not defined a self.time_created_normalized.")

        if self.item_of_interest in ['file']:
            self.label_file_id = self.base_class.id

        if self.item_of_interest in ['instance']:
            self.label_file_id = self.base_class.label_file_id

        # Task ID
        if self.item_of_interest in ['task']:
            self.task_id = self.base_class.id
        # Member Created
        if self.item_of_interest in ['instance', 'file']:
            self.member_created = self.base_class.member_created


    def execute_query(self,
                      view_type: str = None):

        q = self.query
        print(q)
        result = q.all()
        return result


    def apply_permission_scope_to_query(self):

        if self.scope == "project":
            self.query = self.query.filter(
                self.base_class.project_id == self.project.id)


    def generate_standard_report(self):
        """
            Logic for standard reports. This is for reports can be directly generated from single table queries.
            No need to combine, join or aggregate data.
        """
        self.init_query = self.get_init_query(group_by_str = self.report_template.group_by)

        self.query = self.init_query.query
        logger.info(self.query)
        self.apply_permission_scope_to_query()

        if self.report_template.period:

            self.date_from, self.date_to = self.determine_dates_from_dynamic_period(
                dynamic_period = self.report_template.period
            )

            if self.report_template.period != "all":
                self.filter_by_date(
                    date_from = self.date_from,
                    date_to = self.date_to,
                    date_period_unit = self.report_template.date_period_unit)

        self.apply_concrete_filters()

        if self.init_query.group_by_str and not self.init_query.second_group_by_str:
            self.query = self.query.group_by(self.init_query.base)

        if self.init_query.second_group_by_str:
            self.query = self.query.group_by(self.init_query.base, self.init_query.second_group_by)

        if self.report_template.group_by == 'date':
            self.query = self.query.order_by(self.init_query.base)

        self.results = self.execute_query(
            view_type = self.report_template.view_type)
        stats = self.format_for_external(self.results)
        stats_serialized = self.serialize_stats(stats)

        Event.new(
            kind = "report_run",
            session = self.session,
            member = self.member,
            report_data = stats_serialized,
            report_template_id = self.report_template_id,
            report_template_data = self.report_template.serialize(),
            success = True
        )

        return stats

    def generate_custom_report(self):
        ReportClass = None
        if self.item_of_interest == 'time_spent_task':
            ReportClass = TimeSpentReport

        elif self.item_of_interest == 'annotator_performance':
            #ReportClass = AnnotatorPerformanceReport
            #self.init_query = Init_Query()
            #report = ReportClass(
            #    session = self.session, 
            #    report_template = self.report_template, 
            #    init_query = self.init_query)
            # report.build_query()
            pass

        elif self.item_of_interest == 'approval_reject_ratio':
            ReportClass = TaskReportRejectRatioReport
        else:
            raise NotImplementedError
        report = ReportClass(session = self.session, report_template = self.report_template)
        return report.run()

    def build_dummy_report_template_from_data(self):
        self.report_template = ReportTemplate(
            **self.report_template_data
        )
        self.scope = self.report_template_data.get('scope')

    def run(self):

        if self.report_template is None and self.report_template_data:
            self.build_dummy_report_template_from_data()

        self.init_base_class_object(self.report_template.item_of_interest)

        assert self.base_class is not None

        if self.base_class == 'custom_report':
            self.results = self.generate_custom_report()
            self.results['user_metadata'] = self.build_user_metadata(self.results['labels'])
        else:
            self.results = self.generate_standard_report()

        return self.results

    def serialize_stats(self, stats):
        if stats is None: return None
        result = {}
        if type(stats) == dict:
            result = stats.copy()
            if len(stats['labels']) > 0 and type(stats['labels'][0]) == datetime.datetime:
                result['labels'] = [x.strftime('%Y-%m-%d') for x in stats['labels']]
        else:
            result['stats'] = stats
        return result

    def save(self):

        self.report_template = self.get_from_id_or_new_report_template(
            report_template_id = self.report_template_id,
            project = self.project
        )
        if len(self.log["error"].keys()) >= 1:
            return

        self.update_report_template(metadata = self.metadata)

        if len(self.log["error"].keys()) >= 1:
            # Caution for permissions reasons this must come right after update_template
            # specifically the diffgram_wide_default flag
            return

        self.update_dashboard()

        self.session.add(self.report_template)

        # Get ID, relevant if new object
        self.session.flush()

    # New or get existing.
    def get_from_id_or_new_report_template(
        self,
        report_template_id: int,
        project = None
    ) -> ReportTemplate:
        """
        Pattern where creating a "new"
        one really just does the ID and the rest if part of update process?

        """

        if report_template_id:
            report_template = ReportTemplate.get_by_id(
                session = self.session,
                id = report_template_id)

            if report_template is None:
                self.log['error']['report_template'] = "Invalid report_template ID"
                return

            return report_template

        else:
            return ReportTemplate.new(
                member = self.member,
                project = project)

    def validate_report_spec(self,
                             metadata_untrusted: dict):
        """
        This is strictly validating the
        raw data is there it's not checking permissions

        """

        self.log, metadata = regular_input.input_check_many(
            spec_list = report_spec_list,
            log = self.log,
            untrusted_input = metadata_untrusted)

        if len(self.log["error"].keys()) >= 1:
            return

        return metadata

    def init_base_class_object(self, item_of_interest: str):
        if item_of_interest:
            self.item_of_interest = item_of_interest
            self.base_class = self.string_to_class(item_of_interest)
            if self.base_class is None:
                raise NotImplementedError(f'Item of interest "{item_of_interest}" is not supported')
            self.normalize_class_defintions()
        else:
            self.log['error']['item_of_interest'] = "item_of_interest is None"


    def __filter_soft_delete_instances(self):

        self.query = self.query.filter(self.base_class.soft_delete == False)


    def filter_by_task_event_type(self, task_event_type: str):
        if self.report_template.item_of_interest != 'task':
            return
        if task_event_type.lower() == 'all':
            return
        if not self.base_class.event_type:
            return
        self.query = self.query.filter(self.base_class.event_type == task_event_type)


    def apply_concrete_filters(self):

        if self.base_class == TaskTimeTracking:
            # Exclude statues, e.g. time spent looking at completed tasks
            self.query = self.query.filter(TaskTimeTracking.status.is_(None))

        if self.base_class == Instance:
            self.__filter_soft_delete_instances()

        if self.report_template.task_id:
            self.query = self.__filter_by_task(
                query = self.query,
                task_id = self.report_template.task_id)

        if self.report_template.job_id:
            self.filter_by_job(job_id = self.report_template.job_id)

        if self.report_template.task_event_type:
            self.filter_by_task_event_type(task_event_type = self.report_template.task_event_type)

        if self.report_template.member_list:
            self.filter_by_member_list(member_list = self.report_template.member_list)

        if self.report_template.filter_by_items:

            if self.report_template.filter_by_items.get('label_file_id_list'):
                self.filter_by_label_file_id_list(
                    label_file_id_list = self.report_template.filter_by_items.get('label_file_id_list'))


    def __filter_by_task(self,
                         query,
                         task_id: int):

        # TODO: Add suport or remove from UI the task filter when base class is Task
        if self.item_of_interest in ['task']:
            logger.warning(f"No filter supported for task_id. item_of_interest is {self.item_of_interest}")
            return query
        return query.filter(self.base_class.task_id == task_id)


    def filter_by_member_list(self, member_list: list):
        # For now we can't add filters to task object as base class string. Might need to add member_created to task.
        # We added a join here, can discuss other ways of doing it if this is not convincing.
        if self.item_of_interest in ['task']:
            self.query = self.query.join(Member, self.base_class.assignee_user_id == Member.user_id).filter(
                Member.id.in_(member_list)
            )
            return
        self.query = self.query.filter(self.base_class.member_created_id.in_(member_list))


    def filter_by_job(self, job_id: int):
        """

        """

        if self.item_of_interest in ['instance']:
            tasks_in_job = self.session.query(Task).filter(Task.job_id == job_id).all()
            task_id_list = [x.id for x in tasks_in_job]
            self.query = self.query.filter(self.base_class.task_id.in_(task_id_list))
        else:
            self.query = self.query.filter(self.base_class.job_id == job_id)


    def filter_by_label_file_id_list(self, label_file_id_list: list):
        """
        label_file_id_list: List of ints ids
        """
        if self.item_of_interest == 'task':
            self.query = self.query.filter(
                self.base_class.file_id.in_(label_file_id_list))

        else:
            self.query = self.query.filter(
                self.base_class.label_file_id.in_(label_file_id_list))

    def update_report_template(self, metadata: dict):
        """
        Assumes data has been validated...

        I think it's worth referring to this as meta data /
        not report_template_json? since it's shorter,
        and it feels more appropriate in this context where
        it's still sort of "untrusted", ie
        we are treating parts of it differently

        Because we want only super admins editing default report,
            we are returning before testing any of that stuff.

            Assume this covers archive flag case for example along with other stuff
        """
        if self.report_template.diffgram_wide_default is True or \
            metadata.get('diffgram_wide_default') is True:  # init case?

            user = User.get(self.session)
            if user is None or user.is_super_admin is not True:
                self.log['error']['permission'] = "'diffgram_wide_default' Invalid permission."
                return

            # reset project for Diffgram wide report
            self.report_template.project = None
            self.report_template.project_string_id = None

            # clear concrete filters
            self.report_template.job_id = None

        else:
            # custom ids / concrete filters

            # We assume job specific permissions are handled by larger permission scope?
            # ie it's an *and* function with project_id
            self.report_template.job_id = metadata.get('job_id')

        # Assumes permissions handled by project scope
        self.report_template.task_id = metadata.get('task_id')
        self.report_template.member_list = metadata.get('member_list')
        self.report_template.task_event_type = metadata.get('task_event_type')

        self.report_template.diffgram_wide_default = metadata.get('diffgram_wide_default')

        self.report_template.name = metadata.get('name')

        self.report_template.view_type = metadata.get('view_type')
        self.report_template.view_sub_type = metadata.get('view_sub_type')

        self.report_template.scope = metadata.get('scope').lower()

        self.report_template.item_of_interest = metadata.get('item_of_interest').lower()
        self.init_base_class_object(self.report_template.item_of_interest)

        self.report_template.archived = metadata.get('archived')
        self.report_template.is_visible_on_report_dashboard = metadata.get('is_visible_on_report_dashboard')

        self.report_template.group_by = metadata.get('group_by')
        self.report_template.second_group_by = metadata.get('second_group_by')

        self.report_template.member_updated = self.member

        self.report_template.period = metadata.get('period')
        self.report_template.date_period_unit = metadata.get('date_period_unit')
        self.report_template.compare_to_previous_period = metadata.get('compare_to_previous_period')

        self.update_metadata_for_filter_by_items(metadata = metadata)


    def update_metadata_for_filter_by_items(
            self, 
            metadata: dict):

        if not self.report_template.filter_by_items:
            self.report_template.filter_by_items = {}

        self.report_template.filter_by_items['label_file_id_list'] = metadata.get(
            'label_file_id_list')

    def update_dashboard(
            self,
            report_dashboard_id: int = None,
            mode: str = "set_dashboard"):

        if report_dashboard_id is None:
            report_dashboard_id = self.get_or_create_project_report_dashboard_id()

        if mode == "set_dashboard":
            self.set_dashboard(
                report_dashboard_id = report_dashboard_id)

    def set_dashboard(
        self,
        report_dashboard_id: int):

        self.report_template.report_dashboard_id = report_dashboard_id

        self.session.add(self.report_template)


    def get_or_create_project_report_dashboard_id(self):

        if self.report_template.diffgram_wide_default is True:
            """
                Could look at default Dashboard objects related to default reports
                in the future but for now this is very much for projects only
            """
            return None

        if self.project.default_report_dashboard_id:
            return self.project.default_report_dashboard_id

        report_dashboard = ReportDashboard.new(
            project_id = self.project.id)

        self.session.add(report_dashboard)
        self.session.flush()

        self.project.default_report_dashboard_id = report_dashboard.id

        return report_dashboard.id


    @staticmethod
    def convert_str_to_datetime(date):
        """
        Assumption here is if we aren't providing a string date
        We are providing an exact date, (ie by hour) and
        don't want to convert it as want to maintain that...

        Leave off was that we likely would want this for
        * Running a specific instance of a report
        But we we do not store it on the report_template
        because repot_template stores dynamic / relative period ie last 30 days?

        ie
        datetime_from = Report_Runner.convert_str_to_datetime(
            metadata.get('datetime_from'))
        datetime_to = Report_Runner.convert_str_to_datetime(
            metadata.get('datetime_to'))

        """
        format = "%Y-%m-%d"

        if date:
            if isinstance(date, datetime.datetime) is False:
                date = datetime.datetime.strptime(date, format)

        return date


    def determine_dates_from_dynamic_period(
        self,
        dynamic_period: str) -> (datetime.datetime, datetime.datetime):
        """
        Context of calculating python datetime
        from string based description of relative time

        """

        # Default to now, that thing where it's <= so we do this "offset"
        date_to = datetime.datetime.utcnow() + datetime.timedelta(days = 2)

        if dynamic_period == "all":
            # For now assume from when project was created
            # In future could get more specific
            date_from = self.project.time_created
            if date_from is None:  # for older projects
                date_from = datetime.datetime(2018, 6, 1)

        # some code reuse opportunities here...
        if dynamic_period == "last_30_days":
            date_from = date_to - datetime.timedelta(days = 30)

        if dynamic_period == "last_14_days":
            date_from = date_to - datetime.timedelta(days = 14)

        return date_from, date_to


    def filter_by_date(self,
                       date_from,
                       date_to,
                       date_period_unit: str):

        # Set to next day so we can use default of 00:00 start
        # instead of midnight. Otherwise results during the
        # day get excluded
        if date_period_unit == 'day':
            date_to += datetime.timedelta(days = 1)

        self.query = self.query.filter(self.time_created_normalized >= date_from)
        self.query = self.query.filter(self.time_created_normalized < date_to)


    def get_init_query(self, group_by_str: str):
        """
        """
        init_query = InitQuery()
        init_query.group_by_str = group_by_str
        init_query.second_group_by_str = self.report_template.second_group_by

        self.member_id_normalized = self.get_and_set_member_id_normalized()

        logger.info(self.member_id_normalized)

        group_by_dict = {
            None: self.no_group_by,
            'date': self.group_by_date,
            'label': self.group_by_label,
            'user': self.group_by_user,
            'task': self.group_by_task,
            'file': self.group_by_file,
            'task_status': self.group_by_task_status
        }
        first_group_by = group_by_dict.get(init_query.group_by_str)
        first_group_by(init_query)

        if self.base_class == TaskTimeTracking:
            init_query.group_by = func.sum(self.base_class.time_spent)

        init_query = self.set_second_group_by(init_query)

        if init_query.second_group_by_str:
            init_query.query = self.session.query(init_query.base, init_query.group_by, init_query.second_group_by)
            init_query.query = self.apply_init_query_filters(init_query)
            return init_query

        if init_query.group_by_str:
            init_query.query = self.session.query(init_query.base, init_query.group_by)
            init_query.query = self.apply_init_query_filters(init_query)
            return init_query

        # Else no group by
        init_query.query = self.session.query(init_query.base)()
        return init_query


    def apply_init_query_filters(self, init_query):
        if init_query.distinct is True:
            return init_query.query.distinct()

        if init_query.second_group_by:
            return init_query.query.filter()

        return init_query.query


    def set_second_group_by(self, init_query):
        if not self.report_template.second_group_by:
            return init_query
        
        if self.report_template.second_group_by == 'label':
            init_query.second_group_by = self.base_class.label_file_id

        if self.report_template.second_group_by == 'user':
            self.member_id_normalized = self.get_and_set_member_id_normalized()
            init_query.second_group_by = self.member_id_normalized
            logger.info(init_query.second_group_by)

        return init_query


    def no_group_by(self, init_query):
        init_query.base = self.base_class
        return init_query


    def group_by_task_status(self, init_query):
        init_query.base = self.base_class.status
        init_query.group_by = func.count(self.base_class.id)
        return init_query


    def group_by_date(self, init_query):
        self.date_func = func.date_trunc(self.report_template.date_period_unit,
                                         self.time_created_normalized)
        init_query.base = self.date_func
        init_query.group_by = func.count(self.base_class.id)
        return init_query


    def group_by_label(self, init_query):
        if hasattr(self, 'label_file_id'):
           init_query.base = self.label_file_id
           init_query.group_by = func.count(self.base_class.id)
        else:
           init_query.base = self.base_class
        return init_query


    def group_by_file(self, init_query):
        init_query.base = self.base_class.file_id
        init_query.group_by = func.count(self.base_class.id)
        return init_query


    def group_by_task(self, init_query):
        init_query.base = self.base_class.task_id
        init_query.group_by = func.count(self.base_class.id)
        return init_query


    def group_by_user(self, init_query):

        init_query.base = self.member_id_normalized
        init_query.group_by = func.count(self.base_class.id)

        if self.item_of_interest == 'task':
            init_query.group_by = func.count(self.base_class.task_id)
            init_query.distinct = True
        return init_query



    def get_and_set_member_id_normalized(self):

        self.member_id_normalized = None

        if self.item_of_interest in ["instance", "file"]:
            self.member_id_normalized = self.base_class.member_created_id

        elif self.item_of_interest in ["event", "time_spent_task"]:
            self.member_id_normalized = self.base_class.member_id

        if self.item_of_interest == 'task':
            self.set_member_column_from_task_event_type()

        if self.member_id_normalized is None:
            raise Exception(f"self.member_id_normalized is None for self.item_of_interest: {self.item_of_interest}")

        return self.member_id_normalized


    def set_member_column_from_task_event_type(self):
        # Needs review, should only be member
        if self.report_template.task_event_type == ['task_created', 'task_review_start']:
            self.member_id_normalized = self.base_class.member_created_id
        elif self.report_template.task_event_type == ['task_completed']:
            self.member_id_normalized = self.base_class.user_assignee_id
        elif self.report_template.task_event_type == ['task_request_changes']:
            self.member_id_normalized = self.base_class.user_reviewer_id
        else:
            self.member_id_normalized = self.base_class.member_created_id

    def get_class_type_str_from_task_type_column(self):
        result = 'member'
        if self.report_template.task_event_type == ['task_created', 'task_review_start']:
            result = 'member'
        elif self.report_template.task_event_type == ['task_completed']:
            result = 'user'
        elif self.report_template.task_event_type == ['task_request_changes']:
            result = 'user'
        return result

    def format_for_external(
        self,
        execution_results
    ):

        if self.report_template.view_type == "chart":
            return self.format_for_charting(execution_results)

        if self.report_template.view_type == "count":
            # Update, apparently for group_by things we still need
            # do the .all() ( since it's already doing counts for each group
            # otherwise we just get the count of the "groups".
            return self.format_for_charting(execution_results)


    def build_label_names_map_from_second_grouping(
            self,
            second_grouping):

        label_file_ids = set(second_grouping)
        labels_files = File.get_by_id_list(session = self.session, file_id_list = label_file_ids)
        label_names_map = {}
        for label_file in labels_files:
            if label_file.label:
                label_names_map[label_file.id] = label_file.label.name

        return label_names_map


    def format_view_type_count(
            self, 
            list_tuples_by_period: list):

        if len(list_tuples_by_period) == 0:
            return 0
        if self.report_template.second_group:
            labels, second_grouping, values = zip(*list_tuples_by_period)
        else:
            labels, values = zip(*list_tuples_by_period)
        return sum(values)


    def format_for_charting(
            self,
            list_tuples_by_period,
            report_template = None):
        """
        This assumes list_tuples_by_period is something like:
            0: ["Mon, 27 Jan 2020", 2, n]
            1: ["Tue, 28 Jan 2020", 2, n]
            2: ["Wed, 29 Jan 2020", 4, n]

        list_tuples_by_period is the "actual data"

        Does not have to be date centric

        """
        if report_template is None:
            report_template = self.report_template

        second_grouping = None
        label_colour_map = None
        label_names_map = None
        user_metadata = None

        if self.report_template.group_by == 'label' or self.report_template.second_group_by == 'label':
            label_colour_map = self.project.directory_default.label_file_colour_map

        if self.report_template.view_type == "count":
            return self.format_view_type_count(list_tuples_by_period)

        if report_template.group_by and list_tuples_by_period:

            print(list_tuples_by_period)

            if self.report_template.second_group_by:
                labels, values, second_grouping = zip(*list_tuples_by_period)
            else:
                labels, values = zip(*list_tuples_by_period)

            if self.report_template.group_by == 'user':
                user_metadata = self.build_user_metadata(labels)

            if self.report_template.second_group_by == 'user':
                user_metadata = self.build_user_metadata(second_grouping)

            if report_template.group_by == 'date' and report_template.date_period_unit == 'day':

                labels = self.build_date_range(
                    date_from = self.date_from,
                    date_to = self.date_to)

                labels = [i.isoformat() for i in labels]

            count = sum(values)
            
            if self.report_template.second_group_by == 'label':
                label_names_map = self.build_label_names_map_from_second_grouping(second_grouping)

            serialized_list_tuples_by_period = self.serialize_list_tuples_by_period(list_tuples_by_period)

            return {'labels': labels,
                    'values': values,
                    'count': count,
                    'user_metadata': user_metadata,
                    'label_colour_map': label_colour_map,
                    'label_names_map': label_names_map,
                    'second_grouping': second_grouping,
                    'list_tuples_by_period': serialized_list_tuples_by_period}

    def build_date_range(self, 
                date_from: datetime.datetime, 
				date_to: datetime.datetime):

        days_list = []
        period_desired = (date_to - date_from).days
        for i in range(period_desired):
            date = date_from + datetime.timedelta(days=i)
            days_list.append(date.replace(hour=0, minute=0, second=0, microsecond=0))
        return days_list

    def format_if_datetime(self, text):
        if isinstance(text, datetime.datetime):
            return text.isoformat()
        else:
           return text


    def serialize_list_tuples_by_period(self, list_tuples_by_period):
        # e.g. 
        # "(ABC datetime, 13, 1)", "(ABC datetime, 0, 0)
        # Where the the SQL query order is generally maintained
        # So the last element is the last group by etc.
        if self.report_template.second_group_by:
            serialized_list_tuples_by_period = [[self.format_if_datetime(i[0]), i[1], i[2]] for i in list_tuples_by_period]
        else:
            serialized_list_tuples_by_period = [[self.format_if_datetime(i[0]), i[1]] for i in list_tuples_by_period]

        return serialized_list_tuples_by_period


    def build_user_metadata(self, member_ids_list):
        result = []
        if not member_ids_list: return

        member_ids_list = set(member_ids_list)
        users = User.get_by_id_member_list(self.session, member_ids_list)
        for user in users:
            result.append({
                'name': f'{user.first_name} {user.last_name}',
                'user_id': user.id,
                'member_id': user.member_id,
                'email': user.email,
            })
        return result

    def report_template_list(
        self,
        report_dashboard_id = None,
        only_is_visible_on_report_dashboard = None):
        """
        Assumes validated scope / permission

        Seems to make sense to use self here since
        we are only running this if validated right?

        only_is_visible_on_report_dashboard   is None because we have default list of
        all reports, but then on dashboard we can set this to True

        Want to keep these queries separate because
            they are likely to expand in different directions / have different optimizations
            for example default reports relatively static
            and the filtering doesn't really relate to the concerns for the normal
            custom reports
        """

        custom_reports_list = ReportTemplate.list(
            session = self.session,
            scope = self.scope,
            project = self.project,
            return_kind = "objects",
            report_dashboard_id = report_dashboard_id,
            only_is_visible_on_report_dashboard = only_is_visible_on_report_dashboard
        )

        default_reports_list = ReportTemplate.list_default_reports(
            session = self.session,
            only_is_visible_on_report_dashboard = only_is_visible_on_report_dashboard
        )

        return custom_reports_list + default_reports_list
