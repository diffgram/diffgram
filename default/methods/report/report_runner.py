# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *

from sqlalchemy import func
import datetime
import threading

from methods.report.custom_reports.TimeSpentReport import TimeSpentReport
from methods.report.custom_reports.AnnotatorPerformanceReport import AnnotatorPerformanceReport
from shared.database.annotation.instance import Instance
from shared.database.source_control.file import File

from shared.permissions.super_admin_only import Super_Admin
from shared.database.report.report_template import ReportTemplate
from shared.database.report.report_dashboard import ReportDashboard
from shared.database.auth.member import Member

# Would be nice if order of these matched
# order in Report_Template

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

    {"group_by_labels": {
        'default': False,
        'kind': bool,
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


# TODO moving report stuff from stats into here...


class Report_Runner():
    """
    Could we combine the run / save under one thing?

    Directionally trying to make the primary class
    and group by stuff fairly flexible, but at moment there
    are some restrictions there...

    When do we want to set self.query...
        seems like a reasonable thing to couple
        since query will be called so often


    item_of_interest may come from report id

    report_template_id instead of id because they may be other
    id's or say an instance of a report that we interact with

    In context of making this more composable, curious
    if perhaps we should not pass report_template_id
    here at all and that should be part of another thing...
    ie making the base "init" lighter.

        We now assume that a report template will only have 1
        view. In the future can re look at many views for 1 template.

    """

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

        # This will get converted into
        # metadata after validating spec.

        self.metadata_untrusted = metadata
        self.member = member

        # These are assumed to be set from other functions
        # ie through a validation process...???
        self.project = None

        self.log = regular_log.default()

        # Context of say report list or something else...
        if not self.metadata_untrusted:
            return

        self.metadata = self.validate_report_spec(
            metadata_untrusted = self.metadata_untrusted)
        if len(self.log["error"].keys()) >= 1:
            return

        self.project_string_id = project_string_id
        self.project = Project.get_by_string_id(self.session, self.project_string_id)
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
            'task': Task,
            'event': Event,
            'time_spent_task': 'custom_report',
            'annotator_performance': 'custom_report'
        }

        return class_dict.get(item_of_interest)

    def get_existing_report_template(self, report_template_id):
        """
        Not for saving,
        case of just getting,
        don't want to have optinal saving path here
        since we expect to error if report doesn't exist etc.
        """
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
        TODO look at report_scope
        check project valid for user ect (using existing permission
        approaches)...

        Then do we treat updating project
        as seperate from updating other attributes...

        Note at current this assumes the user is logged in.
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
            # Validate project
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

        # Should not be possible to reach here
        # if scope string is validated.
        raise Forbidden("Scope is invalid")

    def normalize_class_defintions(self):
        """
        ie that time created thing or...

        This is more just for things that we
        labelled differently but have different meanings?

        This uses self because it's only relevant if
        both item_of_interest and base_class are created?

        """
        # Time Created
        if self.item_of_interest in ['user', 'instance', 'file']:
            self.time_created = self.base_class.created_time

        if self.item_of_interest in ['task', 'event']:
            self.time_created = self.base_class.time_created

        if self.item_of_interest in ['file']:
            self.label_file_id = self.base_class.id

        if self.item_of_interest in ['instance']:
            self.label_file_id = self.base_class.label_file_id

        # Task ID
        if self.item_of_interest in ['task']:
            self.base_class.task_id = self.base_class.id
        # Member Created
        if self.item_of_interest in ['instance', 'file']:
            self.member_created = self.base_class.member_created

    # self.log['internal'] = 'Ran normalize_class_defintions'

    def execute_query(self,
                      view_type: str = None):

        q = self.query
        # Uncomment for performance debugging
        # from shared.helpers.performance import explain
        # print(q)
        # explain_result = self.session.execute(explain(q)).fetchall()
        # for x in explain_result:
        #     print(x)
        result = q.all()
        return result

    def apply_permission_scope_to_query(self):
        """
        Other stuff is in context of "does user have permission to run report"
        this is the literal query modification

        This assumes the baseclass has project_id,
        in cases where it doesn't then have to think about it a bit.

        """

        if self.scope == "project":
            self.query = self.query.filter(
                self.base_class.project_id == self.project.id)

    def generate_standard_report(self):
        """
            Logic for standard reports. This is for reports can be directly generated from single table queries.
            No need to combine, join or aggregate data. This applies for item of interest like:
            -
        :return:
        """
        init_query = self.get_init_operation(group_by = self.report_template.group_by)

        self.query = init_query()
        self.apply_permission_scope_to_query()

        if self.report_template.period:

            """
            Note 100% sure about setting this self here...
            the format for other thing requires the date to be set

            "All" is relative to when something was created
            and may still be needed for how we format the data for external view
            even if internal sql filtering doesn't need it.
            """

            self.date_from, self.date_to = self.determine_dates_from_dynamic_period(
                dynamic_period = self.report_template.period
            )

            if self.report_template.period != "all":
                self.filter_by_date(
                    date_from = self.date_from,
                    date_to = self.date_to,
                    date_period_unit = self.report_template.date_period_unit)

        self.apply_concrete_filters()

        if self.report_template.group_by == 'date':
            # assumes self.date_func is set from init_query
            self.query = self.query.group_by(self.date_func)
            self.query = self.query.order_by(self.date_func)

        elif self.report_template.group_by == 'label':
            if hasattr(self, 'label_file_id'):
                self.query = self.query.group_by(self.label_file_id)

        elif self.report_template.group_by == 'user':
            self.query = self.query.group_by(self.member_id_normalized)

        elif self.report_template.group_by == 'task':
            self.query = self.query.group_by(self.base_class.task_id)

        elif self.report_template.group_by == 'file':

            if self.report_template.group_by_labels:
                self.query = self.query.group_by(self.base_class.file_id, self.base_class.label_file_id)
            else:
                self.query = self.query.group_by(self.base_class.file_id)

        elif self.report_template.group_by == 'task_status':
            self.query = self.query.group_by(self.base_class.status)

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
        if self.item_of_interest == 'time_spent_task':
            report = TimeSpentReport(session = self.session, report_template = self.report_template)
        if self.item_of_interest == 'annotator_performance':
            report = AnnotatorPerformanceReport(session = self.session, report_template = self.report_template)
        else:
            raise NotImplementedError

        return report.run()

    def build_dummy_report_template_from_data(self):
        self.report_template = ReportTemplate(
            item_of_interest = self.report_template_data['item_of_interest'],
            group_by = self.report_template_data['group_by'],
            job_id = self.report_template_data['job_id'],
            project_id = self.project.id,
            period = self.report_template_data['period'],
            view_type = self.report_template_data['view_type'],
            view_sub_type = self.report_template_data['view_sub_type'],
        )

    def run(self):
        """
        Sets base class.
            I don't think we should have to call "update" in order to run it

        Assumes other values needed are set or loaded from existing???
        """
        if self.report_template is None and self.report_template_data:
            self.build_dummy_report_template_from_data()

        self.init_base_class_object(self.report_template.item_of_interest)

        assert self.base_class is not None

        if self.base_class == 'custom_report':
            self.results = self.generate_custom_report()
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
            self.normalize_class_defintions()
        else:
            self.log['error']['item_of_interest'] = "item_of_interest is None"

    def __filter_soft_delete_instances(self):

        self.query = self.query.filter(self.base_class.soft_delete == False)

    def apply_concrete_filters(self):

        if self.base_class == Instance:
            self.__filter_soft_delete_instances()

        if self.report_template.task_id:
            self.query = self.__filter_by_task(
                query = self.query,
                task_id = self.report_template.task_id)

        if self.report_template.job_id:
            self.filter_by_job(job_id = self.report_template.job_id)

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
            logger.warning('No filter supported for task_id. item_of_interest is {}'.format(self.item_of_interest))
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

        # TODO: Add suport or remove from UI the task filter when base class is Instance
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
        self.report_template.group_by_labels = metadata.get('group_by_labels', False)

        self.report_template.diffgram_wide_default = metadata.get('diffgram_wide_default')

        self.report_template.name = metadata.get('name')

        self.report_template.view_type = metadata.get('view_type')
        self.report_template.view_sub_type = metadata.get('view_sub_type')

        # Is it ok to just store this here
        self.report_template.scope = metadata.get('scope').lower()

        # We assume to store this in lower case because then
        # front end can easily show an upper case value
        self.report_template.item_of_interest = metadata.get('item_of_interest').lower()

        self.init_base_class_object(self.report_template.item_of_interest)

        self.report_template.archived = metadata.get('archived')
        self.report_template.is_visible_on_report_dashboard = metadata.get('is_visible_on_report_dashboard')

        self.report_template.group_by = metadata.get('group_by')

        self.report_template.member_updated = self.member

        self.report_template.period = metadata.get('period')
        self.report_template.date_period_unit = metadata.get('date_period_unit')
        self.report_template.compare_to_previous_period = metadata.get('compare_to_previous_period')

        self.update_metadata_for_filter_by_items(metadata = metadata)

    def update_metadata_for_filter_by_items(self, metadata: dict):
        """
        WIP
        """
        # This still will be part of Filters
        # Not base template.

        if not self.report_template.filter_by_items:
            self.report_template.filter_by_items = {}

        self.report_template.filter_by_items['label_file_id_list'] = metadata.get(
            'label_file_id_list')

    def update_dashboard(
        self,
        report_dashboard_id: int = None,
        mode: str = "set_dashboard"):
        """
        """

        if report_dashboard_id is None:
            report_dashboard_id = self.get_or_create_project_report_dashboard_id()

        if mode == "set_dashboard":
            self.set_dashboard(
                report_dashboard_id = report_dashboard_id)

    def set_dashboard(
        self,
        report_dashboard_id: int
    ):
        """
        Any other validation here or...
        """

        self.report_template.report_dashboard_id = report_dashboard_id

        self.session.add(self.report_template)

    def get_or_create_project_report_dashboard_id(self):
        """
        Not quite sure if this should be here or on each object,
        the challenge is we may want other types of defaults here...
        so for now seems more related to this, especially since we need
        the ReportDashboard object to create new one...
        """

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

        # Default to now, that thing where it's <= so we do this "offset" of 1 day.
        date_to = datetime.datetime.utcnow() + datetime.timedelta(days = 1)

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
        """
        Assumes qeury is set

        Does literal query modification
        see ie determine_dates_from_dynamic_period()
        for determining dates

        """

        # Set to next day so we can use default of 00:00 start
        # instead of midnight. Otherwise results during the
        # day get excluded

        # TODO review if this makes sense in "generic" context

        # Do we assume if date_period_unit == "exact" for example then this doesn't matter?
        if date_period_unit == 'day':
            date_to += datetime.timedelta(days = 1)

        self.query = self.query.filter(self.time_created >= date_from)
        self.query = self.query.filter(self.time_created < date_to)

    def get_init_operation(self, group_by: str):
        """
        Groupby is (must be?) the start of a query...
        Returns an operation that can be called
        ie query = operation()

        All of these functions expect the base class to be set?
        (vs having to pass it?)

        Maybe this should be called like "init_query" or
        something?

            careful, if adding something here it needs to also be in group_by
            clause above.

        """
        group_by_dict = {
            None: self.no_group_by,
            'date': self.group_by_date,
            'label': self.group_by_label,
            'user': self.group_by_user,
            'task': self.group_by_task,
            'file': self.group_by_file,
            'task_status': self.group_by_task_status
        }
        return group_by_dict.get(group_by)

    def no_group_by(self):
        query = self.session.query(self.base_class)
        return query

    def group_by_task_status(self):
        self.date_func = func.date_trunc(self.report_template.date_period_unit,
                                         self.time_created)
        query = self.session.query(self.base_class.status, func.count(self.base_class.id))
        return query

    def group_by_date(self):
        """
        Assumes everything is set,
            ie report_template is set
        """
        self.date_func = func.date_trunc(self.report_template.date_period_unit,
                                         self.time_created)
        query = self.session.query(self.date_func,
                                   func.count(self.base_class.id))
        return query

    def group_by_label(self):
        """
        WIP only really for Instance
        Yes this must use an id it look like for group by
        """
        if hasattr(self, 'label_file_id'):
            query = self.session.query(self.label_file_id, func.count(self.base_class.id))
        else:
            query = self.session.query(self.base_class)
        return query

    def group_by_file(self):
        if self.report_template.group_by_labels:
            query = self.session.query(self.base_class.file_id, self.base_class.label_file_id,
                                       func.count(self.base_class.id))
            query = query.filter()
        else:
            query = self.session.query(self.base_class.file_id, func.count(self.base_class.id))

        return query

    def group_by_task(self):
        """
        """
        query = self.session.query(self.base_class.task_id, func.count(self.base_class.id))
        return query

    def group_by_user(self):
        """
        Do we want to call this member or user...

        """

        # normalize member_id
        self.member_id_normalized = None

        if self.item_of_interest in ["instance", "file"]:
            self.member_id_normalized = self.base_class.member_created_id
        elif self.item_of_interest == "event":
            self.member_id_normalized = self.base_class.member_id

        # Task has assignee_user_id instead of member id...

        query = self.session.query(self.member_id_normalized,
                                   func.count(self.base_class.id))
        return query

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

    def format_for_charting(
        self,
        stats_list_by_period,
        report_template = None):
        """
        This assumes stats_list_by_period is something like:
            0: ["Mon, 27 Jan 2020 00:00:00 GMT", 2]
            1: ["Tue, 28 Jan 2020 00:00:00 GMT", 2]
            2: ["Wed, 29 Jan 2020 00:00:00 GMT", 4]

        Basically stats_list_by_period is the "actual data"
        so to speak... the shape of the date needs work still

        We set report_template from self if it's None...

        """
        if report_template is None:
            report_template = self.report_template

        second_grouping = None
        label_colour_map = None
        label_names_map = None
        if self.report_template.group_by_labels:
            # Get colour map for bars colors
            label_colour_map = self.project.directory_default.label_file_colour_map

        if self.report_template.view_type == "count":

            if len(stats_list_by_period) == 0:
                return 0
            if self.report_template.group_by_labels:
                labels, second_grouping, values = zip(*stats_list_by_period)
            else:
                labels, values = zip(*stats_list_by_period)
            return sum(values)

        # TODO stronger handling if
        # stats_list_by_period is None
        # ie empty

        if report_template.group_by and stats_list_by_period:
            # fill missing days is sorta designed
            # for "day" period?
            if report_template.group_by == 'date' and report_template.date_period_unit == 'day':

                with_missing_dates = Stats.fill_missing_dates(
                    date_from = self.date_from,
                    date_to = self.date_to,
                    list_by_period = stats_list_by_period)

                if self.report_template.group_by_labels:
                    labels, second_grouping, values = zip(*with_missing_dates)
                    label_file_ids = set(second_grouping)
                    labels_files = File.get_by_id_list(session = self.session, file_id_list = label_file_ids)
                    label_names_map = {}
                    for label_file in labels_files:
                        label_names_map[label_file.id] = label_file.label.name
                else:
                    labels, values = zip(*with_missing_dates)

            else:
                if self.report_template.group_by_labels:
                    labels, second_grouping, values = zip(*stats_list_by_period)
                    label_file_ids = set(second_grouping)
                    labels_files = File.get_by_id_list(session = self.session, file_id_list = label_file_ids)
                    label_names_map = {}
                    for label_file in labels_files:
                        label_names_map[label_file.id] = label_file.label.name
                else:
                    labels, values = zip(*stats_list_by_period)

            # Front end now handles for user case
            if report_template.group_by in ['label']:
                labels, values = zip(*stats_list_by_period)

                labels = self.ids_to_human_readable_labels(
                    ids_list = labels,
                    group_by = report_template.group_by)

            # This assumes values is a list of ints
            # like [2000, 456, 123]
            count = sum(values)

            # stats_list_by_period = date_convert_to_string(stats_list_by_period)

            return {'labels': labels,
                    'values': values,
                    'count': count,
                    'label_colour_map': label_colour_map,
                    'label_names_map': label_names_map,
                    'second_grouping': second_grouping}

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

    def ids_to_human_readable_labels(
        self,
        ids_list: list,
        group_by: str):
        """
        SO clearly WIP not very composable yet
        ALSO note 100% clear if it's great to worry about getting the labels
        seperetly like this... Is there a way to built it into group by?

        Careful with order here...
        Getting the ids from a list does not preserve order...

        I swear we were doing something with this type of id
        to object mapping before but maybe eventually trying to make this
        more generic...
        https://stackoverflow.com/questions/35316864/sqlalchemy-get-query-results-in-same-order-as-in-clause
        """

        human_readable = []

        if group_by == 'label':

            label_file_list = File.get_by_id_list(self.session, ids_list)

            id_to_label_file = {file.id: file for file in label_file_list}

            # CAUTION we are using ids list to maintain order
            # Append None if issue so as to keep order.
            for id in ids_list:
                attribute = None
                file = id_to_label_file.get(id)
                if file and file.label:
                    attribute = file.label.name
                human_readable.append(attribute)

        # note we are handling this on the front end
        # Probably can delete this block
        if group_by == 'user':
            # TODO get member list...
            # Then return relevant info....
            pass

        return human_readable


@routes.route('/api/v1/report/info/<int:report_template_id>',
              methods = ['GET'])
@General_permissions.grant_permission_for(['normal_user'])
def report_info_api(report_template_id):
    """
    Permissions handled by Report_Runner
    """

    with sessionMaker.session_scope() as session:
        report_runner = Report_Runner(
            session = session,
            member = None,
            report_template_id = report_template_id
        )

        if len(report_runner.log["error"].keys()) >= 1:
            return jsonify(log = report_runner.log), 400

        report_runner.get_existing_report_template(report_template_id)

        report_runner.validate_existing_report_id_permissions()

        report_runner.log['success'] = True

        return jsonify(
            log = report_runner.log,
            report_template = report_runner.report_template.serialize()), 200


@routes.route('/api/v1/report/save',
              methods = ['POST'])
@General_permissions.grant_permission_for(['normal_user'])
def report_save_api():
    """
    May or may not have an ID if it's new.

    I think it's save for save to be different from running it.

    metadata meaning it's data one level removed from actual report
    ie how the report should be structured
    see report_spec for an example

    """
    spec_list = [
        {"report_template_id": {
            'kind': int,
            'required': False  # (ie for first save)
        }
        },
        {'metadata': dict}
    ]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        report_runner = Report_Runner(
            session = session,
            member = None,
            report_template_id = input['report_template_id'],
            metadata = input['metadata']
        )

        if len(report_runner.log["error"].keys()) >= 1:
            return jsonify(log = report_runner.log), 400

        # TODO abstract this check into a better function to share with running it
        if input['metadata'].get('diffgram_wide_default') is True:

            # TODO edge case of default wide === false (After
            # prior being True) is not handled yet

            user = User.get(session)
            if user is None or user.is_super_admin is not True:
                log['error']['permission'] = "'diffgram_wide_default' Invalid permission."
                return jsonify(log = log), 400
        else:
            report_runner.validate_report_permissions_scope(
                scope = input['metadata'].get('scope'),
                project_string_id = input['metadata'].get('project_string_id'),
            )

        report_runner.save()

        if len(report_runner.log["error"].keys()) >= 1:
            return jsonify(log = report_runner.log), 400

        report_runner.log['success'] = True

        return jsonify(
            log = report_runner.log,
            report_template = report_runner.report_template.serialize()), 200


@routes.route('/api/v1/report/run',
              methods = ['POST'])
@General_permissions.grant_permission_for(['normal_user'])
def run_report_api():
    """

    Question:
        [] Idea that we could hit the same end point,
        and either pass a specification for the report we want
        OR an ID??

        Another option is two sperate APIs that join up
        when they get to the "Core" part of it...

        Should this also return report metadata?
        (seems silly to have a seperate thing for that? or)...

        I guess it's possible we may want to get report info without ...

    Answer:
     For now we assume we must have a saved report to run it
     as a future optimization can look at more ways to
     run this just in "preview" mode...

    """

    spec_list = [
        {"report_template_id": {
            'kind': int,
            'required': False
        }
        },
        {"report_template_data": {
            'kind': dict,
            'required': False
        }
        },
        {"project_string_id": {
            'kind': str,
            'default': None,
            'required': False
        }
        }
    ]

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = spec_list)

    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400
    if input.get('report_template_id') is None and input.get('report_template_data') is None:
        log['error']['report_template'] = 'Provide report_template_id or report_template_data'
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        report_runner = Report_Runner(
            session = session,
            member = None,
            report_template_id = input['report_template_id'],
            report_template_data = input['report_template_data'],
            project_string_id = input['project_string_id']
        )

        if len(report_runner.log["error"].keys()) >= 1:
            return jsonify(log = report_runner.log), 400

        report_runner.get_existing_report_template(input['report_template_id'])

        """
        For Diffgram wide reports, they only need to validate the project string id
        BUT if it's not, then the project_string_id should match too.
        """
        if report_runner.report_template is not None:
            if report_runner.report_template.diffgram_wide_default is True:
                report_runner.validate_existing_report_id_permissions(
                    project_string_id = input['project_string_id'])
            else:
                # This assume project based...
                # this should be part of that other permission scope validation.
                # testing but going to say http://127.0.0.1:8085/report/4
                # with a non super user, will need to revist this for super admins too
                if report_runner.report_template.project.project_string_id != input['project_string_id']:
                    raise Forbidden("No access to this project.")

                report_runner.validate_existing_report_id_permissions(
                    project_string_id = input['project_string_id'])
        else:
            # Case where not report_template_id is provided (only report_template_data)
            Project_permissions.user_has_project(Roles = ["admin", "Editor", "Viewer"])
        results = report_runner.run()

        if len(report_runner.log["error"].keys()) >= 1:
            return jsonify(log = report_runner.log), 400

        log['success'] = True
        return jsonify(log = report_runner.log,
                       report_template = report_runner.report_template.serialize(),
                       stats = results), 200
