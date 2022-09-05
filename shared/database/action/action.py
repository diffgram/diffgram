from shared.database.common import *
from shared.database.org.org import Org
from shared.database.action.action_template import Action_Template
from sqlalchemy.dialects.postgresql import JSONB
from enum import Enum
from sqlalchemy_serializer import SerializerMixin
class ActionTriggerEventTypes(Enum):
    task_completed = 'task_completed'
    task_created = 'task_created'
    task_review_start = 'task_review_start'
    task_request_changes = 'task_request_changes'
    task_review_complete = 'task_review_complete'
    task_in_progress = 'task_in_progress'
    task_comment_created = 'task_comment_created'
    task_template_completed = 'task_template_completed'
    input_file_uploaded = 'input_file_uploaded'
    input_instance_uploaded = 'input_instance_uploaded'
    action_completed = 'action_completed'
    manual_trigger = 'manual_trigger'
    file_copy = 'file_copy'
    file_move = 'file_move'
    file_mirror = 'file_mirror'


class ActionKinds(Enum):
    create_task = 'create_task'
    export = 'export'


class Action(Base, SerializerMixin):
    """
        Each step of a workflow is called an action.

    """

    __tablename__ = 'action'
    id = Column(BIGINT, primary_key = True)

    kind = Column(String())

    active = Column(Boolean)
    archived = Column(Boolean, default = False)  # Hide from list

    # Soft delete? Issues? etc...
    status = Column(String())

    template_id = Column(Integer, ForeignKey('action_template.id'))
    template = relationship(Action_Template, foreign_keys = [template_id])

    workflow_id = Column(Integer, ForeignKey('workflow.id'))
    workflow = relationship("Workflow", foreign_keys = [workflow_id])

    public_name = Column(String())

    icon = Column(String())

    description = Column(String())

    trigger_data = Column(MutableDict.as_mutable(JSONB))

    config_data = Column(MutableDict.as_mutable(JSONB))

    precondition = Column(MutableDict.as_mutable(JSONB))

    completion_condition_data = Column(MutableDict.as_mutable(JSONB))

    # Output of action, usually caches the output of latest ActionRun.
    output = Column(MutableDict.as_mutable(JSONB))

    # This is possible return of the output
    output_interface = Column(MutableDict.as_mutable(JSONB))

    ordinal = Column(Integer)

    is_root = Column(Boolean)
    root_id = Column(Integer, ForeignKey('action.id'))

    parent_id = Column(Integer, ForeignKey('action.id'))

    child_primary_id = Column(Integer, ForeignKey('action.id'))

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project")

    org_id = Column(Integer, ForeignKey('org.id'))
    org = relationship(Org, foreign_keys = [org_id])

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

    # Action preconditions


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
    def get_triggered_actions(session, trigger_kind: str, project_id = None):
        from shared.database.action.workflow import Workflow
        actions = session.query(Action).join(Workflow, Action.workflow_id == Workflow.id).filter(
            Workflow.active == True,
            Action.archived == False,
            Action.project_id == project_id,
            Action.trigger_data['event_name'].astext == trigger_kind
        ).all()
        return actions


    @staticmethod
    def new(
        session,
        project,
        kind,
        member,
        workflow,
        template,
        trigger_data,
        icon,
        description,
        ordinal,
        precondition,
        completion_condition_data,
        public_name,
        add_to_session = True,
        flush_session = True,
        output_interface = None,
    ):
        """
        We default active to True for easier searching

        Does NOT add to session since we only
        want to do that for success cases
        """

        if workflow is None:
            return False

        action = Action(
            active = True,
            kind = kind,
            project = project,
            member_created = member,
            workflow = workflow,
            template = template,
            trigger_data = trigger_data,
            icon = icon,
            description = description,
            ordinal = ordinal,
            public_name = public_name,
            completion_condition_data = completion_condition_data,
            output_interface = output_interface,
            precondition = precondition
        )
        if add_to_session:
            session.add(action)

        if flush_session:
            session.flush()

        return action

    def get_previous_action(self, session) -> 'Action':
        ordinal = self.ordinal
        if ordinal == 0:
            return None
        action = session.query(Action).filter(
            Action.ordinal == ordinal - 1,
            Action.workflow_id == self.workflow_id,
            Action.project_id == self.project_id
        ).first()
        return action


    def serialize(self):
        """
        pattern is that the kind specific thing gets inserted as a dict
        and we stripe away the kind_ thing
        so condition_something becomes condition.something for front end
        this is to maintain the dict setup the front end seems to
        need, and flat structure shared.database wants
        Likely a better way so if you know one please speak up!

        """
        data = self.to_dict(rules = (
            '-template',
            '-workflow',
            '-project',
            '-org',
            '-count_label_file',
            '-overlay_label_file',
            '-overlay_image',
            '-member_created',
            '-member_updated'))

        return data

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
            Action.workflow_id == flow_id,
            Action.project_id == project_id,
            Action.archived == archived
        )

        if active_only is True:
            query = query.filter(Action.active == True)

        # For now we assume we want it ordered this way
        query = query.order_by(Action.id)

        if return_kind == "count":
            if limit:
                return query.limit(limit).count()
            else:
                return query.count()
        if return_kind == "objects":
            if limit:
                return query.limit(limit).all()
            else:
                return query.all()

    @staticmethod
    def get_by_id(session,
                  id,
                  project_id = None) -> 'Action':
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

    def parent(self, session):
        return Action.get_by_id_skip_project_security_check(
            session, self.parent_id)

    def child_list(self, session):
        return session.query(Action).filter(
            Action.parent_id == self.id).all()

    def child_primary(self, session):
        return Action.get_by_id_skip_project_security_check(
            session, self.child_primary_id)

    def root(self, session):
        return Action.get_by_id(session, self.root_id)
