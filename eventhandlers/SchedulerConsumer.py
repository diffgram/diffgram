import json
import pika
import threading
from pika.exchange_type import ExchangeType
from pika.channel import Channel
from shared.queueclient.QueueClient import RoutingKeys, Exchanges, QueueNames
from TaskScheduler import diffgram_scheduler
from shared.shared_logger import get_shared_logger
import functools
from shared.regular import regular_log
from shared.helpers.sessionMaker import session_scope_threaded
from shared.queueclient.QueueClient import QueueClient, RoutingKeys, Exchanges
import json
from shared.database.action.workflow import Workflow
logger = get_shared_logger()

def trigger_workflow(workflow_id: int, project_id: int):
    with session_scope_threaded() as session:
        workflow = Workflow.get(session = session, workflow_id = workflow_id)
        msg = {
            'workflow_id': workflow_id,
            'member_id': workflow.member_created_id,
            'kind': 'time_trigger',
            'project_id': project_id,
            'action_id': None
        }
        queueclient = QueueClient()
        logger.debug(f"Triggering Workflow {workflow_id}...")
        queueclient.send_message(message = msg,
                                 routing_key = RoutingKeys.action_trigger_event_new.value,
                                 exchange = Exchanges.actions.value)

class SchedulerConsumer:

    def __init__(self, channel: Channel, connection: pika.SelectConnection):
        self.channel = channel
        self.connection = connection
        cb = functools.partial(self.on_exchange_declareok,
                               userdata = {})

        self.exchange = self.channel.exchange_declare(
            exchange = Exchanges.scheduler.value,
            exchange_type = ExchangeType.direct.value,
            passive = False,
            auto_delete = False,
            callback = cb
        )

    def on_exchange_declareok(self, _unused_frame, userdata):
        logger.info(f'Scheduler Consumer Created. Adding Queues...')
        self.channel.queue_declare(queue = QueueNames.scheduler_tasks.value)
        self.channel.queue_bind(
            queue = QueueNames.scheduler_tasks.value,
            exchange = Exchanges.scheduler.value,
            routing_key = RoutingKeys.scheduler.value)
        self.channel.basic_qos(prefetch_count = 1)
        threads = []
        on_message_callback = functools.partial(SchedulerConsumer.on_message, args = (self.connection, threads))
        self.channel.basic_consume(queue = QueueNames.scheduler_tasks.value,
                                   on_message_callback = on_message_callback,
                                   auto_ack = True)
        logger.info('Scheduler Queues ready to listen for messages')

    @staticmethod
    def on_message(ch, method_frame, _header_frame, body, args):
        (conn, thrds) = args
        delivery_tag = method_frame.delivery_tag
        t = threading.Thread(target = SchedulerConsumer.process_new_event, args = (conn, ch, delivery_tag, body))
        t.start()
        thrds.append(t)

    @staticmethod
    def process_new_event(channel, method, properties, msg):
        """
            Receives a trigger event a fi
            queueclient = QueueClient()nds any actions
            matching the event trigger for action
            execution.
        :return:
        """
        logger.debug(f'New Scheduler Message:  {msg}')
        msg_data = json.loads(msg)
        log = regular_log.default()
        if msg_data.get('workflow_id') is None:
            log['error']['workflow_id'] = f'Message must contain workflow_id. Message is: {msg_data}'
        if msg_data.get('project_id') is None:
            log['error']['project_id'] = f'Message must contain project_id. Message is: {msg_data}'
        if msg_data.get('action') is None:
            log['error']['action'] = f'Message most contain an action. Message is: {msg_data}'
        if msg_data.get('cron_expression') is None:
            log['error']['cron_expression'] = f'Message must contain a cron_expression. Message is: {msg_data}'


        if regular_log.log_has_error(log):
            logger.error(f'Error processing jobs message: {log}')
            return

        workflow_id = msg_data.get('workflow_id')
        project_id = msg_data.get('project_id')
        action = msg_data.get('action')
        cron_expression = msg_data.get('cron_expression')
        logger.debug(f'Processing Scheduler event: {msg}')

        with session_scope_threaded() as session:
            if action == 'add':
                diffgram_scheduler.add_job(job_id = workflow_id, cron_expr = cron_expression, func = trigger_workflow, args = [workflow_id, project_id])
            elif action == 'remove':
                diffgram_scheduler.remove_job(job_id = workflow_id)
            else:
                logger.warning(f'Scheduler Consumer: Unknown action type "{action}"')
            logger.debug(f'Scheduler event processed successfully. {msg}')