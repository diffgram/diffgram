from shared.database.common import *
from shared.shared_logger import get_shared_logger
logger = get_shared_logger()


class EventHub(Base):
    __tablename__ = 'event_hub'

    """
        Table for recording user events across all installations of Diffgram OpenCore/Enterprise.
        This table gets populated by making a POST request to the endpoint.
        
        /api/v1/eventhub/new
        
        For now it is a write only table, as we are still pending a more robust way of visualizing 
        this raw data and getting insightful analytics from it.

    """

    id = Column(BIGINT, primary_key=True)

    kind = Column(String(), index=True)

    page_name = Column(String())

    object_type = Column(String(), index=True)

    description = Column(String())

    success = Column(Boolean)

    error_log = Column(MutableDict.as_mutable(JSONEncodedDict))

    run_time = Column(Float)

    link = Column(String())

    project_id = Column(Integer)

    input_id = Column(Integer)

    task_id = Column(Integer)

    task_template_id = Column(Integer)

    member_id = Column(Integer)

    # New August 7th, 2019
    file_id = Column(Integer)

    report_template_id = Column(Integer)

    report_data = Column(MutableDict.as_mutable(JSONEncodedDict))

    report_template_data = Column(MutableDict.as_mutable(JSONEncodedDict))

    time_created = Column(DateTime, default=datetime.datetime.utcnow)

    startup_time = Column(DateTime, default = None, nullable = True)

    shut_down_time = Column(DateTime, default = None, nullable = True)

    install_fingerprint = Column(String())

    diffgram_version = Column(String())

    previous_version = Column(String())

    host_os = Column(String())

    storage_backend = Column(String())

    service_name = Column(String())

    event_type = Column(String())

    def serialize(self):
        return {
            'id': self.id,
            'kind': self.kind,
            'description': self.description,
            'error_log': self.error_log,
            'object_type': self.object_type,
            'page_name': self.page_name,
            'input_id': self.input_id,
            'file_id': self.file_id,
            'task_id': self.task_id,
            'task_template_id': self.task_template_id,
            'report_template_id': self.report_template_id,
            'report_data': self.report_data,
            'report_template_data': self.report_template_data,
            'member_id': self.member_id,
            'time_created': self.time_created.strftime('%m/%d/%Y, %H:%M:%S')

        }

    @staticmethod
    def new(session,
            kind=None,
            member_id=None,
            success=None,
            error_log=None,
            description=None,
            link=None,
            project_id=None,
            task_id=None,
            run_time=None,
            page_name=None,
            object_type=None,
            task_template_id=None,
            member=None,
            input_id=None,
            file_id=None,
            report_template_id=None,
            report_data=None,
            report_template_data=None,
            add_to_session=True,
            flush_session=True,
            install_fingerprint = None,
            diffgram_version = None,
            storage_backend = None,
            service_name = None,
            previous_version = None,
            host_os = None,
            startup_time = None,
            shut_down_time = None,
            event_type = None,
            ):
        """
        Generally we always want a member_id
        BUT till we have a better system to detect it there
        are some cases where we don't record it yet (ie brain training)

        As we add various checks,
        conditions, triggers etc. it's useful to have this
        as a generic "new" method. Also means we can "force"
        having a kind, etc...

        """

        # TODO handle if account is none? / check? hmmm

        # This allows smoother handling if we pass a member
        # Object... I guess that's better then it determining it?

        # Careful this overrides stuff effectively
        if member:
            member_id = member.id

            user = member.user
            if user:
                email = user.email

        event = EventHub(
            kind=kind,
            member_id=member_id,
            success=success,
            error_log=error_log,
            description=description,
            link=link,
            project_id=project_id,
            task_id=task_id,
            task_template_id=task_template_id,
            run_time=run_time,
            object_type=object_type,
            input_id=input_id,
            file_id=file_id,
            page_name=page_name,
            report_data=report_data,
            report_template_data=report_template_data,
            report_template_id=report_template_id,
            install_fingerprint = install_fingerprint,
            diffgram_version = diffgram_version,
            storage_backend = storage_backend,
            service_name = service_name,
            previous_version = previous_version,
            host_os = host_os,
            startup_time = startup_time,
            shut_down_time = shut_down_time,
            event_type = event_type,
        )
        if add_to_session:
            session.add(event)
        if flush_session:
            session.flush()

        return event
