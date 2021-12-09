from shared.database.common import *


class Action_Event(Base):
    """
    Design doc:
    https://docs.google.com/document/d/1gMddC4vR1vnrO7WxGm1p6kUCzSnvk2FuX3lZkfJsBh0/edit#heading=h.brnwo25wzzr

    Created for each "Run" of each action in a flow

    """

    __tablename__ = 'action_event'
    id = Column(BIGINT, primary_key = True)

    flow_event_id = Column(BIGINT, ForeignKey('action_flow_event.id'))
    flow_event = relationship("Action_Flow_Event", foreign_keys = [flow_event_id])

    file_id = Column(BIGINT, ForeignKey('file.id'))
    file = relationship("File", foreign_keys = [file_id])

    action_id = Column(BIGINT, ForeignKey('action.id'))
    action = relationship("Action", foreign_keys = [action_id])

    # Cache here
    kind = Column(String())

    flow_id = Column(Integer, ForeignKey('action_flow.id'))
    flow = relationship("Action_Flow", foreign_keys = [flow_id])

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

    # Reuse image class setup for clarity
    overlay_rendered_image_id = Column(Integer, ForeignKey('image.id'))  # new feb 12 2019
    overlay_rendered_image = relationship("Image",
                                          foreign_keys = [overlay_rendered_image_id])

    @staticmethod
    def new(session,
            flow_event_id,
            flow_id,
            action_id,
            file_id,
            project_id = None,
            org = None,
            link = None,
            member = None,
            kind = None
            ):
        """
        objects vs ids here...

        Not using member yet.

        """
        if flow_event_id is None:
            return

        action_event = Action_Event(
            flow_event_id = flow_event_id,
            flow_id = flow_id,
            action_id = action_id,
            file_id = file_id,
            project_id = project_id,
            org = org,
            kind = kind
        )

        session.add(action_event)
        return action_event

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

        query = session.query(Action_Event).filter(
            Action_Event.flow_event_id == id,
            Action_Event.project_id == project_id)

        # if active_only is True:
        #	query = query.filter(Action.active == True)

        if return_kind == "count":
            return query.limit(limit).count()

        if return_kind == "objects":
            return query.limit(limit).all()

    def serialize(self,
                  session = None):

        # Question, do we want to include
        # Other information about the action?
        # ie serialize the "original" action too
        # so perosn can see how it flowed through system?

        # session if needed to regen urls
        self.session = session

        event = {
            'id': self.id,
            'kind': self.kind,
            'time_created': self.time_created
        }

        # Get kind specific attributes
        kind_specific = self.kind_specific_serialize_strategy.get(
            self.kind)
        if kind_specific is None:
            return "class Action Event Serialize Error. Error, no kind"

        event[self.kind] = kind_specific(self)

        return event

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
