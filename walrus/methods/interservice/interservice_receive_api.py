from methods.regular.regular_api import *
from methods.task.task_template.task_template_launch_handler import TaskTemplateLauncherThread
from methods.sync_events.sync_actions_handler import SyncActionsHandlerThread
from methods.input.packet import enqueue_packet

@routes.route('/api/walrus/v1/interservice/receive',
              methods=['POST'])
def interservice_receive_api():
    """
    Inter-Service route to notify of new job launch

    For now relies on inter_service_security_token for permissions...

    This is just a starting point for more generic inter service notification
    Pros/Cons to having DB as intermediary point there, fo now
    this is fairly light weight.
    
    Once we have a good pattern here, eg retry/overflow handling,
    can probably remove polling / thread

    """
    spec_list = [{"inter_service_security_token": {
        'kind': str,
        'required': True,
        'security_token': settings.INTER_SERVICE_SECRET
    }
    },
        {"message": {
            'kind': str,
            'required': True
        }
        },
        {"id": {  # or "base_class_id"?
            'kind': int,
            'required': False,
            'default': None
        }
        },
        {"extra_params": {
            'kind': dict,
            'required': False,
            'default': None
        }
        },
        {"base_class_string": {
            'kind': str,
            'required': False,
            'default': None
        }
        },
        {"project_string_id": {
            'kind': str,
            'required': False,
            'default': None
        }
        }
        # Serialized object maybe?
    ]

    log, input_from_request, untrusted_input = regular_input.master(request = request, spec_list = spec_list)

    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    logger.info("Received valid inter service request")

    with sessionMaker.session_scope() as session:

        # CAUTIONS
        # Generally assumes any calls here are non blocking
        # So as to reasonably return   
        

        # eg 1) Condition on message then some_launcher(event_id = input['id'])

        # Or 2) if we want object here for some reason, something like:
        # if input['base_class_string']:
        #    base_object = getattr(sys.modules[__name__], input['base_class_string']).get_by_id(
        #        id = input['id'],
        #        session = session)

        if input_from_request['message'] == 'new_job_launch_queue_item':
            job_launcher_thread = TaskTemplateLauncherThread(run_once=True)
            log['info']['job_launcher_thread'] = True
        if input_from_request['message'] == 'new_sync_action_item':
            sync_action_thread = SyncActionsHandlerThread(run_once=True)
            log['info']['job_launcher_thread'] = True
        if input_from_request['message'] == 'video_copy':
            enqueue_packet(project_string_id = input_from_request.get('project_string_id'),
                           session = session,
                           media_url = None,
                           media_type = 'video',
                           directory_id = input_from_request['extra_params'].get('destination_working_dir_id'),
                           source_directory_id = input_from_request['extra_params'].get('source_working_dir_id'),
                           remove_link = input_from_request['extra_params'].get('remove_link'),
                           add_link = input_from_request['extra_params'].get('add_link'),
                           copy_instance_list = input_from_request['extra_params'].get('copy_instance_list'),
                           job_id = None,
                           batch_id = input_from_request['extra_params'].get('batch_id'),
                           file_id = input_from_request['id'],
                           instance_list = [],
                           video_parent_length = input_from_request['extra_params'].get('frame_count'),
                           task_id = None,
                           mode = 'copy_file',
                           commit_input=True)
        if input_from_request['message'] == 'image_copy':
            enqueue_packet(project_string_id = input_from_request.get('project_string_id'),
                           session = session,
                           media_url = None,
                           media_type = 'image',
                           directory_id = input_from_request['extra_params'].get('destination_working_dir_id'),
                           source_directory_id = input_from_request['extra_params'].get('source_working_dir_id'),
                           remove_link = input_from_request['extra_params'].get('remove_link'),
                           add_link = input_from_request['extra_params'].get('add_link'),
                           copy_instance_list = input_from_request['extra_params'].get('copy_instance_list'),
                           job_id = None,
                           batch_id = input_from_request['extra_params'].get('batch_id'),
                           file_id = input_from_request['id'],
                           instance_list = [],
                           video_parent_length = None,
                           task_id = None,
                           mode = 'copy_file',
                           commit_input=True)

        log['success'] = True
        return jsonify(log=log), 200
