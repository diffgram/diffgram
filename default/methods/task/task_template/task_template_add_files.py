# OPENCORE - ADD
from methods.regular.regular_api import *
from shared.database.task.job.job import Job
from typing import List
from sqlalchemy.orm.session import Session
from shared.queueclient.QueueClient import RoutingKeys, Exchanges, QueueClient
from shared.database.auth.member import Member
from shared.query_engine.query_creator import QueryCreator
from shared.query_engine.sqlalchemy_query_exectutor import SqlAlchemyQueryExecutor

@routes.route('/api/v1/job/<int:task_template_id>/add-files', methods = ['POST'])
@Job_permissions.by_job_id(
    project_role_list = ["admin", "Editor"],
    apis_project_list = [],
    apis_user_list = ["api_enabled_builder"])
def task_template_add_files_api(task_template_id):
    """
        Creates tasks for the given file id list or diffgram query value.
    :param task_template_id:
    :return:
    """
    spec_list = [
        {"file_id_list": {
            'required': False,
            'kind': list
        }
        },
        {"query": {
            'required': False,
            'kind': str
        }
        },
    ]
    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = spec_list)

    if regular_log.log_has_error(log):
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        member = get_member(session)
        add_files_result, log = task_template_add_files_core(session = session,
                                                             task_template_id = task_template_id,
                                                             member = member,
                                                             file_id_list = input.get('file_id_list'),
                                                             query = input.get('query'),
                                                             log = log)
        if regular_log.log_has_error(log):
            return jsonify(log = log), 400
        return jsonify(add_files_result), 200


def task_template_add_files_core(session: Session,
                                 task_template_id: int,
                                 member: Member,
                                 file_id_list: List[int] = None,
                                 query: str = None,
                                 log = regular_log.default()):
    task_template = Job.get_by_id(session, task_template_id)
    if task_template is None:
        log['error']['task_template'] = "Task Template does not exists."
        return False, log
    if not file_id_list and not query:
        log['error']['file_id_list'] = "Provide file_id_list or query for adding files."
        return False, log
    id_list = []
    if file_id_list:
        id_list = file_id_list
    elif query:
        query_creator = QueryCreator(session = session,
                                     project = task_template.project,
                                     member = member,
                                     directory = task_template.project.directory_default)
        diffgram_query_obj = query_creator.create_query(query_string = query)
        if regular_log.log_has_error(query_creator.log):
            log = query_creator.log
            logger.error(f'Error making query {query_creator.log}')
            return False, log
        executor = SqlAlchemyQueryExecutor(session = session, diffgram_query = diffgram_query_obj)
        sql_alchemy_query, log = executor.execute_query()
        if regular_log.log_has_error(log):
            log = query_creator.log
            logger.error(f'Error executing query {log}')
            return False, log
        files = sql_alchemy_query.all()
        id_list = [f.id for f in files]

    msg_data = {
        'file_id_list': id_list,
        'member_id': member.id,
        'task_template_id': task_template_id
    }
    # Send message for batch processing on Rabbit
    queueclient = QueueClient()
    queueclient.send_message(message = msg_data,
                             routing_key = RoutingKeys.job_add_task.value,
                             exchange = Exchanges.jobs.value)