from shared.database.common import *


class Action(Base):
    """

    Instance of an action.
    A flow has many actions.
    An action has many (Action) Events


    """

    __tablename__ = 'action'
    id = Column(BIGINT, primary_key = True)

    kind = Column(String())

    active = Column(Boolean)
    archived = Column(Boolean, default = False)  # Hide from list

    # Soft delete? Issues? etc...
    status = Column(String())

    template_id = Column(Integer, ForeignKey('action_template.id'))
    template = relationship("Action_Template", foreign_keys = [template_id])

    flow_id = Column(Integer, ForeignKey('action_flow.id'))
    flow = relationship("Action_Flow", foreign_keys = [flow_id])

    is_root = Column(Boolean)
    root_id = Column(Integer, ForeignKey('action.id'))

    def root(self, session):
        return Action.get_by_id(session, self.root_id)

    parent_id = Column(Integer, ForeignKey('action.id'))

    def parent(self, session):
        return Action.get_by_id_skip_project_security_check(
            session, self.parent_id)

    def child_list(self, session):
        return session.query(Action).filter(
            Action.parent_id == self.id).all()

    child_primary_id = Column(Integer, ForeignKey('action.id'))

    def child_primary(self, session):
        return Action.get_by_id_skip_project_security_check(
            session, self.child_primary_id)

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project")

    org_id = Column(Integer, ForeignKey('org.id'))
    org = relationship("Org", foreign_keys = [org_id])

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_updated_id])

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    # Action style
    # Action kind then thing
    # ie  brain_thin

    brain_kind = Column(String())  # ie "new" or "train" or ...

    brain_run_visual = Column(Boolean)

    brain_completion_directory_id = Column(Integer, ForeignKey('working_dir.id'))
    brain_completion_directory = relationship("WorkingDir")

    # Count label x actions

    count_label_file_id = Column(Integer, ForeignKey('file.id'))
    count_label_file = relationship("File", foreign_keys = [count_label_file_id])

    count = Column(Integer)  # ie 1, 4, 0
    count_confidence_threshold = Column(Float)  # ie 0.50 prediction confidence

    # Condition action

    condition_operator = Column(String)  # (equals, less than, greater than, etc.)

    condition_left_operand = Column(String)
    condition_right_operand = Column(String)

    # How the condition evaulates
    condition_true_exists = Column(Boolean)
    condition_false_exists = Column(Boolean)

    condition_true_action_id = Column(Integer, ForeignKey('action.id'))
    condition_false_action_id = Column(Integer, ForeignKey('action.id'))

    # Time delay

    time_delay = Column(Integer)  # In seconds?...

    # Send email

    email_send_to = Column(String())
    email_subject = Column(String())
    email_body = Column(String())

    # Webhooks
    url_to_post = Column(String())
    secret_webhook = Column(String())

    # Overlay

    # New June 19, 2019

    overlay_kind = Column(String())  # "text", "image", "icon" ?
    overlay_text = Column(String())

    overlay_image_id = Column(Integer, ForeignKey('image.id'))  # new feb 12 2019
    overlay_image = relationship("Image",
                                 foreign_keys = [overlay_image_id])

    overlay_position = Column(String())  # Center, Top_Corner
    overlay_size = Column(String())  # Fill?

    overlay_label_file_id = Column(Integer, ForeignKey('file.id'))
    overlay_label_file = relationship("File", foreign_keys = [overlay_label_file_id])

    @staticmethod
    def new(
        session,
        project,
        kind,
        org,
        member,
        flow,
        template
    ):
        """
        We default active to True for easier searching

        Does NOT add to session since we only
        want to do that for success cases
        """

        if flow is None:
            return False

        action = Action(
            active = True,
            kind = kind,
            project = project,
            org = org,
            member_created = member,
            flow = flow,
            template = template
        )

        return action

    # WIP WIP WIP
    def serialize(self):
        """
        pattern is that the kind specific thing gets inserted as a dict
        and we stripe away the kind_ thing
        so condition_something becomes condition.something for front end
        this is to maintain the dict setup the front end seems to
        need, and flat structure shared.database wants
        Likely a better way so if you know one please speak up!

        """

        # Do we want to include all this other info by default or?

        # Common start
        action = {
            'id': self.id,
            'kind': self.kind,
            'active': self.active,
            'flow_id': self.flow_id,
            'project_id': self.project_id,
            'template_id': self.template_id
        }

        # Get kind specific attributes
        kind_specific = self.kind_specific_strategy_operations_serialize.get(self.kind)
        if kind_specific is None:
            return "class Action Serialize Error. Error, no kind"

        action[self.kind] = kind_specific(self)

        return action

    def serialize_file(self):
        pass

    def serialize_brain_run(self):

        brain_dict = self.brain_ai.serialize()
        brain_dict['brain_run_visual'] = self.brain_run_visual

        return brain_dict

    def serialize_count(self):

        label_file = None
        if self.count_label_file:
            label_file = self.count_label_file.serialize_with_label()

        return {
            'label_file': label_file
        }

    def serialize_condition(self):

        return {
            'left_operand': self.condition_left_operand,
            'right_operand': self.condition_right_operand,
            'operator': self.condition_operator
        }

    def serialize_delay(self):
        pass

    def serialize_email(self):

        return {
            'send_to': self.email_send_to,
            'subject': self.email_subject,
            'body': self.email_body
        }

    def serialize_webhook(self):
        return {
            'url_to_post': self.url_to_post
        }

    def serialize_overlay(self):

        label_file = None
        if self.overlay_label_file:
            label_file = self.overlay_label_file.serialize_with_label()

        # TOOD may need to pass session
        overlay_image = None
        if self.overlay_image:
            overlay_image = self.overlay_image.serialize(),

        return {
            'label_file': label_file,
            'overlay_image': overlay_image,
            'kind': self.overlay_kind
        }

    kind_specific_strategy_operations_serialize = {
        "file": serialize_file,
        "brain_run": serialize_brain_run,
        "count": serialize_count,
        "condition": serialize_condition,
        "delay": serialize_delay,
        "email": serialize_email,
        "webhook": serialize_webhook,
        "overlay": serialize_overlay
    }

    @staticmethod
    def list(
        session,
        flow_id,
        project_id,
        active_only = True,
        archived = False,
        limit = 100,
        return_kind = "objects"
    ):
        """

        Require project id for security

        """

        query = session.query(Action).filter(
            Action.flow_id == flow_id,
            Action.project_id == project_id,
            Action.archived == archived
        )

        if active_only is True:
            query = query.filter(Action.active == True)

        # For now we assume we want it ordered this way
        query = query.order_by(Action.id)

        if return_kind == "count":
            return query.limit(limit).count()

        if return_kind == "objects":
            return query.limit(limit).all()

    @staticmethod
    def get_by_id(session,
                  id,
                  project_id = None):
        """
        Must include project id for security check

        (This assumes untrusted source)...

        """

        return session.query(Action).filter(
            Action.id == id,
            Action.project_id == project_id).first()

    @staticmethod
    def get_by_id_skip_project_security_check(
        session,
        id):
        """
        Must include project id for security check

        (This assumes untrusted source)...

        """

        return session.query(Action).filter(
            Action.id == id).first()
