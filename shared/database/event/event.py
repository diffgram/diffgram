# OPENCORE - ADD
from shared.database.common import *
import analytics
from shared.shared_logger import get_shared_logger
import threading
import requests
import shared.helpers.sessionMaker as sessionMaker
from shared.helpers.sessionMaker import AfterCommitAction
from shared.queueclient.QueueClient import QueueClient, Exchanges, RoutingKeys


logger = get_shared_logger()
# The extra imports are only needed if they haven't already been
# imported somewhere else by the ORM

analytics.write_key = settings._ANALYTICS_WRITE_KEY

if settings.DIFFGRAM_SYSTEM_MODE == "sandbox":
    def on_error(error, items):
        print("An error occurred:", error)


    analytics.debug = True
    analytics.on_error = on_error

    # Don't send in debug mode
    analytics.send = False


class Event(Base):
    __tablename__ = 'event'

    """

    Stuff that happens in the system
    ie
    New project

    kind = new_project
    member_id = "person / api key who created it"

    link = [url to new project, for user facing activity?]

    description = "optional string information on the event?"
    
    """

    id = Column(BIGINT, primary_key = True)

    kind = Column(String())

    page_name = Column(String())

    object_type = Column(String())

    description = Column(String())

    success = Column(Boolean)

    error_log = Column(MutableDict.as_mutable(JSONEncodedDict))
    # Would prefer to store full error log like mutable dict?

    run_time = Column(Float)  # In milliseconds ie using time.time()
    # Not required, but relevant for long running operations, ie export_generation
    # also something we could potentially turn on on demand if
    # an issue is detected around an event

    link = Column(String())  # Context of being able to go to event
    # This could easily become out of date, but at least it's a starting point

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project")

    input_id = Column(Integer, ForeignKey('input.id'))
    input = relationship("Input")

    task_id = Column(Integer, ForeignKey('task.id'))
    task = relationship("Task")

    job_id = Column(Integer, ForeignKey('job.id'))
    job = relationship("Job")

    member_id = Column(Integer, ForeignKey('member.id'))
    member = relationship('Member', foreign_keys = [member_id])

    file_id = Column(Integer, ForeignKey('file.id'))
    file = relationship("File")

    directory_id = Column(Integer, ForeignKey('working_dir.id'))
    directory = relationship("WorkingDir")

    action_id = Column(Integer, ForeignKey('action.id'))
    action = relationship("Action")

    workflow_id = Column(Integer, ForeignKey('workflow.id'))
    workflow = relationship("Workflow")

    report_template_id = Column(Integer, ForeignKey('report_template.id'))
    report_template = relationship("ReportTemplate")

    report_template_data = Column(MutableDict.as_mutable(JSONEncodedDict))
    report_data = Column(MutableDict.as_mutable(JSONEncodedDict))

    install_fingerprint = Column(String)

    diffgram_version = Column(String)

    extra_metadata = Column(MutableDict.as_mutable(JSONB))

    # We don't need an "update" since this is meant to be a static record??
    time_created = Column(DateTime, default = datetime.datetime.utcnow)

    def serialize(self):
        return {
            'id': self.id,
            'kind': self.kind,
            'description': self.description,
            'error_log': self.error_log,
            'object_type': self.object_type,
            'page_name': self.page_name,
            'input_id': self.input_id,
            'project_id': self.project_id,
            'directory_id': self.directory_id,
            'action_id': self.action_id,
            'workflow_id': self.workflow_id,
            'file_id': self.file_id,
            'task_id': self.task_id,
            'job_id': self.job_id,
            'member_id': self.member_id,
            'report_template_data': self.report_template_data,
            'report_data': self.report_data,
            'time_created': self.time_created.strftime('%Y-%m-%d'),
            'install_fingerprint': self.install_fingerprint,
            'diffgram_version': settings.DIFFGRAM_VERSION_TAG,
            'host_os': settings.DIFFGRAM_HOST_OS,
            'storage_backend': settings.DIFFGRAM_STATIC_STORAGE_PROVIDER,
            'service_name': settings.DIFFGRAM_SERVICE_NAME,
            'extra_metadata': self.extra_metadata
        }

    def serialize_for_visit_history(self, session):

        return {
            'id': self.id,
            'kind': self.kind,
            'description': self.description,
            'error_log': self.error_log,
            'object_type': self.object_type,
            'page_name': self.page_name,
            'project_string_id': self.project.project_string_id,
            'input_id': self.input_id,
            'file_id': self.file_id,
            'task_id': self.task_id,
            'job_id': self.job_id,
            'member_id': self.member_id,
            'time_created': self.time_created.strftime('%Y-%m-%d')

        }

    @staticmethod
    def get_by_id(
        id: int,
        session):

        if id is None: return False

        return session.query(Event).filter(Event.id == id).first()

    @staticmethod
    def new_deferred(session = None,
                     kind = None,
                     member_id = None,
                     success = None,
                     error_log = None,
                     description = None,
                     directory_id = None,
                     link = None,
                     project_id = None,
                     task_id = None,
                     job_id = None,
                     run_time = None,
                     email = None,
                     member = None,
                     input_id = None,
                     add_to_session = True,
                     flush_session = True,
                     file_id = None,
                     wait_for_commit = True):
        """
        Keyword Arg Note:
            Any keyword args added here will be propagated to
                __new_event_threaded()
                __launch_new_event_threaded()
                AfterCommitAction

            Session is removed by default
            wait_for_commit is removed after waiting

        Therefore to add/remove a keyword arg it needs 'only' 3 places:
            new_deferred() argument
            new()  argument
            new()  Event() literal

        This makes it relatively easy to read, and easier to add.
        The assumption here is that the format of after_commit, and starting the thread
        will change relatively slowly, but we expect we will wish to add new arguments

        Try block because in general events are a "secondary" concern, so we don't 
        want to risk disrupting core operation if this fails for some reason
        """

        try:
            event_args = locals()
            event_args.pop('session', None)  # Other downstream processes don't expect this key

            if wait_for_commit:
                event_args.pop('wait_for_commit', None)
                if kind in ['task_created', 'task_completed', 'input_file_uploaded', 'task_template_completed']:
                    AfterCommitAction(session = session,
                                      callback = Event.__launch_new_event_threaded,
                                      callback_args = event_args)
            else:
                Event.__launch_new_event_threaded(**event_args)
        except Exception as exception:
            logger.error(str(exception))

    @staticmethod
    def __new_event_threaded(**kwargs):
        event_args = locals().get('kwargs')  # Because using the **kwargs instead of actual args we need one more 'get'
        with sessionMaker.session_scope_threaded() as session:
            event_args['session'] = session
            event_args['flush_session'] = True  # for ID
            event = Event.new(**event_args)
            event_id = int(event.id)
            event_kind = event.kind

    @staticmethod
    def __launch_new_event_threaded(**kwargs):
        t = threading.Thread(
            target = Event.__new_event_threaded,
            kwargs = locals().get('kwargs'))
        t.daemon = True  # Allow hot reload to work
        t.start()

    def broadcast(self):
        if settings.DIFFGRAM_SYSTEM_MODE == 'testing':
            return
        queue_mngr = QueueClient()
        message = self.serialize()
        queue_mngr.send_message(message = message,
                                routing_key = RoutingKeys.event_new.value,
                                exchange = Exchanges.events.value)
    @staticmethod
    def new(session,
            kind = None,
            member_id = None,
            success = None,
            error_log = None,
            description = None,
            link = None,
            project_id = None,
            task_id = None,
            directory_id = None,
            run_time = None,
            page_name = None,
            object_type = None,
            job_id = None,
            email = None,
            member = None,
            input_id = None,
            file_id = None,
            action_id = None,
            workflow_id = None,
            report_data = None,
            report_template_id = None,
            report_template_data = None,
            add_to_session = True,
            flush_session = True,
            extra_metadata = None
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
        if member:
            member_id = member.id

            user = member.user
            if user:
                email = user.email
        event = Event(
            kind = kind,
            member_id = member_id,
            success = success,
            error_log = error_log,
            description = description,
            link = link,
            project_id = project_id,
            task_id = task_id,
            job_id = job_id,
            directory_id = directory_id,
            run_time = run_time,
            object_type = object_type,
            input_id = input_id,
            file_id = file_id,
            action_id = action_id,
            workflow_id = workflow_id,
            report_data = report_data,
            report_template_id = report_template_id,
            report_template_data = report_template_data,
            page_name = page_name,
            extra_metadata = extra_metadata
        )
        if add_to_session:
            session.add(event)
        if flush_session:
            session.flush()
        Event.track_user(event, email)
        logger.debug(f'Created event {event.id}:{event.kind}')
        #event.send_to_eventhub()
        event.broadcast()
        return event



    def send_to_eventhub(self):
        """
            Sends the current event to Diffgram's EventHub for anonymous data tracking.
        :return:
        """
        from shared.settings import settings
        EXCLUDED_EVENTHUB_TRACKING_EVENTS = ['user_visit']
        if settings.DIFFGRAM_SYSTEM_MODE in ['testing', 'testing_e2e']:
            return

        if settings.DIFFGRAM_SYSTEM_MODE in ['sandbox'] and self.kind in EXCLUDED_EVENTHUB_TRACKING_EVENTS:
            return
        
        if settings.ALLOW_EVENTHUB is False:
            return
        
        try:
            event_data = self.serialize()
            event_data['event_type'] = 'user'
            event_data['install_fingerprint'] = settings.DIFFGRAM_INSTALL_FINGERPRINT
            result = requests.post(settings.EVENTHUB_URL, json = event_data, timeout = 3)
            if result.status_code == 200:
                logger.debug(f"Sent event: {self.id} to Diffgram Eventhub")
            else:
                logger.error(
                    f"Error sending ID: {self.id} to Eventhub. Status Code: {result.status_code}. result.text: {result.text}")
        except Exception as e:
            logger.error(f"Exception sending {str(e)} to Diffgram Eventhub: ")

    @staticmethod
    def identify_user(user):
        """
        user, class User DB object

        Expects to be run within a session

        Note already checking system mode uptop with
        "if settings.DIFFGRAM_SYSTEM_MODE == "sandbox"

        """
        # This is just for passing info about a user
        # to system
        if settings.DIFFGRAM_SYSTEM_MODE in ['testing', 'testing_e2e']:
            return
        try:
            analytics.identify(user.member_id, {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'how_hear_about_us': user.how_hear_about_us,
                'signup_role': user.signup_role,
                'signup_demo': user.signup_demo,
                'city': user.city,
                'company': user.company_name
            })
        except:
            print("Analytics error")
            pass

    @staticmethod
    def track_user(
        event,
        email = None):
        # Validate an event exists.
        if settings.DIFFGRAM_SYSTEM_MODE in ['testing', 'testing_e2e']:
            return
        if event is None:
            return
        if event.member_id is None:
            return
        if email is None:
            return
        if not settings._ANALYTICS_WRITE_KEY:
            return
        # CAREFUL using MEMBER id NOT user id.
        props = {
            'description': event.description,
            'success': event.success,
            'run_time': event.run_time,
            'email': email,
            'project_id': event.project_id
        }
        if event.error_log is not None and type(event.error_log) is dict:
            props.update(event.error_log)
        try:
            analytics.track(
                user_id = event.member_id,
                event = event.kind,
                properties = props,
                context = {
                    'traits': {
                        event.kind: True
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error tracking user: {e}")
            pass

    @staticmethod
    def list(
        session,
        project_id: int,
        limit: int = 10,
        kind: str = None,
        member_id: int = None,
        date_from_string: str = None,
        date_to_string: str = None,
        file_id: int = None):

        """
        """

        # Front end pagination does -1 for All
        if limit == -1:
            limit = 1000
        limit = min(limit, 1000)

        query = session.query(Event).filter(
            Event.project_id == project_id)

        if kind:
            kind = kind.lower()
            query = query.filter(Event.kind == kind)

        if member_id:
            query = query.filter(Event.member_id == member_id)

        query = regular_methods.regular_query(
            query = query,
            date_from_string = date_from_string,
            date_to_string = date_to_string,
            base_class = Event
        )

        if file_id:
            query = query.filter(Event.file_id == file_id)

        event_list = query.order_by(
            Event.id.desc()).limit(limit).all()

        return event_list
