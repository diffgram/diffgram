# OPENCORE - ADD
import scaleapi
from methods.regular.regular_api import *
import requests
from shared.connection.connectors.connectors_base import Connector, with_connection
from shared.regular import regular_log
from shared.permissions.task_permissions import Permission_Task
from methods.connectors.connectors import ConnectorManager
from shared.database.task.job.job import Job
from shared.database.external.external import ExternalMap
from methods.input.packet import enqueue_packet


def with_scale_ai_exception_handler(f):
    def wrapper(*args):
        log = regular_log.default()
        try:
            res = f(*args)
            return res
        except Exception as e:
            log['error'][
                'auth_credentials'] = 'Error connecting to ScaleAI. Please check you private API key is correct.'
            log['error']['exception_details'] = str(e)
            return {'log': log}

    return wrapper


# Note: this should eventually inherit from base class, we just have to decide if we will leave base class offering
# just the connect()  test_data() fetch_data() and put_data() abstract methods
class ScaleAIConnector(Connector):

    def connect(self):
        """
            This should be the first method called to connect to the source.
            All implementations should return a ConnectionError exception in case
            connection is unsuccessful.
        :return:
        """

        client = scaleapi.ScaleClient(self.auth_data['client_secret'])
        self.connection_client = client
        return True

    @with_scale_ai_exception_handler
    @with_connection
    def __create_bounding_box_task(self, opts):
        callback_url = opts['callback_url']
        instruction = opts['instruction']
        attachment_type = opts['attachment_type']
        attachment = opts['attachment']
        objects_to_annotate = opts['objects_to_annotate']
        metadata = opts.get('metadata')
        project = opts['project']
        task_data = self.connection_client.create_annotation_task(
            callback_url=callback_url,
            project=project,
            instruction=instruction,
            attachment_type=attachment_type,
            attachment=attachment,
            objects_to_annotate=objects_to_annotate,
            metadata=metadata
        )
        return {'result': task_data}

    @with_scale_ai_exception_handler
    @with_connection
    def __create_point_annotation_task(self, opts):
        callback_url = opts['callback_url']
        instruction = opts['instruction']
        attachment_type = opts['attachment_type']
        attachment = opts['attachment']
        objects_to_annotate = opts['objects_to_annotate']
        with_labels = opts['with_labels']
        metadata = opts['metadata']
        task_data = self.connection_client.create_pointannotation_task(
            callback_url=callback_url,
            instruction=instruction,
            attachment_type=attachment_type,
            attachment=attachment,
            objects_to_annotate=objects_to_annotate,
            with_labels=with_labels,
            metadata=metadata
        )
        return task_data

    @with_scale_ai_exception_handler
    @with_connection
    def __create_line_task(self,
                           opts,
                           instruction,
                           attachment_type,
                           attachment,
                           objects_to_annotate,
                           with_labels,
                           metadata={}):
        callback_url = opts['callback_url']
        instruction = opts['instruction']
        attachment_type = opts['attachment_type']
        attachment = opts['attachment']
        objects_to_annotate = opts['objects_to_annotate']
        metadata = opts['metadata']
        task_data = self.connection_client.create_lineannotation_task(
            callback_url=callback_url,
            instruction=instruction,
            attachment_type=attachment_type,
            attachment=attachment,
            objects_to_annotate=objects_to_annotate,
            metadata=metadata
        )
        return task_data

    @with_scale_ai_exception_handler
    @with_connection
    def __create_polygon_task(self, opts):
        callback_url = opts['callback_url']
        attachment = opts['attachment']
        instruction = opts['instruction']
        attachment_type = opts['attachment_type']
        objects_to_annotate = opts['objects_to_annotate']
        metadata = opts.get('metadata')
        task_data = self.connection_client.create_polygonannotation_task(
            callback_url=callback_url,
            instruction=instruction,
            attachment_type=attachment_type,
            attachment=attachment,
            objects_to_annotate=objects_to_annotate,
            metadata=metadata
        )
        return {'result': task_data}

    @with_scale_ai_exception_handler
    @with_connection
    def __fetch_single_task(self, opts):
        """
            Fetches a single ScaleAI task.
            expects opts: {'task_id': str}
        :return: task_data: dict with scaleAI's task data.
        """
        task = self.connection_client.fetch_task(opts['task_id'])
        return task

    @with_scale_ai_exception_handler
    @with_connection
    def __cancel_task(self, opts):
        """
            Fetches a single ScaleAI task.
            expects opts: {'task_id': str}
        :return: task_data: dict with scaleAI's task data.
        """
        task = self.connection_client.cancel_task(opts['task_id'])
        return task

    @with_connection
    def __create_project(self, opts):
        import requests
        url = "https://api.scale.com/v1/projects"
        payload = {
            "type": opts['type'],
            "name": opts['name'],
            "params": {"instruction": "Please label According to the given objects."}
        }
        headers = {
            "content-type": "application/json",
        }
        response = requests.request("POST", url,
                                    json=payload,
                                    headers=headers,
                                    auth=(self.auth_data['client_secret'], ''))
        data = response.json()

        return {'result': data}

    @with_connection
    def put_data(self, opts):
        """
            This function puts an object from diffgram to the source
        :param diffgram_input: the diffgram input object
        :param path: the URI to the paths object
        :return:
        """
        if 'action_type' not in opts:
            raise Exception('Provide action_type key.')
        action_type = opts.pop('action_type')
        if action_type == 'bounding_box':
            return self.__create_bounding_box_task(opts)
        if action_type == 'point':
            return self.__create_point_annotation_task(opts)
        if action_type == 'line':
            return self.__create_line_task(opts)
        if action_type == 'polygon':
            return self.__create_polygon_task(opts)
        if action_type == 'video_box_annotation':
            return self.__create_video_bounding_box_task(opts)
        if action_type == 'create_project':
            return self.__create_project(opts)

    @with_scale_ai_exception_handler
    def test_connection(self):
        """
            This function checks if there is a successful connecction to the source
        :return: True/False
        """
        self.connect()
        tasks = self.connection_client.tasks()
        if 'error' in tasks:
            raise Exception('Connection Error, Check Scale API credentials')
        return {'result': True}

    @with_connection
    def fetch_data(self, opts):
        """
            This function should start in a new Thread. It does the necessary logic to bring all the contents
            of the given source path to Diffgram.
        :return: True/False
        """
        if 'action_type' not in opts:
            raise Exception('Provide action_type key.')

        if opts['action_type'] == 'fetch_task':
            return self.__fetch_single_task(**opts)

    @with_connection
    def get_meta_data(self):
        return {}


