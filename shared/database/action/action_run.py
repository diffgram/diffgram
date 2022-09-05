from shared.database.common import *


class ActionRun(Base):
    """
    Design doc:
    https://docs.google.com/document/d/1gMddC4vR1vnrO7WxGm1p6kUCzSnvk2FuX3lZkfJsBh0/edit#heading=h.brnwo25wzzr

    Created for each "Run" of each action in a workflow

    """

    __tablename__ = 'action_run'
    id = Column(BIGINT, primary_key = True)

    workflow_run_id = Column(BIGINT, ForeignKey('workflow_run.id'))
    workflow_run = relationship("WorkflowRun", foreign_keys = [workflow_run_id])

    file_id = Column(BIGINT, ForeignKey('file.id'))
    file = relationship("File", foreign_keys = [file_id])

    status = Column(String())
    action_id = Column(BIGINT, ForeignKey('action.id'))
    action = relationship("Action", foreign_keys = [action_id])

    # Cache here
    kind = Column(String())

    workflow_id = Column(Integer, ForeignKey('workflow.id'))
    workflow = relationship("Workflow", foreign_keys = [workflow_id])

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project")

    org_id = Column(Integer, ForeignKey('org.id'))
    org = relationship("Org", foreign_keys = [org_id])

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    # If we want a scrambeld URL link?
    link_to_results = Column(String())

    # Count label x actions
    count = Column(Integer)

    # TODO add count_result
    # count_result = Column(Boolean)

    # Condition action
    condition_true = Column(Boolean)
    condition_false = Column(Boolean)

    condition_result = Column(Boolean)

    # Time delay
    # None relevant here?

    # Send email

    email_was_sent_to = Column(String())
    email_subject = Column(String())
    email_body = Column(String())

    # Output of action, usually caches the output of latest ActionRun.
    output = Column(MutableDict.as_mutable(JSONB))

    # Reuse image class setup for clarity
    overlay_rendered_image_id = Column(Integer, ForeignKey('image.id'))  # new feb 12 2019
    overlay_rendered_image = relationship("Image",
                                          foreign_keys = [overlay_rendered_image_id])

    @staticmethod
    def new(session,
            workflow_id,
            action_id,
            file_id = None,
            workflow_run_id = None,
            project_id = None,
            org = None,
            kind = None
            ):
        """
            Creates a new Action run.
        :param session:
        :param workflow_run_id:
        :param workflow_id:
        :param action_id:
        :param file_id:
        :param project_id:
        :param org:
        :param link:
        :param member:
        :param kind:
        :return:
        """
        action_run = ActionRun(
            workflow_id = workflow_id,
            workflow_run_id = workflow_run_id,
            action_id = action_id,
            file_id = file_id,
            project_id = project_id,
            org = org,
            kind = kind
        )

        session.add(action_run)
        session.flush()
        return action_run

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

        query = session.query(WofklowRun).filter(
            WofklowRun.flow_event_id == id,
            WofklowRun.project_id == project_id)

        # if active_only is True:
        #	query = query.filter(Action.active == True)

        if return_kind == "count":
            return query.limit(limit).count()

        if return_kind == "objects":
            return query.limit(limit).all()

    @staticmethod
    def list_by_action_id(session, action_id, limit = None, offset = None):
        query = session.query(ActionRun).filter(ActionRun.action_id == action_id)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return query.all()

    def serialize_action_run(self):
        return {
            'id': self.id,
            'output': self.output
        }

    def serialize(self, session = None):

        action_run_data = {
            'id': self.id,
            'kind': self.kind,
            'output': self.output,
            'workflow_id': self.workflow_id,
            'action_id': self.action_id,
            'time_created': self.time_created
        }

        return action_run_data

    def serialize_file(self):
        pass

    def serialize_brain_new(self):

        brain_inference = self.brain_inference.serialize()

        return brain_inference

    def serialize_count(self):

        return {
            'count': self.count
        }

    def serialize_condition(self):

        return {
            'condition_result': self.condition_result
        }

    def serialize_delay(self):
        pass

    def serialize_email(self):

        return {}

    def serialize_overlay(self):

        return {
            'image_rendered': self.overlay_rendered_image.serialize_for_source_control(
                session = self.session)
        }

    # Down here so that functions can load

    kind_specific_serialize_strategy = {
        "file": serialize_file,
        "brain_run": serialize_brain_new,
        "count": serialize_count,
        "condition": serialize_condition,
        "delay": serialize_delay,
        "email": serialize_email,
        "overlay": serialize_overlay
    }
