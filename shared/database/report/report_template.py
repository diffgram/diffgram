# OPENCORE - ADD
from shared.database.common import *


class ReportTemplate(Base):
    __tablename__ = 'report_template'

    """

    Metadata about the report template

    Columns are done by Column

    NOTE 
        May 1, 2020 
            If adding items, make sure to add to serialize too,
            since the report save assumes that will exist.
        
    """

    id = Column(Integer, primary_key = True)

    name = Column(String())

    diffgram_wide_default = Column(Boolean, default = False)

    archived = Column(Boolean, default = False)

    scope = Column(String, default = "project")

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", foreign_keys = [project_id])

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_updated_id])

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    # Meta data
    # User, Instance etc.
    base_class_string = Column(String())

    group_by = Column(String())

    # dynamic period
    # all, last_week, last 14 days, last month, last year etc…
    # 1_hour, 6_hours, 12_hours, 1_day, 2_days, 4_days, 7_days
    # always in context of current to previous right?
    period = Column(String(), default = "last_30_days")

    # Return type is decided by the view?

    # day, month
    date_period_unit = Column(String())

    compare_to_previous_period = Column(Boolean, default = False)

    # TODO add a list relation
    # ie to access Column objects from here...
    # and filters etc...

    task_id = Column(Integer, ForeignKey('task.id'))
    task = relationship("Task", foreign_keys = [task_id])

    # New May 11, 2020
    job_id = Column(Integer, ForeignKey('job.id'))
    job = relationship("Job", foreign_keys = [job_id])
    # If we wanted to add a multiple select filter for this in the future
    # Could have a 'job_id_list' as part of the filters concept.
    # I'm really wondering if we need a multiple select here...

    member_list = Column(ARRAY(Integer), nullable = True, default = [])

    filter_by_items = Column(MutableDict.as_mutable(JSONEncodedDict),
                             default = {
                                 'label_file_id_list': [],
                                 'directory_id_list': [],
                                 'jobs_id_list': []
                             })

    # WIP, NEW April 15, 2020
    report_dashboard_id = Column(Integer, ForeignKey('report_dashboard.id'))
    report_dashboard = relationship("ReportDashboard", foreign_keys = [report_dashboard_id])

    is_visible_on_report_dashboard = Column(Boolean, default = True)

    ### VIEW information
    view_type = Column(String())  # [count, rows, chart, objects]
    # 'objects' is internal only maybe

    # Maybe what type of chart?
    view_sub_type = Column(String())  # [web_chart, future]...

    group_by_labels = Column(Boolean, default = False)

    @staticmethod
    def get_by_id(session,
                  id: int):

        return session.query(ReportTemplate).filter(
            ReportTemplate.id == id).first()

    def serialize(self):

        # Context that current permissions
        # thing looks at this when we save it back again
        # not id (long story)
        project_string_id = None
        if self.project:
            project_string_id = self.project.project_string_id

        label_file_id_list = None
        if self.filter_by_items:
            label_file_id_list = self.filter_by_items.get('label_file_id_list')

        time_updated = None
        if self.time_updated:
            time_updated = self.time_updated.strftime('%m/%d/%Y, %H:%M:%S')

        return {
            'id': self.id,
            'name': self.name,
            'scope': self.scope,
            'project_id': self.project_id,
            'project_string_id': project_string_id,  # note no self
            'member_created_id': self.member_created_id,
            'member_updated': self.member_updated,
            'time_created': self.time_created.strftime('%m/%d/%Y, %H:%M:%S'),
            'time_updated': time_updated,
            'base_class_string': self.base_class_string,
            'group_by_labels': self.group_by_labels,
            'group_by': self.group_by,
            'period': self.period,
            'date_period_unit': self.date_period_unit,
            'compare_to_previous_period': self.compare_to_previous_period,
            'archived': self.archived,
            'view_type': self.view_type,
            'report_dashboard_id': self.report_dashboard_id,
            'diffgram_wide_default': self.diffgram_wide_default,
            'view_sub_type': self.view_sub_type,
            'is_visible_on_report_dashboard': self.is_visible_on_report_dashboard,
            'job_id': self.job_id,
            'label_file_id_list': label_file_id_list,
            'task_id': self.task_id

        }

    @staticmethod
    def list_default_reports(
        session,
        only_is_visible_on_report_dashboard = None
    ):

        query = session.query(ReportTemplate)
        query = query.filter(ReportTemplate.diffgram_wide_default == True)
        query = query.filter(ReportTemplate.archived == False)

        # ie report list may have 20 (active) default reports
        # but dashboard only has 3....
        if only_is_visible_on_report_dashboard:
            query = query.filter(
                ReportTemplate.is_visible_on_report_dashboard == True)

        return query.all()

    @staticmethod
    def list(
        session,
        scope: str,
        project = None,
        limit = 100,
        return_kind = "objects",
        date_to = None,
        date_from = None,
        report_dashboard_id = None,
        only_is_visible_on_report_dashboard = None
    ):
        """
        We take objects so it's easier to work if we don't know
        scope in advance

        """
        query = session.query(ReportTemplate)

        query = query.filter(ReportTemplate.diffgram_wide_default == False)
        query = query.filter(ReportTemplate.archived == False)

        if report_dashboard_id:
            query = query.filter(
                ReportTemplate.report_dashboard_id == report_dashboard_id)

        if only_is_visible_on_report_dashboard:
            query = query.filter(
                ReportTemplate.is_visible_on_report_dashboard == True)

        if scope == "project" and project:
            query = query.filter(ReportTemplate.project_id == project.id)


        else:
            return False

        # TODO this is missing the "AND" joint thing for date_from
        if date_from:
            query = query.filter(ReportTemplate.time_created >= date_from)

        if date_to:
            query = query.filter(ReportTemplate.time_created <= date_to)

        if return_kind == "count":
            return query.limit(limit).count()

        if return_kind == "objects":
            return query.limit(limit).all()

    @staticmethod
    def new(
        member: 'Member' = None,
        project: 'Project' = None) -> 'ReportTemplate':

        report_template = ReportTemplate(
            member_created = member,
            project = project,
        )

        return report_template
