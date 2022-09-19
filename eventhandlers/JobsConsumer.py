import json
import pika
import threading
from pika.exchange_type import ExchangeType
from pika.channel import Channel
from shared.queueclient.QueueClient import RoutingKeys, Exchanges, QueueNames
from shared.database.action.action import ActionTriggerEventTypes
from shared.shared_logger import get_shared_logger
from shared.queueclient.QueueClient import QueueClient
import functools
from shared.regular import regular_log
from shared.utils import job_dir_sync_utils
from shared.utils.sync_events_manager import SyncEventManager
from shared.helpers.sessionMaker import session_scope_threaded
from shared.database.task.job.job import Job
from shared.database.source_control.file import File
from shared.database.source_control.working_dir import WorkingDir
from shared.database.auth.member import Member

logger = get_shared_logger()


class JobsConsumer:

    def __init__(self, channel: Channel, connection: pika.SelectConnection):
        self.channel = channel
        self.connection = connection
        cb = functools.partial(self.on_exchange_declareok,
                               userdata = {})

        self.exchange = self.channel.exchange_declare(
            exchange = Exchanges.jobs.value,
            exchange_type = ExchangeType.direct.value,
            passive = False,
            auto_delete = False,
            callback = cb
        )

    def on_exchange_declareok(self, _unused_frame, userdata):
        logger.info(f'BulkTaskCreation Created. Adding Queues...')
        self.channel.queue_declare(queue = QueueNames.job_tasks.value)
        self.channel.queue_bind(
            queue = QueueNames.job_tasks.value,
            exchange = Exchanges.jobs.value,
            routing_key = RoutingKeys.job_add_task.value)
        self.channel.basic_qos(prefetch_count = 1)
        threads = []
        on_message_callback = functools.partial(JobsConsumer.on_message, args = (self.connection, threads))
        self.channel.basic_consume(queue = QueueNames.job_tasks.value,
                                   on_message_callback = on_message_callback,
                                   auto_ack = True)
        logger.info('Queues ready to listen for messages')

    @staticmethod
    def on_message(ch, method_frame, _header_frame, body, args):
        (conn, thrds) = args
        delivery_tag = method_frame.delivery_tag
        t = threading.Thread(target = JobsConsumer.process_new_event, args = (conn, ch, delivery_tag, body))
        t.start()
        thrds.append(t)

    @staticmethod
    def process_new_event(channel, method, properties, msg):
        """
            Receives a trigger event a fi        queueclient = QueueClient()nds any actions matching the event trigger for action
            execution.
        :return:
        """
        logger.debug(f'New Job Message:  {msg}')
        msg_data = json.loads(msg)
        log = regular_log.default()
        if msg_data.get('task_template_id') is None:
            log['error']['task_template_id'] = f'Message most contain task template ID. Message is: {msg_data}'
        if msg_data.get('file_id_list') is None:
            log['error']['file_id_list'] = f'Message most contain a file_id_list. Message is: {msg_data}'
        if msg_data.get('member_id') is None:
            log['error']['member_id'] = f'Message most contain a member_id. Message is: {msg_data}'

        if regular_log.log_has_error(log):
            logger.error(f'Error processing jobs message: {log}')
            return

        task_template_id = msg_data.get('task_template_id')
        file_id_list = msg_data.get('file_id_list')
        member_id = msg_data.get('member_id')
        logger.debug(f'Creating tasks for Job: {msg}')

        with session_scope_threaded() as session:
            task_template = Job.get_by_id(session = session, job_id = task_template_id)
            files = File.get_by_id_list(session = session, file_id_list = file_id_list)
            member = Member.get_by_id(session = session, member_id = member_id)
            job_sync_manager = job_dir_sync_utils.JobDirectorySyncManager(
                session = session,
                job = task_template,
                log = log
            )
            for file in files:
                directories_ids = File.get_directories_ids(session = session, file_id = file.id)
                directory = WorkingDir.get_by_id(session = session, directory_id = directories_ids[0])
                sync_event_manager = SyncEventManager.create_sync_event_and_manager(
                    session = session,
                    dataset_source_id = directory,
                    dataset_destination = None,
                    description = 'Sync file from dataset {} to job {} and create task'.format(
                        directory.nickname,
                        task_template.name
                    ),
                    file = file,
                    job = task_template,
                    input_id = file.input_id,
                    project = task_template.project,
                    event_effect_type = 'create_task',
                    event_trigger_type = 'file_added',
                    status = 'init',
                    member_created = member
                )

                task, log = job_sync_manager.add_file_into_job(
                    file = file,
                    incoming_directory = directory,
                    job = task_template,
                    create_tasks = True,
                    sync_event_manager = sync_event_manager
                )

                if regular_log.log_has_error(log):
                    return None, log

            task_template.update_file_count_statistic(session)
            logger.info(f'{len(files)} Tasks created successfully.')