@dataclass
class ScaleAISyncManager:
    """
        This class will contain all operations for sending and receiving files from
        labelbox.
    """
    session: any
    task_template: Job
    log: dict
    scale_ai_connector: ScaleAIConnector = None

    def _with_task_template(f):
        @wraps(f)
        def wrapped(inst, *args, **kwargs):
            if not inst.task_template:
                return
            return f(inst, *args, **kwargs)

        return wrapped

    def get_label_objects(self):
        result = []
        for label_element in self.task_template.label_dict['label_file_list_serialized']:
            result.append(label_element['label']['name'])
        return list(set(result))

    def get_scale_ai_project(self):
        external_map = ExternalMap.get(
            session=self.session,
            job_id=self.task_template.id,
            connection_id=self.task_template.interface_connection_id,
            diffgram_class_string='task_template',
            type=self.task_template.interface_connection.integration_name,
        )
        if external_map:
            return external_map.external_id
        return None

    def map_scale_ai_task(self, task, scale_ai_task, type='box'):
        task_id = None
        if type == 'box':
            task_id = scale_ai_task.id
        elif type == 'polygon':
            task_id = scale_ai_task.task_id

        if task_id is None:
            raise Exception('Cannot map ScaleAI task. Id is None')
        external_map = ExternalMap.new(
            session=self.session,
            task=task,
            external_id=scale_ai_task.id,
            connection=task.job.interface_connection,
            diffgram_class_string='task',
            type=f"{task.job.interface_connection.integration_name}_task",
            url='',
            add_to_session=True,
            flush_session=True
        )
        # Commented to bottom to avoid circular dependencies on job.
        self.task_template.default_external_map = external_map

        logger.debug(f"Created ScaleAI Task {scale_ai_task.id}")
        return external_map

    def set_task_in_progress(self, task):
        task.status = 'in_progress'
        self.session.add(task)
        return task

    def transform_annotations_to_diffgram_instance_list(self, annotations):
        instance_list = []
        for annotation in annotations:
            diffgram_instance_format = {
                'label_file': {},
                'colour': {
                    "a": 1,
                    "hex": "#00FF80",
                    "hsl": {
                        "a": 1,
                        "h": 150,
                        "l": 0.5,
                        "s": 1
                    },
                    "hsv": {
                        "a": 1,
                        "h": 150,
                        "s": 1,
                        "v": 1
                    },
                    "oldHue": 150,
                    "rgba": {
                        "a": 1,
                        "b": 128,
                        "g": 255,
                        "r": 0
                    },
                    "source": "hsva"
                },
                'created_time': str(datetime.datetime.now()),
                'hash': '',
                'label': {},
                'state': 'added',
                'label_file_id': None,
                'instance_id': None,
                'type': 'box',
                'x_max': None,
                'x_min': None,
                'y_max': None,
                'y_min': None,
                'points': []
            }

            diffgram_label_file = self.task_template.get_label_file_by_name(annotation['label'])
            diffgram_instance_format['label_file_id'] = diffgram_label_file['id']
            diffgram_instance_format['type'] = self.task_template.instance_type
            if self.task_template.instance_type == 'box':
                diffgram_instance_format['colour'] = diffgram_label_file['colour']
                diffgram_instance_format['x_min'] = annotation['left']
                diffgram_instance_format['x_max'] = diffgram_instance_format['x_min'] + annotation['width']
                diffgram_instance_format['y_min'] = annotation['top']
                diffgram_instance_format['y_max'] = diffgram_instance_format['y_min'] + annotation['height']
            if self.task_template.instance_type == 'polygon':
                diffgram_instance_format['colour'] = diffgram_label_file['colour']
                for vertx in annotation['vertices']:
                    diffgram_instance_format['points'].append({
                        'x': vertx['x'],
                        'y': vertx['y']
                    })
            instance_list.append(diffgram_instance_format)
        return instance_list

    def enqueue_scale_ai_annotations(self, diffgram_task, annotations):
        diffgram_instance_list = self.transform_annotations_to_diffgram_instance_list(annotations)
        enqueue_packet(project_string_id=self.task_template.project.project_string_id,
                       session=self.session,
                       media_url=None,
                       media_type='image',
                       job_id=self.task_template.id,
                       file_id=diffgram_task.file.id,
                       instance_list=diffgram_instance_list,
                       task_id=diffgram_task.id,
                       task_action='complete_task',
                       commit_input=True,
                       mode="update")
        return

    def send_diffgram_task(self, task):
        if task is None:
            self.log['error'] = {'task': {'Provide task'}}
            return False, self.log
        if task.file.type not in ['image']:
            # TODO: add support for video.
            self.log['error'] = {'Scale AI File Type': 'Only images supported'}
            return False, self.log
        scale_ai_type = None
        callback_url = settings.SCALE_AI_WEBHOOKS_URL
        objects_to_annotate = self.get_label_objects()
        scale_ai_project = self.get_scale_ai_project()
        attachment_type = task.file.type
        logger.debug(f"Creating ScaleAI of for task_template type {self.task_template.instance_type}")
        if self.task_template.instance_type == 'box':
            scale_ai_type = 'bounding_box'
            if self.task_template.guide_default:
                instruction = self.task_template.guide_default.description_markdown
            else:
                instruction = "Please label the provided objects."
            result = self.scale_ai_connector.put_data({
                'action_type': scale_ai_type,
                'objects_to_annotate': objects_to_annotate,
                'callback_url': callback_url,
                'attachment_type': attachment_type,
                'attachment': task.file.get_signed_url(session=self.session),
                'instruction': instruction,
                'project': scale_ai_project
            })
            if 'log' in 'result':
                self.log['error'] = {
                    'scale_ai_type': result
                }
                return False, self.log
            if 'result' not in result:
                self.log['error'] = {
                    'scale_ai_type': result
                }
                return False, self.log
            self.map_scale_ai_task(task, result['result'], type='box')
            self.set_task_in_progress(task)
            return result['result'], self.log

        elif self.task_template.instance_type == 'polygon':
            scale_ai_type = 'polygon'
            if self.task_template.guide_default:
                instruction = self.task_template.guide_default.description_markdown
            else:
                instruction = "Please label the provided objects."
            result = self.scale_ai_connector.put_data({
                'action_type': scale_ai_type,
                'objects_to_annotate': objects_to_annotate,
                'callback_url': callback_url,
                'attachment_type': attachment_type,
                'attachment': task.file.get_signed_url(session=self.session),
                'instruction': instruction,
                'project': scale_ai_project
            })
            if 'log' in 'result':
                self.log['error'] = {
                    'scale_ai_type': result
                }
                return False, self.log
            if 'result' not in result:
                self.log['error'] = {
                    'scale_ai_type': result
                }
                return False, self.log
            print('RESLYT', result)
            self.map_scale_ai_task(task, result['result'], type='polygon')
            self.set_task_in_progress(task)
            return result['result'], self.log
        else:
            self.log['error'] = {
                'type': {'Invalid type for Scale AI task. Just polygon and bounding box are supported.'}}
            return False, self.log


