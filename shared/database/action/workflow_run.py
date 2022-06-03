from shared.database.common import *


class WorkflowRun(Base):
    """
    Direct link to class in design doc:
    https://docs.google.com/document/d/1gMddC4vR1vnrO7WxGm1p6kUCzSnvk2FuX3lZkfJsBh0/edit#heading=h.mzaw1n5b53n

    The execution of a Workflow

    """

    __tablename__ = 'workflow_run'
    id = Column(BIGINT, primary_key = True)

    status = Column(String())
    status_description = Column(String())

    # New June 20, 2019
    file_id = Column(BIGINT, ForeignKey('file.id'))
    file = relationship("File", foreign_keys = [file_id])

    workflow_id = Column(Integer, ForeignKey('workflow.id'))
    workflow = relationship("Workflow", foreign_keys = [workflow_id])

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project")

    org_id = Column(Integer, ForeignKey('org.id'))
    org = relationship("Org", foreign_keys = [org_id])

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    # If we want a scrambled URL link?
    link_to_results = Column(String())

    @staticmethod
    def new(session,
            workflow = None,
            project = None,
            org = None,
            file = None
            ):
        """

        Careful, flow_id and flow_event_id are different!!!
        flow_id is template, flow_event_id is instance of it

        """

        workflow_run = WorkflowRun(
            workflow = workflow,
            project = project,
            org = org,
            file = file
        )

        session.add(workflow_run)

        # To get id
        session.flush()

        return workflow_run

    @staticmethod
    def list(
        session,
        id,
        project_id,
        active_only = True,
        limit = 100,
        return_kind = "objects"
    ):
        """

        Require project id for security

        active_only not used yet

        Careful we want this based on flow id not event id!

        """

        query = session.query(WorkflowRun).filter(
            WorkflowRun.flow_id == id,
            WorkflowRun.project_id == project_id)

        # if active_only is True:
        #	query = query.filter(Action.active == True)

        query = query.order_by(WorkflowRun.id.desc())

        if return_kind == "count":
            return query.limit(limit).count()

        if return_kind == "objects":
            return query.limit(limit).all()

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
