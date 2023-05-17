from shared.database.common import *

import random
import string
from shared.database.action.action import Action

TIME_WINDOW_SECONDS_MAPPER = {
    '1_minute': 1 * 60,
    '5_minutes': 5 * 60,
    '10_minutes': 10 * 60,
    '30_minutes': 30 * 60,
    '1_hours': 60 * 60,
    '4_hours': 60 * 60 * 4,
    '12_hours': 60 * 60 * 12,
    '1_days': 60 * 60 * 24,
}


class Workflow(Base):
    """

    Group of actions.
    Ie a user creates a flow where an Action A then Action B happens


    """

    __tablename__ = 'workflow'
    id = Column(Integer, primary_key = True)

    name = Column(String())
    string_id = Column(String())

    time_window = Column(String())

    active = Column(Boolean)  # Running / not running
    archived = Column(Boolean, default = False)  # Hide from list
    is_new = Column(Boolean, default = True)

    kind = Column(String())

    trigger_type = Column(String())  # Reference types from ActionFlowTriggerEventQueue

    count_events = Column(Integer)

    # New Jun 18 2019  foreign key not added yet
    directory_id = Column(Integer, ForeignKey('working_dir.id'))
    directory = relationship("WorkingDir",
                             foreign_keys = [directory_id])

    first_action_id = Column(BIGINT, ForeignKey('action.id'))
    first_action = relationship(Action, foreign_keys = [first_action_id])

    last_action_id = Column(BIGINT, ForeignKey('action.id'))
    last_action = relationship(Action, foreign_keys = [last_action_id])

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

    @staticmethod
    def new(
        session,
        project,
        org,
        name,
        member,
        trigger_type = None,
        time_window = None,

    ):
        # Else create a new one
        workflow = Workflow(
            active = False,
            project = project,
            org = org,
            name = name,
            trigger_type = trigger_type,
            time_window = time_window,
            member_created = member)

        Workflow.update_string_id(
            session = session,
            workflow = workflow)

        session.add(workflow)
        session.flush()

        return workflow

    def has_time_trigger(self, session) -> bool:
        first_action = self.get_first_action(session = session)
        return first_action and first_action.trigger_data.get('event_name') == 'time_trigger' and first_action.trigger_data.get('cron_expression')
    def get_existing_unmodified_flow(
        session,
        project,
        member
    ):
        """
        Concept that it gets a new flow that exists instead of creating
        new one (if unedited)

        relies on setting is_new to False by update methods

        this could cause issues
        but it seems so silly to keep recreating blank ones

        member so if two people created same one in same project...

        """

        return session.query(Workflow).filter(
            Workflow.is_new == True,
            Workflow.member_created == member,
            Workflow.project == project).first()

    def serialize(self):

        # Include project id or?

        return {
            'id': self.id,
            'string_id': self.string_id,
            'name': self.name,
            'trigger_type': self.trigger_type,
            'time_window': self.time_window,
            'active': self.active,
            'time_updated': self.time_updated
        }

    @staticmethod
    def get(session, workflow_id: int):
        """
            Gets a single workflow by ID.
        :param session:
        :param workflow_id:
        :return:
        """
        return session.query(Workflow).filter(Workflow.id == workflow_id).first()

    @staticmethod
    def get_by_id(session,
                  id,
                  project_id = None):
        """
        Must include project id for security check

        (This assumes untrusted source)...

        """

        return session.query(Workflow).filter(
            Workflow.id == id,
            Workflow.project_id == project_id).first()

    def get_by_string_id(
        session,
        string_id):

        return session.query(Workflow).filter(
            Workflow.string_id == string_id).first()

    @staticmethod
    def list(
        session,
        project_id,
        active_only = None,
        archived = False,
        trigger_type = None,
        limit = 100,
        return_kind = "objects"
    ):
        """

        """

        query = session.query(Workflow).filter(
            Workflow.archived == False,
            Workflow.project_id == project_id)

        if active_only is True:
            query = query.filter(Workflow.active == True)

        if trigger_type is not None:
            query = query.filter(Workflow.trigger_type == trigger_type)

        if return_kind == "count":
            return query.limit(limit).count()

        if return_kind == "objects":
            return query.order_by(Workflow.time_created).limit(limit).all()

    @staticmethod
    def update_string_id(
        session,
        workflow):

        # Not super happy with this here...
        if workflow.name is None:
            workflow.name = "Untitled flow"

        workflow.string_id = safe_name(workflow.name)

        workflow.string_id += f"_{create_random_string(length=20)}"


    def serialize_with_actions(self, session):
        data = self.serialize()
        actions = Action.list(
            session = session,
            flow_id = self.id,
            project_id = self.project_id,
            limit = None
        )
        data['actions_list'] = [a.serialize() for a in actions]
        return data

    def get_first_action(self, session) -> Action:
        action = session.query(Action).filter(
            Action.workflow_id == self.id,
            Action.ordinal == 0,
            Action.archived == False).first()
        return action


# 'abcdefghijklmnopqrstuvwxyz0123456789'
# can add chars in front if needed ie "." etc.
valid_chars = f"{string.ascii_letters}{string.digits}"


def safe_name(name, character_limit = 10):
    # TODO review using unicdoe normalize ie
    # https://gist.github.com/wassname/1393c4a57cfcbf03641dbc31886123b8

    name = name[:character_limit]

    name = name.lower()  # Email safe no upper case
    # Want to preserve user capitilized things though

    safe_name = ""

    for char in name:
        if char in valid_chars:
            safe_name += char

    return safe_name


# see auth_api_new copied from there
def create_random_string(length):
    # Email safe, so no upper case

    return ''.join(random.choice(
        string.ascii_lowercase +
        string.digits) for x in range(length))
