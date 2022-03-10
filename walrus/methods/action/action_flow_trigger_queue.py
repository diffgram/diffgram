import threading
from methods.regular.regular_api import *
from shared.database.action.action_flow_trigger_event import ActionFlowTriggerEventQueue
from methods.action.action_pipeline import Action_Pipeline
import traceback
from shared.database.action.action_flow import Action_Flow
from shared.database.action.action_flow_trigger_event import SUPPORTED_ACTION_TRIGGER_EVENT_TYPES
from shared.regular.regular_methods import commit_with_rollback

class ActionFlowTriggerQueueThread:
    """
        This class will be in charge of processing the queue element in the
        ActionFlowEventsQueue for determining if a ActionFlow will be trigerred
        or not.
    """

    def __init__(self,
                 run_once=True,
                 thread_sleep_time_min=0,
                 thread_sleep_time_max=0, ):

        if run_once is True:
            self.thread = threading.Thread(
                target=self.check_if_events_to_process)
        else:
            self.thread_sleep_time_min = thread_sleep_time_min
            self.thread_sleep_time_max = thread_sleep_time_max

            self.thread = threading.Thread(target=self.start_queue_check_loop)

        if settings.DIFFGRAM_SYSTEM_MODE != 'testing':
            self.thread.daemon = True  # Allow hot reload to work
            self.thread.start()

    @staticmethod
    def try_to_enqueue_new_action_flows(session, event_id, commit_per_element=True):
        event = Event.get_by_id(session=session, id=event_id)
        project_id = event.project_id
        task_id = event.task_id
        job_id = event.job_id
        input_id = event.input_id
        member_id = event.member_id
        if event.kind in SUPPORTED_ACTION_TRIGGER_EVENT_TYPES and event.project_id:
            # Check for supported actions in flow registry
            action_flows = Action_Flow.list(session=session,
                                            project_id=project_id,
                                            trigger_type=event.kind)

            for action_flow in action_flows:
                # If the action flow has a time window configured, we should check if there's a running window first.
                if action_flow.time_window:
                    aggregation_trigger_event = ActionFlowTriggerEventQueue.list(
                        session=session,
                        has_aggregation_event_running=True,
                        action_flow_id=action_flow.id
                    )
                    # If there's an aggregation event running, we do nothing.
                    if len(aggregation_trigger_event) > 0:
                        logger.debug('Skipped event enqueue because aggregation event already exists.')
                        continue
                    # Otherwise we enqueue the first event and set the start time of the aggregation.
                    start_time = datetime.datetime.utcnow()
                    if event.kind == 'task_completed':
                        start_time = event.task.time_completed
                    if event.kind == 'task_created':
                        start_time = event.task.time_created
                    if event.kind == 'task_template_completed':
                        start_time = event.job.time_completed
                    if event.kind == 'input_file_uploaded':
                        start_time = event.input.created_time
                    ActionFlowTriggerEventQueue.enqueue_new_event(
                        session=session,
                        add_to_session=True,
                        type=event.kind,
                        project_id=project_id,
                        task_id=task_id,
                        job_id=job_id,
                        input_id=input_id,
                        member_created_id=member_id,
                        has_aggregation_event_running=True,
                        aggregation_window_start_time=start_time,
                        action_flow_id=action_flow.id)
                    if commit_per_element:
                        # We commit right away and add rollback in case a concurrent transaction occurs and
                        # a Integrity error is raised
                        # more info here: http://rachbelaid.com/handling-race-condition-insert-with-sqlalchemy/
                        try:
                            commit_with_rollback(session)
                        except:
                            continue
                else:
                    # Enqueue the event with no aggregation configurations.
                    ActionFlowTriggerEventQueue.enqueue_new_event(
                        session=session,
                        add_to_session=True,
                        type=event.kind,
                        project_id=project_id,
                        task_id=task_id,
                        job_id=job_id,
                        input_id=input_id,
                        member_created_id=member_id,
                        has_aggregation_event_running=None,
                        aggregation_window_start_time=None,
                        action_flow_id=action_flow.id)
                    if commit_per_element:
                        # We commit right away and add rollback in case a concurrent transaction occurs and
                        # a Integrity error is raised
                        # more info here: http://rachbelaid.com/handling-race-condition-insert-with-sqlalchemy/
                        try:
                            commit_with_rollback(session)
                        except:
                            continue
        return len(action_flows)

    def execute_action_flow_for_event(self, session, action_flow_trigger_event):
        """
            Exectutes the action flow given the trigger event.
        :return:
        """
        if not action_flow_trigger_event:
            return None
        logger.info(f"Executing flow for event {action_flow_trigger_event.id}")
        # Check if there are any other duplicate events on the window (In case of a concurrent update on the queue)
        # And if so delete, duplicate trigger_events with aggregations
        project = action_flow_trigger_event.project
        action_pipeline = Action_Pipeline(
            session=session,
            member=None,
            project=project,
            org=None,
            log=None,
            mode=None,
            file=None,
            trigger_event=action_flow_trigger_event,
            flow=action_flow_trigger_event.action_flow)
        action_pipeline.start()

    def check_if_events_to_process(self):
        """
            Gets the first element of the queue
        """
        action_flow_trigger_event_id = None
        logger.debug('Checking for Events to process.')
        try:
            with sessionMaker.session_scope_threaded() as session:

                # Main assumptions for pulling 1 at a time
                # 1) On deployments, each instance has multiple workers that run this. In that context, each worker can
                # grab the next element.
                # 2) Each ActionFlow triggering might be a heavy process.

                action_flow_trigger_event = ActionFlowTriggerEventQueue.get_next(session)
                # Can use sort in sql if needed here
                if action_flow_trigger_event is not None:
                    action_flow_trigger_event_id = int(action_flow_trigger_event.id)
                    self.execute_action_flow_for_event(session, action_flow_trigger_event)
                    session.query(ActionFlowTriggerEventQueue).filter(
                        ActionFlowTriggerEventQueue.id == action_flow_trigger_event.id
                    ).delete()
        except Exception as e:
            logger.error(f"Errror on action flow trigger queue. {str(e)}")
            if action_flow_trigger_event_id:
                with sessionMaker.session_scope_threaded() as session:
                    action_flow_trigger_event = session.query(ActionFlowTriggerEventQueue).filter(
                        ActionFlowTriggerEventQueue.id == action_flow_trigger_event_id
                    ).first()

                    logger.critical(f"Error launching Processing action event {action_flow_trigger_event.id}")
                    logger.error(traceback.format_exc())
                    logger.info('Deleting Action Trigger Event queue element'.format(action_flow_trigger_event.id))
                    session.query(ActionFlowTriggerEventQueue).filter(
                        ActionFlowTriggerEventQueue.id == action_flow_trigger_event_id
                    ).delete()

    def start_queue_check_loop(self):
        """

        """
        regular_methods.loop_forever_with_random_load_balancing(
            log_start_message='Starting ActionFlow Queue handler... ',
            log_heartbeat_message='[ActionFlow Queue heartbeat]',
            function_call=self.check_if_events_to_process,
            function_args={},
            thread_sleep_time_min=self.thread_sleep_time_min,
            thread_sleep_time_max=self.thread_sleep_time_max,
            logger=logger
        )
