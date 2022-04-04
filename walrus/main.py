# WALRUS service
import time

start_time = time.time()

from flask import Flask, request
from werkzeug.contrib.fixers import ProxyFix  # needed for get_remote_address to get right ip
import logging
from flask_sslify import SSLify
from datetime import timedelta

app = Flask('Diffgram',
            static_folder="./dist/static",
            template_folder="./dist")

app.app_context()
sslify = SSLify(app, subdomains=True)


# This is so all the ORM can map the shared modules
# Appears to be needed even if not directly using them
# Maybe a setting we can look into
# Unlikely to need all of these BUT not worth energy to figure out right now

import shared.database_setup_supporting
from methods.connectors import connector_interface
from methods.input.upload import api_project_upload_large

from methods.input.packet import input_packet
from methods.input.input_view import input_list_web
from methods.input.input_update import api_input_update
from methods.input.input_view_detail import input_view_detail_api

from methods.export.export_web import web_export_to_file
from methods.export.export_generation import new_external_export
from methods.export.export_view import export_list

from methods.video.interpolation import interpolate_all_frames
from methods.connectors.labelbox_connector import labelbox_web_hook_manager
from methods.connectors.scale_ai_connector import send_task_to_scale_ai, task_completed_scaleai

from methods.interservice.interservice_receive_api import interservice_receive_api
from methods.data_mocking.generate_data import generate_data_api
from methods.eventhub.eventhub_new import new_eventhub_web
from methods.project_migration.project_migration_new import api_new_project_migration
from methods.project_migration.project_migration_detail import api_project_migration_detail
from methods.project_migration.project_migration_list import api_project_migration_list
from methods import routes as routes_blueprint

with app.app_context():
    from shared.error_handlers.error_handlers import *

app.register_blueprint(routes_blueprint)


@app.route('/', methods=['GET'])
def walrus_alive():
    return """
	<img src="https://storage.googleapis.com/diffgram_public/walrus/alive.jpg" width="100%">
	"""

@app.route('/api/walrus/status', methods=['GET'])
def walrus_alive_api():
    return jsonify(True), 200

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=14)
app.config['MAX_CONTENT_LENGTH'] = 250 * 1024 * 1024    # 250 Mb limit

@app.after_request
def apply_security_rules(response):
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@app.before_request
def handle_chunking():
    """
    Sets the "wsgi.input_terminated" environment flag, thus enabling
    Werkzeug to pass chunked requests as streams.  The gunicorn server
    should set this, but it's not yet been implemented.
    """

    transfer_encoding = request.headers.get("Transfer-Encoding", None)
    if transfer_encoding == u"chunked":
        request.environ["wsgi.input_terminated"] = True

from shared.settings import settings

app.secret_key = settings.SECRET_KEY
from methods.task.task_template.task_template_launch_handler import TaskTemplateLauncherThread
from methods.sync_events.sync_actions_handler import SyncActionsHandlerThread
from shared.helpers.security import limiter
from methods.startup.system_startup_checker import WalrusServiceSystemStartupChecker
from methods.connectors.datasaur_connector import DatasaurSyncManager
from methods.input.process_media_queue_manager import ProcessMediaQueueManager
from methods.action.action_flow_trigger_queue import ActionFlowTriggerQueueThread

limiter.init_app(app)

settings.DIFFGRAM_SERVICE_NAME = 'walrus_service'
startup_checker = WalrusServiceSystemStartupChecker()
startup_checker.execute_startup_checks()

# This starts the queue loop for processing media uploads.
process_media_queue_manager = ProcessMediaQueueManager()
process_media_queue_manager.start_process_media_threads()

# This starts the thread for checking job launches queue.
job_launcher_thread = TaskTemplateLauncherThread(
    run_once=False,
    thread_sleep_time_min=settings.TASK_TEMPLATE_THREAD_SLEEP_TIME_MIN,
    thread_sleep_time_max=settings.TASK_TEMPLATE_THREAD_SLEEP_TIME_MAX)
sync_actions_thread = SyncActionsHandlerThread(thread_sleep_time_min=settings.SYNC_ACTIONS_THREAD_SLEEP_TIME_MIN,
                                               thread_sleep_time_max=settings.SYNC_ACTIONS_THREAD_SLEEP_TIME_MAX,
                                               run_once = False)
datasaur_sync_manager = DatasaurSyncManager(thread_sleep_time_min=settings.DATASAUR_SYNC_THREAD_SLEEP_TIME_MIN,
                                            thread_sleep_time_max=settings.DATASAUR_SYNC_THREAD_SLEEP_TIME_MAX)
datasaur_sync_manager.start_sync_loop()

actions_thread = ActionFlowTriggerQueueThread(thread_sleep_time_min=settings.ACTION_THREAD_SLEEP_TIME_MIN,
                                              thread_sleep_time_max=settings.ACTION_THREAD_SLEEP_TIME_MAX,
                                              run_once=False)


print("Startup in", time.time() - start_time)

# actions_thread = ActionFlowTriggerQueueThread(thread_sleep_time_min=5,
#                                               thread_sleep_time_max=6,
#                                               run_once=False)
# Debug
if __name__ == '__main__':

    settings.NAME_EQUALS_MAIN = True  # can adjust this for local deferral testing if needed?
    limiter.enabled = False
    # os.environ['test'] = "test_os_environ"

    app.run(host='0.0.0.0', port=8082, debug=True, use_reloader=True)
    # CAUTION . app.run() is BLOCKING
    # code below app.run will not execute!!!
else:
    print("settings.NAME_EQUALS_MAIN", settings.NAME_EQUALS_MAIN)

    app.debug == False
    app.wsgi_app = ProxyFix(app.wsgi_app, num_proxies=2)