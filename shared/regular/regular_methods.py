# OPENCORE - ADD
import time
import random
from shared.settings import settings
import requests
import json
import datetime
import traceback
from shared.helpers.sessionMaker import AfterCommitAction

# TODO would like to have this as a mixin
def try_to_commit(self):
	try:
		self.session.commit()
	except:
		self.session.rollback()
		raise


def commit_with_rollback(session):
    try:
        session.commit()
    except:
        session.rollback()
        raise


def clean_up_temp_dir(path):
    import shutil
    try:
        shutil.rmtree(path)  # delete directory
        print("Cleaned successfully")
    except OSError as exc:
        print("shutil error")


def transmit_interservice_request_after_commit(
        session: object,
        message: str,
        logger: dict,
        service_target: str = 'walrus',
        id: int = None,
        base_class_string: str = None,
        project_string_id: str = None,
        extra_params: dict = {}

):
    AfterCommitAction(session = session,
                      callback = transmit_interservice_request,
                      callback_args = {
                          'message': message,
                          'logger': logger,
                          'service_target': service_target,
                          'base_class_string': base_class_string,
                          'id': id,
                          'project_string_id': project_string_id,
                          'extra_params': extra_params
                      })

def transmit_interservice_request(
        message: str,
        logger = None,
        service_target: str = 'walrus',
        id: int = None,
        base_class_string: str = None,
        project_string_id: str = None,
        extra_params: dict = {},
        ):
    """
    Example usage

    1)
    regular_methods.transmit_interservice_request(
        message = 'new_job_launch_queue_item',
        logger = logger,
        service_target = 'walrus')

    2)
    In service target 

    Add a thing 	eg right now just if statement

    if input['message'] == 'new_job_launch_queue_item':
        job_launcher_thread = TaskTemplateLauncherThread(run_once = True)
        log['info']['job_launcher_thread'] = True

    Check Walrus interservice_receive_api() for example implementation

    Other assumptions
        There is a valid settings security key that matches
        
    """
    if settings.DIFFGRAM_SYSTEM_MODE == 'testing':
        return

    data = {
        'inter_service_security_token': settings.INTER_SERVICE_SECRET,
        'message': message,
        'id': id,
        'base_class_string': base_class_string,
        'project_string_id': project_string_id,
        'extra_params': extra_params
        }
    if service_target == 'walrus':

        endpoint = settings.WALRUS_SERVICE_URL_BASE + 'api/walrus/v1/interservice/receive'
    else:
        raise NotImplementedError
    response = requests.post(endpoint, data=json.dumps(data))
    try:
        data = response.json()
        if logger: logger.info('[Interservice]' + str(data))
    except:
        if logger: logger.info('[Interservice]' + str(response))



def regular_query(
        query,
        date_from_string: str = None,
        date_to_string: str = None,
        base_class = None,
        created_time_string: str = 'time_created'
        ):
    """
    Example usage

    query = regular_methods.regular_query(
        query = query,
        date_from_string = date_from_string,
        date_to_string = date_to_string,
        base_class = Event
        )

    Plan to add more common things here like
        - limit
        - return type
        - maybe even project scoping
    """

    if date_from_string:
        date_from_datetime = datetime.datetime.strptime(date_from_string, "%Y-%m-%d")
        query = query.filter(
            getattr(base_class, created_time_string) >= date_from_datetime)

    if date_to_string:
        date_to_datetime = datetime.datetime.strptime(date_to_string, "%Y-%m-%d")
        query = query.filter(
            getattr(base_class, created_time_string) <= date_to_datetime)

    return query


def loop_forever_with_random_load_balancing(
		log_start_message="",
		log_heartbeat_message="",
		function_call=None,		# note we assume that self. is passed if needed
		function_args={},
		thread_sleep_time_min=1,
		thread_sleep_time_max=2,
		logger=None):
	"""
	-> Idea with it is that way we get coverage / load balance without having to know which of the workers last did it. 
	Basically it's a poor man's load balancing. eg 5 workers, each one gets it at a random time
	-> Want the sleep to first - because otherwise when the server starts up, it spams it times the number of workers.

	Example Usage:

	regular_methods.loop_forever_with_random_load_balancing(
		log_start_message='Starting SyncActionsHandlerThread Queue handler... ',
		log_heartbeat_message='[SyncActions Queue heartbeat]',
		function_call=self.check_for_new_sync_actions,
		function_args={},
		thread_sleep_time_min=self.thread_sleep_time_min,
		thread_sleep_time_max=self.thread_sleep_time_max,
		logger=logger
		)
	"""

	if logger: logger.info(log_start_message)
	while True:
		deferred_time = random.randint(thread_sleep_time_min, thread_sleep_time_max)
		time.sleep(deferred_time)
		if logger: logger.info(log_heartbeat_message + str(deferred_time))
		try:
			function_call(**function_args)
		except Exception as exception:
			if logger: logger.error(traceback.format_exc())
