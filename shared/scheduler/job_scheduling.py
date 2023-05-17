from shared.queueclient.QueueClient import RoutingKeys, Exchanges, QueueClient
from shared.shared_logger import get_shared_logger

logger = get_shared_logger()


def remove_job_scheduling(workflow_id: int, project_id: int):
    msg_data = {
        'workflow_id': workflow_id,
        'project_id': project_id,
        'action': 'remove',
        'cron_expression': '',
    }
    logger.info(f'Removing Task Schedule {msg_data}')
    # Send message for batch processing on Rabbit
    queueclient = QueueClient()
    queueclient.send_message(message = msg_data,
                             routing_key = RoutingKeys.scheduler.value,
                             exchange = Exchanges.scheduler.value)


def add_job_scheduling(workflow_id: int, project_id: int, cron_expression: str):
    logger.info(f'Sending Task Schedule')
    msg_data = {
        'workflow_id': workflow_id,
        'project_id': project_id,
        'action': 'add',
        'cron_expression': cron_expression,
    }
    logger.info(f'Sending Task Schedule {msg_data}')
    # Send message for batch processing on Rabbit
    queueclient = QueueClient()
    queueclient.send_message(message = msg_data,
                             routing_key = RoutingKeys.scheduler.value,
                             exchange = Exchanges.scheduler.value)
