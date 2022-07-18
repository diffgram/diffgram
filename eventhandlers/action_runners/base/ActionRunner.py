import traceback

from shared.database.action.action import Action
from shared.queueclient.QueueClient import QueueClient, RoutingKeys, Exchanges
from shared.database.event.event import Event
from shared.regular import regular_log
from shared.helpers import sessionMaker
from shared.database.action.action_template import Action_Template
from shared.shared_logger import get_shared_logger
from shared.database.action.action_run import ActionRun
from sqlalchemy.orm.session import Session
from action_runners.base.ActionTrigger import ActionTrigger
from action_runners.base.ActionCondition import ActionCondition
from action_runners.base.ActionCompleteCondition import ActionCompleteCondition
from shared.data_tools_core import Data_tools

logger = get_shared_logger()

data_tools = Data_tools().data_tools

class ActionRegistrationError(Exception):
    pass


class ActionRunner:
    action: Action
    event_data: dict
    log: dict
    public_name: str
    icon: str
    kind: str
    category: str
    description: str
    trigger_data: ActionTrigger
    session: Session
    precondition: ActionCondition
    completion_condition_data: ActionCompleteCondition
    action_run: ActionRun

    def __init__(self, session, action = None, event_data: dict = None):
        self.session = session
        self.action = action
        self.event_data = event_data
        self.log = regular_log.default()
        self.mngr = QueueClient()

    def save_html_output(self, session, html_data: str):
        self.action.output = {'html': html_data}
        self.action_run.output = {'html': html_data}
        session.add(self.action)
        session.add(self.action_run)

    def execute_pre_conditions(self, session: Session) -> bool:
        """
        Function to determine if pre conditions for execution are met.
        Returns true if action can be executed and False if actions cannot be executed.
        :param session:
        :return:
        """
        raise NotImplementedError

    def execute_action(self, session: Session) -> dict:
        """
            Function that executes main action logic. This is implemented on the subclasses of the `ActionRunner`
        :param session:
        :return:
        """
        raise NotImplementedError

    def verify_registration_data(self) -> None:
        """

        :return:
        """
        fields = ['public_name',
                  'description',
                  'icon',
                  'kind',
                  'trigger_data',
                  'precondition',
                  'completion_condition_data']
        for field in fields:
            if self.__getattribute__(field) is None:
                msg = f'Error registering {self.__class__}. Provide {field}'
                logger.error(msg)
                raise ActionRegistrationError(msg)

    def update(self, session) -> None:
        self.verify_registration_data()
        payload = {
            "public_name": self.public_name,
            "description": self.description,
            "trigger_data": self.trigger_data.build_data(),
            "precondition": self.precondition.build_data(),
            "completion_condition_data": self.completion_condition_data.build_data(),
            "icon": self.icon,
            "category": None
        }
        Action_Template.update_by_kind(session, self.kind, payload)

    def register(self, session) -> None:
        self.verify_registration_data()
        Action_Template.register(
            session = session,
            public_name = self.public_name,
            description = self.description,
            icon = self.icon,
            kind = self.kind,
            category = None,
            trigger_data = self.trigger_data.build_data() if self.trigger_data else None,
            condition_data = self.precondition.build_data() if self.precondition else None,
            completion_condition_data = self.completion_condition_data.build_data() if self.completion_condition_data else None,
        )

    def run(self) -> None:
        """
        Executes the action. This method does not need to be overriden.
        The method calls `execute_pre_conditions` and then `execute_action`.
        Finally it calls `declare_action_complete` or `declare_action_failed` depending on outcome
        :return:
        """
        session = self.session
        self.action_run = ActionRun.new(
            session = session,
            workflow_id = self.action.workflow_id,
            action_id = self.action.id,
            project_id = self.action.project_id,
            workflow_run_id = None,
            file_id = None
        )

        allow = self.execute_pre_conditions(session)

        if not allow:
            return
        try:
            output = self.execute_action(session)
        except Exception as e:
            msg = traceback.format_exc()
            logger.error(msg)
            self.log['error']['trace'] = msg
            self.declare_action_failed(session)
            return
        if output:
            if isinstance(output, dict):
                self.action_run.output = output

            self.declare_action_complete(session, output)
        else:
            self.declare_action_failed(session)

    def declare_action_failed(self, session: Session) -> None:
        Event.new(
            session = session,
            action_id = self.action.id,
            kind = 'action_failed',
            error_log = self.log,
            project_id = self.action.project_id,
        )

    def declare_action_complete(self, session: Session, output) -> None:
        has_output = isinstance(output, dict)
        event_payload = {
            'session': session,
            'action_id': self.action.id,
            'kind': 'action_completed',
            'project_id': self.action.project_id,
            'file_id': None if not has_output else output.get('file_id'),
            'task_id': None if not has_output else output.get('task_id'),

        }
        print('DECLARE ACTION COMPELTEEED', event_payload)
        if has_output:
            event_payload['extra_metadata'] = output
        Event.new(
            **event_payload
        )