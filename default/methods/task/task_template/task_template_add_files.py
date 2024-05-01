# OPENCORE - ADD
from methods.regular.regular_api import *  # Import regular_input for input validation
from shared.database.task.job.job import Job  # Job class for accessing task template
from typing import List  # For type hinting the file_id_list parameter
from sqlalchemy.orm.session import Session  # For database session handling
from shared.queueclient.QueueClient import RoutingKeys, Exchanges, QueueClient  # For sending messages to RabbitMQ
from shared.database.auth.member import Member  # Member class for accessing member information
from shared.query_engine.query_creator import QueryCreator  # For creating a query object from a string
from shared.query_engine.sqlalchemy_query_exectutor import SqlAlchemyQueryExecutor  # For executing the query

@routes.route('/api/v1/job/<int:task_template_id>/add-files', methods=['POST'])
@Job_permissions.by_job_id(
    project_role_list=["admin", "Editor"],
    apis_project_list=[],
    apis_user_list=["api_enabled_builder"])
def task_template_add_files_api(task_template_id):
    """
    Creates tasks for the given file id list or Diffgram query value.
    
    :param task_template_id: The ID of the task template to add files to
    :return: A JSON response containing the result of the operation and an HTTP status code
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

    # Validate and preprocess input data
    log, input, untrusted_input = regular_input.master(
        request=request,
        spec_list=spec_list,
        string_len_not_zero=False)

    # Return a 400 Bad Request response if there are any errors in the input data
    if regular_log.log_has_error(log):
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:
        member = get_member(session)
        add_files_result, log = task_template_add_files_core(session=session,
                                                             task_template_id=task_template_id,
                                                             member=member,
                                                             file_id_list=input.get('file_id_list'),
                                                             query=input.get('query'),
                                                             log=log)

        # Return a 400 Bad Request response if there are any errors in the processing
        if regular_log.log_has_error(log):
            return jsonify(log=log), 400
        return jsonify(add_files_result), 200


def task_template_add_files_core(session: Session,
                                 task_template_id: int,
                                 member: Member,
                                 file_id_list: List[int] = None,
                                 query: str = None,
                                 log=regular_log.default()):
    """
    Processes the request to add files to a task template based on the provided file IDs or Diffgram query value.

    :param session: The database session object
    :param task_template_id: The ID of the task template to add files to
    :param member: The member making the request
    :param file_id_list: A list of file IDs to add to the task template
    :param query: A Diffgram query value to add files to the task template
    :param log: The log object for recording errors and messages
    :return: A tuple containing the result of the operation and the log object
    """
    task_template = Job.get_by_id(session, task_template_id)

    # Check if the task template exists
    if task_template is None:
        log['error']['task_template'] = "Task Template does not exists."
        return False, log

    # Check if both file_id_list and query are None
    if not file_id_list and query is None:
        log['error']['file_id_list'] = "Provide file_id_list or query for adding files."
        return False, log

    id_list = []

    # Process the file_id_list parameter
    if file_id_list:
        id_list = file_id_list

    # Process the query parameter
    elif query is not None:
        query_creator = QueryCreator(session=session,
                                     project=task_template.project,
                                     member=member,
                                     directory=task_template.project.directory_default)

        # Create a query object from the query string
        diffgram_query_obj = query_creator.create_query(query_string=query)

        # Check for errors in creating the query
        if regular_log.log_has_error(query_creator.log):
            log = query_creator.log
            logger.error(f'Error making query {query_creator.log}')
            return False, log

        executor = SqlAlchemyQueryExecutor(session=session, diffgram_query=diffgram_query_obj)

        # Execute the query
        sql_alchemy_query, log = executor.execute_query()

        # Check for errors in executing the query
        if regular_log.log_has_error(log):
            log = query_creator.log
            logger.error(f'Error executing query {log}')
            return False, log

        # Get the list of file IDs from the query result
        files = sql_alchemy_query.all()
        id_list = [f.id for f in files]

    # Send a message to RabbitMQ for batch processing
    msg_data = {
        'file_id_list': id_list,
        'member_id': member.id,
        'task_template_id': task_template_id
    }
    queueclient = QueueClient()
    queueclient.send_message(message=msg_data,
                             routing_key=RoutingKeys.job_add_task.value,
                             exchange=Exchanges.jobs.value)

    return id_list, log