@routes.route('/api/walrus/v1/connections/send-task-to-scale-ai', methods=['POST'])
@General_permissions.grant_permission_for(['normal_user'])
@Permission_Task.by_task_id(apis_user_list=["builder_or_trainer"])
def send_task_to_scale_ai():
    """
        Webhook for receiving data on Diffgram once finished on labelbox.
        # NOTE: Labelbox does not supportText or dropdown classifications in export for videos.
    :return:
    """
    # First check if secret is correct
    spec_list = [{'task_id': dict}, {'project_string_id': str}]

    log, input_data, untrusted_input = regular_input.master(request=request,
                                                            spec_list=spec_list)

    log = regular_log.default()
    with sessionMaker.session_scope() as session:
        task_id = input_data['task_id']
        task = Task.get_by_id(session, task_id=task_id)
        if task:
            task_template = task.job
            connection = task_template.interface_connection
            logger.debug(f"Connection for ScaleAI: {connection}")
            connector_manager = ConnectorManager(connection=connection, session=session)
            connector = connector_manager.get_connector_instance()
            connector.connect()

            scale_ai_sync_manager = ScaleAISyncManager(
                task_template=task_template,
                scale_ai_connector=connector,
                log=log,
                session=session

            )

            scale_ai_task, log = scale_ai_sync_manager.send_diffgram_task(task)
            logger.debug(f"Scale AI create result: {scale_ai_task} || {log}")
            if not scale_ai_task:
                return jsonify(log=log), 400

            return jsonify({'message': 'OK.', 'scale_ai_task_id': scale_ai_task.id})
        else:
            log['error']['task_id'] = 'Task not found.'
            return jsonify(log)


from methods.regular.regular_api import *


@routes.route('/api/walrus/v1/webhooks/scale-ai',
              methods=['POST'])
def task_completed_scaleai():
    spec_list = [{'status': str},
                 {'task': {
                     'task_id': str,
                     'completed_at': str,
                     'response': dict,
                     'created_at': str,
                     'callback_url': str,
                     'type': str,
                     'status': str,
                     'instruction': str,
                     'params': dict,
                     'metadata': dict,

                 }},
                 {'response': dict},
                 {'task_id': str},

                 ]

    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    annotations = input['response']['annotations']
    with sessionMaker.session_scope() as session:
        external_map_task = ExternalMap.get(
            session=session,
            external_id=input['task']['task_id'],
            type="scale_ai_task"
        )
        task = external_map_task.task
        task_template = task.job
        scale_ai_sync_manager = ScaleAISyncManager(
            session=session,
            task_template=task_template,
            log=log,
            scale_ai_connector=None
        )

        scale_ai_sync_manager.enqueue_scale_ai_annotations(task, annotations)

        return jsonify({})
