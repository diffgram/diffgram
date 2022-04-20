from shared.database.common import *
from shared.database.action.workflow import Workflow
SUPPORTED_ACTION_TRIGGER_EVENT_TYPES = [
    'task_completed',
    'task_created',
    'task_template_completed',
    'input_file_uploaded',
    'input_instance_uploaded'
]


class WorkFlowTriggerEventQueue(Base):
    """
        A system generated event that might be a possible trigger a workflow or action inside a workflow.
        Contains metadata like the related objects, who triggered it and other relevant information.

        This table will work as a queue, so all elements that are beings processed here will be eventually
        deleted when they have been processed.

    """

    __tablename__ = 'workflow_trigger_event_queue'

    id = Column(BIGINT, primary_key = True)

    type = Column(
        String())  # ['task_completed', 'task_template_completed', 'input_files_uploaded', 'input_instances_uploaded']

    has_aggregation_event_running = Column(Boolean(), default = False)

    aggregation_window_start_time = Column(DateTime, default = None)

    input_id = Column(BIGINT, ForeignKey('input.id'))
    input = relationship("Input", foreign_keys = [input_id])

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project")

    task_id = Column(Integer, ForeignKey('task.id'))
    task = relationship("Task", foreign_keys = [task_id])

    job_id = Column(Integer, ForeignKey('job.id'))
    job = relationship("Job", foreign_keys = [job_id])

    workflow_id = Column(Integer, ForeignKey('workflow.id'))
    workflow = relationship(Workflow, foreign_keys = [workflow_id])

    org_id = Column(Integer, ForeignKey('org.id'))
    org = relationship("Org", foreign_keys = [org_id])

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_updated_id])

    @staticmethod
    def list(session = None,
             workflow_id = None,
             type = None,
             has_aggregation_event_running = None):

        query = session.query(WorkFlowTriggerEventQueue)
        if workflow_id:
            query = query.filter(WorkFlowTriggerEventQueue.workflow_id == workflow_id)
        if type:
            query = query.filter(WorkFlowTriggerEventQueue.type == type)
        if has_aggregation_event_running:
            query = query.filter(
                WorkFlowTriggerEventQueue.has_aggregation_event_running == has_aggregation_event_running
            )

        return query.all()

    @staticmethod
    def enqueue_new_event(session = None,
                          add_to_session = False,
                          flush_session = False,
                          type = None,
                          input_id = None,
                          project_id = None,
                          task_id = None,
                          job_id = None,
                          org_id = None,
                          workflow_id = None,
                          has_aggregation_event_running = False,
                          aggregation_window_start_time = None,
                          member_created_id = None,
                          member_updated_id = None):
        """
            Adds a new event to the actions queue.
        :param session:
        :param add_to_session:
        :param flush_session:
        :param type:
        :param input_id:
        :param project_id:
        :param task_id:
        :param job_id:
        :param org_id:
        :param workflow_id:
        :param has_aggregation_event_running:
        :param aggregation_window_start_time:
        :param member_created_id:
        :param member_updated_id:
        :return:
        """

        workflow_trigger_event = WorkFlowTriggerEventQueue(
            type = type,
            input_id = input_id,
            project_id = project_id,
            task_id = task_id,
            job_id = job_id,
            org_id = org_id,
            workflow_id = workflow_id,
            time_created = datetime.datetime.now(),
            member_created_id = member_created_id,
            member_updated_id = member_updated_id,
            has_aggregation_event_running = has_aggregation_event_running,
            aggregation_window_start_time = aggregation_window_start_time,
            time_updated = datetime.datetime.now(),
        )
        if add_to_session:
            session.add(workflow_trigger_event)
        if flush_session:
            session.flush()

        return workflow_trigger_event

    @staticmethod
    def get_next(session):
        """
            Gets the next element in the queue to process.
        :param session:
        :return:
        """
        result = session.query(WorkFlowTriggerEventQueue).with_for_update(skip_locked = True) \
            .order_by(WorkFlowTriggerEventQueue.time_created).all()
        if len(result) == 0:
            return None
        else:
            return result[0]
    def serialize(self):

        file = None
        if self.file:
            file = self.file.serialize_with_type()

        flow = {
            'id': self.id,
            'status': self.status,
            'status_description': self.status_description,
            'file': file
        }

        return flow
