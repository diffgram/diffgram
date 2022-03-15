# OPENCORE - ADD
from methods.regular.regular_api import *
from shared.connection.connectors.connectors_base import Connector, with_connection
from shared.regular import regular_log
from dataclasses import dataclass
import labelbox
import requests
from functools import wraps
from shared.annotation import Annotation_Update
import hmac
import hashlib
from shared.database.external.external import ExternalMap
from shared.database.task.job.job import Job
from shared.database.task.job.job_working_dir import JobWorkingDir
from shared.utils.task import task_complete
from methods.connectors.connectors import ConnectorManager
from methods.input.packet import enqueue_packet
from shared.regular.regular_log import result_has_error
from shared.regular import regular_log
from shared.database.auth.member import Member
from shared.database.attribute.attribute_template_group import Attribute_Template_Group
from shared.database.attribute.attribute_template import Attribute_Template
import colorsys


def with_labelbox_exception_handler(f):
    def wrapper(*args):
        log = regular_log.default()
        try:
            res = f(*args)
            return res
        except Exception as e:
            log['error'][
                'connection_error'] = 'Error connecting to Labelbox. Please check you private API key is correct.'
            log['error']['exception_details'] = str(e)
            return {'log': log}

    return wrapper


class LabelboxConnector(Connector):

    @with_labelbox_exception_handler
    def connect(self):
        log = regular_log.default()
        self.connection_client = labelbox.Client(self.auth_data['client_secret'])
        return {'result': True}

    @with_labelbox_exception_handler
    @with_connection
    def __get_projects(self, opts):
        results = []
        limit = 10
        if opts.get('limit'):
            limit = opts.get('limit')
        projects = self.connection_client.get_projects()
        for p in projects:
            if len(results) < limit:
                results.append({'id': p.uid, 'name': p.name})
            else:
                break
        return {'result': results}

    @with_labelbox_exception_handler
    @with_connection
    def __get_dataset(self, opts):
        try:
            dataset_id = opts['dataset_id']
            dataset = self.connection_client.get_dataset(dataset_id)
            return {'result': dataset, 'exists': True}
        except labelbox.exceptions.ResourceNotFoundError:
            return {'result': None,
                    'exists': False}

    @with_labelbox_exception_handler
    @with_connection
    def __get_project(self, opts):
        project = self.connection_client.get_project(opts['project_id'])
        return {'result': project}

    @with_labelbox_exception_handler
    @with_connection
    def __get_frames(self, opts):
        frames_url = opts['frames_url']
        headers = {'Authorization': f"Bearer {self.auth_data['client_secret']}"}
        ndjson_response = requests.get(frames_url, headers = headers)
        frames_data = ndjson_response.text.split('\n')
        result = [json.loads(elm) for elm in frames_data if elm != '']
        return {'result': result}

    @with_labelbox_exception_handler
    @with_connection
    def __get_data_rows(self, opts):
        dataset = opts['dataset']
        data_row_ids = opts.get('data_row_ids', [])
        data = {}
        data['dataRowIds'] = data_row_ids
        data['datasetId'] = dataset.uid
        query = """
                query($datasetId: ID!, $dataRowIds: [ID!]) {
                  datasets(where:{id: $datasetId }){
                    name
                    id
                    dataRows(where:{id_in: $dataRowIds}){
                      id,
                      externalId
                    }
                  }
                }
        """
        res = self.connection_client.execute(query, data)
        return {'result': res}

    def __map_instance_type(self, labelbox_type):

        instance_types_mapping = {
            'rectangle': 'box',
            'point': 'point',
            'polygon': 'polygon',
            'superpixel': 'polygon',
        }
        return instance_types_mapping[labelbox_type]

    def __map_attribute_type(self, labelbox_type):

        attr_types_mapping = {
            'radio': 'radio',
            'checklist': 'multiple_select',
            'dropdown': 'select',
            'text': 'text',
        }
        return attr_types_mapping[labelbox_type]

    def __set_multiple_select_attribute_data(self, session, clsf, existing_attribute_group, member):
        """
            Creates a diffgram attribute from the give labelbox classification object.
        :param clsf:
        :return:
        """

        logger.info(f'Creating Multi Select Type Attribute data: {existing_attribute_group.name}')

        for option in clsf.options:
            existing_attr = Attribute_Template.get_by_name(
                session = session,
                attr_template_group = existing_attribute_group,
                name = option.value
            )
            if existing_attr is None:
                existing_attr = Attribute_Template.new(
                    existing_attribute_group.project,
                    member,
                    existing_attribute_group,
                    name = option.value

                )
                session.add(existing_attr)
                logger.log(f'Created Multi Select Type Attribute Option: {option.value}')
            else:
                logger.info(f'Multi Select option {option.value} already exists.')

    def __set_select_attribute_data(self, session, clsf, existing_attribute_group, member):
        """
            Creates a diffgram attribute from the give labelbox classification object.
        :param clsf:
        :return:
        """

        logger.info(f'Creating Select Type Attribute data: {existing_attribute_group.name}')

        for option in clsf.options:
            existing_attr = Attribute_Template.get_by_name(
                session = session,
                attr_template_group = existing_attribute_group,
                name = option.value
            )
            if existing_attr is None:
                existing_attr = Attribute_Template.new(
                    existing_attribute_group.project,
                    member,
                    existing_attribute_group,
                    name = option.value

                )
                session.add(existing_attr)
                logger.log(f'Created Select Type Attribute Option: {option.value}')
            else:
                logger.info(f'Select option {option.value} already exists.')

    def __set_radio_attribute_data(self, session, clsf, existing_attribute_group, member):
        """
            Creates a diffgram attribute from the give labelbox classification object.
        :param clsf:
        :return:
        """

        logger.info(f'Creating Radio Type Attribute data: {existing_attribute_group.name}')

        for option in clsf.options:
            existing_attr = Attribute_Template.get_by_name(
                session = session,
                attr_template_group = existing_attribute_group,
                name = option.value
            )
            if existing_attr is None:

                existing_attr = Attribute_Template.new(
                    existing_attribute_group.project,
                    member,
                    existing_attribute_group,
                    name = option.value

                )
                session.add(existing_attr)
                logger.log(f'Created Radio Attribute Option: {option.value}')
            else:
                logger.info(f'Radio option {option.value} already exists.')

    def __add_attributes_to_label_file(self, session, label_file, diffgram_project, member, tool):
        """
            Creates all the classifications from the given labelbox tool as attributes in diffgram.
            If the attribute name and type already exists, it will update the options of the attribute.
        :param session:
        :param label_file:
        :param diffgram_project:
        :param member:
        :param tool:
        :return:
        """
        classifications = tool.classifications
        logger.log(f'Creating Attributes from Labelbox tool "{tool.name}"')
        for clsf in classifications:
            class_type = clsf.class_type.value
            attr_name = clsf.name
            diffgram_attribute_type = self.__map_attribute_type(class_type)
            # Search for attribute to see if it exists
            existing_attribute = Attribute_Template_Group.get_by_name_and_type(
                session = session,
                project_id = diffgram_project.id,
                name = attr_name,
                kind = diffgram_attribute_type
            )
            if existing_attribute is None:
                # Create the attribute
                logger.info(f'Creating attribute "{attr_name}"')
                existing_attribute = Attribute_Template_Group.new(
                    session = session,
                    project = diffgram_project,
                    member = member
                )
            existing_attribute.is_new = False
            existing_attribute.name = clsf.name
            existing_attribute.prompt = clsf.name
            existing_attribute.is_global = False

            if existing_attribute.kind == 'radio':
                self.__set_radio_attribute_data(
                    session = session,
                    clsf = clsf,
                    existing_attribute_group = existing_attribute,
                    member = member
                )
            elif existing_attribute.kind == 'select':
                self.__set_select_attribute_data(
                    session = session,
                    clsf = clsf,
                    existing_attribute_group = existing_attribute,
                    member = member
                )
            elif existing_attribute == 'multiple_select':
                self.__set_multiple_select_attribute_data(
                    session = session,
                    clsf = clsf,
                    existing_attribute_group = existing_attribute,
                    member = member
                )
            elif existing_attribute.kind == 'text':
                continue

    def __import_labels_to_project(self, session, ontology, diffgram_project, member):

        label_tools = ontology.tools()
        logger.info(f'Importing labels from ontology "{ontology.name}"')
        for tool in label_tools:
            labelbox_instance_type = tool.tool.value
            diffgram_instance_type = self.__map_instance_type(labelbox_instance_type)
            name = tool.name
            color_hex = tool.color
            rgb = tuple(int(color_hex[i:i + 2], 16) for i in (0, 2, 4))
            hls = colorsys.rgb_to_hsv(rgb[0], rgb[1], rgb[2])
            hsv = colorsys.rgb_to_hls(rgb[0], rgb[1], rgb[2])
            color_dict = {"hex": "#194d33",
                          "hls": {"l": hls[1], "h": hls[0], "s": hls[2], "a": 1},
                          "rgba": {"a": 1, "g": rgb[2], "r": rgb[0], "b": rgb[2]},
                          "hsv": {"a": 1, "h": hsv[0], "s": hsv[1], "v": hsv[2]}, "a": 1}

            label_file = File.get_by_label_name(
                session = session,
                label_name = name,
                project_id = diffgram_project.id
            )
            if label_file is None:

                label_file = File.new_label_file(
                    session = session,
                    name = name,
                    default_sequences_to_single_frame = False,
                    working_dir_id = diffgram_project.directory_default_id,
                    project = diffgram_project,
                    colour = color_dict,
                    log = regular_log.default()
                )
                logger.info(f'Created Label: "{name}"')
            else:
                logger.info(f'Label File "{name}" already exists.')

            if tool.classifications and len(tool.classifications) > 0:
                self.__add_attributes_to_label_file(label_file = label_file,
                                                    session = session,
                                                    diffgram_project = diffgram_project,
                                                    member = member,
                                                    tool = tool)

    def __import_ontology_to_project(self, opts):
        label_box_project_id = opts['labelbox_project_id']
        diffgram_project_string_id = opts['project_string_id']
        member_id = opts['member_id']
        logger.info(f'Starting ontolgy import for project {diffgram_project_string_id}')
        logger.info(f'Labelbox project  {label_box_project_id}')
        with sessionMaker.session_scope_threaded() as session:
            member = Member.get_by_id(session, member_id = member_id)
            diffgram_project = Project.get_by_string_id(session = session,
                                                        project_string_id = diffgram_project_string_id)
            labelbox_project = self.connection_client.get_project(project_id = label_box_project_id)
            ontology = labelbox_project.ontology()
            self.__import_labels_to_project(session, ontology, diffgram_project, member)

    @with_labelbox_exception_handler
    @with_connection
    def __attach_dataset(self, opts):
        project = opts['project']
        dataset = opts['dataset']
        query = """
            mutation AttachDataset($projectId: ID!, $datasetId: ID!){ 
                updateProject( 
                    where:{ 
                        id: $projectId 
                    }, 
                    data:{ 
                        setupComplete: "2018-11-29T20:46:59.521Z", 
                        datasets:{ 
                            connect:{ 
                                id: $datasetId
                            } 
                        } 
                    } 
                ){ 
                    id 
                } 
            }
        """
        data = {'projectId': project.uid, 'datasetId': dataset.uid}
        result = self.connection_client.execute(query, data)
        # TODO: implement attach
        return {'result': result}

    @with_labelbox_exception_handler
    @with_connection
    def __get_default_frontend(self, opts):
        frontends = list(self.connection_client.get_labeling_frontends())
        for frontend in frontends:
            if frontend.name == 'Editor':
                return {'result': frontend}

    @with_labelbox_exception_handler
    @with_connection
    def __create_project(self, opts):
        results = []
        project = self.connection_client.create_project(name = opts['name'])
        return {'result': project}

    @with_labelbox_exception_handler
    @with_connection
    def __create_dataset(self, opts):
        dataset = self.connection_client.create_dataset(name = opts['name'], projects = opts['project'])
        return {'result': dataset}

    @with_labelbox_exception_handler
    @with_connection
    def __setup_ontology(self, opts):
        project = opts['project']
        frontend = opts['frontend']
        ontology = opts['ontology']
        project.labeling_frontend.connect(frontend)
        ontology_setup = project.setup(frontend, ontology)
        return {'result': ontology}

    @with_labelbox_exception_handler
    @with_connection
    def __execute(self, opts):
        query = opts['query']
        data = opts['data']
        result = self.connection_client.execute(query, data)
        return {'result': result}

    @with_connection
    def fetch_data(self, opts):
        """
            This function routes any action_type to the correct S3 connector actions.
        :return: Object
        """
        if 'action_type' not in opts:
            raise Exception('Provide action_type key.')
        if 'event_data' not in opts:
            raise Exception('Provide event_data key.')

        action_type = opts.pop('action_type')
        if action_type == 'get_default_frontend':
            return self.__get_default_frontend(opts)
        if action_type == 'get_dataset':
            return self.__get_dataset(opts)
        if action_type == 'get_data_rows':
            return self.__get_data_rows(opts)
        if action_type == 'get_project':
            return self.__get_project(opts)
        if action_type == 'get_project_list':
            return self.__get_projects(opts)
        if action_type == 'get_frames':
            return self.__get_frames(opts)

    @with_connection
    def put_data(self, opts):
        """
            This function routes any action_type to the correct S3 connector actions.
        :return: Object
        """
        action_type = opts.pop('action_type')
        if 'event_data' not in opts:
            raise Exception('Provide event_data key.')
        if action_type == 'create_project':
            return self.__create_project(opts)
        if action_type == 'create_dataset':
            return self.__create_dataset(opts)
        if action_type == 'setup_ontology':
            return self.__setup_ontology(opts)
        if action_type == 'execute':
            return self.__execute(opts)
        if action_type == 'attach_dataset':
            return self.__attach_dataset(opts)
        raise NotImplementedError

    @with_connection
    def get_meta_data(self):
        raise NotImplementedError

    def test_connection(self):
        auth_result = self.connect()
        if 'log' in auth_result:
            return auth_result
        # Test fecthing projects
        projects = self.__get_projects({})
        logger.info('Labelbox connection success.')
        return projects


@dataclass
class LabelBoxSyncManager:
    """
        This class will contain all operations for sending and receiving files from
        labelbox.
    """
    session: any
    task_template: Job
    labelbox_project: any
    log: dict
    labelbox_connector: LabelboxConnector

    def _with_task_template(f):
        @wraps(f)
        def wrapped(inst, *args, **kwargs):
            if not inst.task_template:
                return
            return f(inst, *args, **kwargs)

        return wrapped

    def _with_labelbox_project(f):
        @wraps(f)
        def wrapped(inst, *args, **kwargs):
            if not inst.labelbox_project:
                return
            return f(inst, *args, **kwargs)

        return wrapped

    def start_sync_loop(self):
        """
            Starts an infinite loop for checking any new incoming files from any
            task template. Or pending files to send in the queue.
        :return:
        """
        # TODO implement
        # Update. Since webhooks are available this is not needed any more.
        raise NotImplementedError

    @_with_task_template
    def update_instance_list_for_image_or_frame(self,
                                                label_instances,
                                                diffgram_task,
                                                video_data = None,
                                                frame_packet_map = None):
        instance_list = []
        count = 1
        for labelbox_instance in label_instances:
            # Check if instance mapping already exists, if so provide instance_id to avoid overriding data.
            instance_map = ExternalMap.get(
                session = self.session,
                external_id = labelbox_instance['featureId'],
                diffgram_class_string = 'instance',
                type = 'labelbox_instance',
                connection_id = self.task_template.interface_connection.id
            )
            if not instance_map:
                instance_map = ExternalMap.new(
                    session = self.session,
                    external_id = None,
                    diffgram_class_string = 'instance',
                    type = 'labelbox_instance',
                    connection = self.task_template.interface_connection,
                    add_to_session = True,
                    flush_session = True
                )
            diffgram_label_file_data = self.task_template.get_label_file_by_name(labelbox_instance['title'])
            diffgram_label_instance = self.transform_labelbox_label_to_diffgram_instance(labelbox_instance,
                                                                                         diffgram_label_file_data,
                                                                                         instance_map = instance_map,
                                                                                         sequence_num = count if video_data is not None else None)

            if frame_packet_map is not None:
                if video_data['current_frame'] not in frame_packet_map:
                    frame_packet_map[video_data['current_frame']] = [diffgram_label_instance]
                else:
                    frame_packet_map[video_data['current_frame']].append(diffgram_label_instance)

            if diffgram_label_instance:
                instance_list.append(diffgram_label_instance)
            count += 1
        if instance_list and video_data is None:
            enqueue_packet(project_string_id = self.task_template.project.project_string_id,
                           session = self.session,
                           media_url = None,
                           media_type = 'image',
                           job_id = self.task_template.id,
                           file_id = diffgram_task.file.id,
                           instance_list = instance_list,
                           task_id = diffgram_task.id,
                           task_action = 'complete_task',
                           commit_input = True,
                           external_map_id = instance_map.id,
                           external_map_action = 'set_instance_id',
                           mode = "update_with_existing")
            return True
        elif instance_list:
            return True
        else:
            return False

    @_with_task_template
    def update_instance_list_for_video(self, frames_data, diffgram_task):
        frame_packet_map = {}
        for frame in frames_data:
            logger.debug(f"Processing Frame {frame['frameNumber']}")
            video_data = {
                'current_frame': frame['frameNumber'],
                'video_mode': True,
                'video_file_id': diffgram_task.file.id
            }
            label_instances = frame['objects']
            if len(label_instances) > 0:
                result = self.update_instance_list_for_image_or_frame(label_instances,
                                                                      diffgram_task,
                                                                      video_data = video_data,
                                                                      frame_packet_map = frame_packet_map)
        enqueue_packet(project_string_id = self.task_template.project.project_string_id,
                       session = self.session,
                       media_url = None,
                       media_type = 'video',
                       job_id = self.task_template.id,
                       file_id = diffgram_task.file.id,
                       frame_packet_map = frame_packet_map,
                       task_id = diffgram_task.id,
                       task_action = 'complete_task',
                       commit_input = True,
                       mode = "update_with_existing")
        return result

    @_with_task_template
    def handle_task_creation_hook(self, payload):
        labelbox_data_row_id = payload['dataRow']['id']
        label = json.loads(payload['label'])
        labelbox_label_id = payload['id']
        video_mode = False
        frames_data = None
        if 'frames' in label:
            # Fetch video objects
            frames_result = self.labelbox_connector.fetch_data({
                'action_type': 'get_frames',
                'frames_url': label['frames'],
                'event_data': {},
            })
            if result_has_error(frames_result):
                return jsonify(frames_result), 400
            frames_data = frames_result['result']
            video_mode = True
        else:
            label_instances = label['objects']
        file_external_mapping = ExternalMap.get(
            session = self.session,
            external_id = labelbox_data_row_id,
            diffgram_class_string = 'file',
            type = 'labelbox'
        )
        if file_external_mapping:
            diffgram_task = self.session.query(Task).filter(Task.job_id == self.task_template.id,
                                                            Task.file_id == file_external_mapping.file_id).first()

            if diffgram_task:
                # Build external mapping
                diffgram_task.default_external_map = ExternalMap.new(
                    session = self.session,
                    external_id = payload['id'],
                    task = diffgram_task,
                    diffgram_class_string = "task",
                    type = "labelbox",
                    add_to_session = True,
                    flush_session = True
                )
                self.session.add(diffgram_task)
                # Now process Labels and add them to file.
                if video_mode:
                    result = self.update_instance_list_for_video(frames_data, diffgram_task)
                    if not result:
                        logger.error('Error updating instances')
                        return jsonify('Error updating instances'), 400
                    logger.info('Updated instances succesfully enqueued.')
                else:
                    result = self.update_instance_list_for_image_or_frame(label_instances, diffgram_task)
                    if not result or not result:
                        logger.error('Error updating instances')
                        return jsonify('Error updating instances'), 400

                    else:
                        logger.info('Updated instances succesfully enqueued.')
            else:
                logger.error('Diffgram task not found')
                raise Exception('Diffgram task not found')
        else:
            logger.error('file_external_mapping not found')
            raise Exception('file_external_mapping not found')

    def deduct_instance_type_from_geometry(self, geometry):
        x_vals = [elm['x'] for elm in geometry]
        y_vals = [elm['y'] for elm in geometry]
        if len(geometry) > 4:
            return 'polygon'
        if len(set(x_vals)) == 2 and len(set(y_vals)):
            return 'bbox'
        return 'polygon'

    def get_bounding_box_from_geometry(self, geometry):
        x_vals = [elm['x'] for elm in geometry]
        y_vals = [elm['y'] for elm in geometry]
        x_min = min(x_vals)
        x_max = max(x_vals)
        y_min = min(y_vals)
        y_max = max(y_vals)
        return int(x_min), int(x_max), int(y_min), int(y_max)

    def transform_labelbox_label_to_diffgram_instance(self, label_object, diffgram_label_file_data,
                                                      sequence_num = None, instance_map = None):
        logger.debug(f"Bulding instance from: {label_object}")
        logger.debug(f"Bulding instance with diffgram label_file ID: {diffgram_label_file_data['id']}")
        instance_id = None
        if instance_map.instance_id:
            instance_id = instance_map.instance_id
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
        logger.debug(f"Sequence num is: {sequence_num}")
        if sequence_num is not None:
            diffgram_instance_format['number'] = sequence_num
        diffgram_instance_format['label_file_id'] = diffgram_label_file_data['id']

        # instance_type = self.deduct_instance_type_from_geometry(geometry)
        if 'polygon' in label_object:
            diffgram_instance_format['points'] = [
                {'x': int(elm['x']), 'y': int(elm['y'])}
                for elm in label_object['polygon']
            ]
            diffgram_instance_format['type'] = 'polygon'

        elif 'bbox' in label_object:
            top = label_object['bbox']['top']
            left = label_object['bbox']['left']
            height = label_object['bbox']['height']
            width = label_object['bbox']['width']
            diffgram_instance_format['x_min'] = int(left)
            diffgram_instance_format['x_max'] = int(left + width)
            diffgram_instance_format['y_min'] = int(top)
            diffgram_instance_format['y_max'] = int(top + height)
            diffgram_instance_format['colour']['hex'] = label_object['color']

        if 'classifications' in label_object:
            diffgram_instance_format['attribute_groups'] = {}
            for classification in label_object['classifications']:
                attr_group = self.task_template.get_attribute_group_by_name(diffgram_label_file_data,
                                                                            classification['value'])
                if attr_group['kind'] in ['multiple_select']:
                    diffgram_instance_format['attribute_groups'][attr_group['id']] = []
                    for answer in classification['answers']:
                        attr_template = self.task_template.get_attribute_template_by_name(attr_group, answer['title'])
                        diffgram_instance_format['attribute_groups'][attr_group['id']].append(
                            {
                                'display_name': classification['title'],
                                'value': classification['value'],
                                'id': attr_template['id'],
                                'name': attr_template['id']
                            }
                        )
                elif attr_group['kind'] in ['select']:
                    # NOTE: Labelbox does not supportText or dropdown classifications in export for video
                    attr_template = self.task_template.get_attribute_template_by_name(attr_group,
                                                                                      classification['answer'][0][
                                                                                          'title'])
                    diffgram_instance_format['attribute_groups'][attr_group['id']] = {
                        'display_name': classification['answer'][0]['title'],
                        'value': classification['answer'][0]['value'],
                        'id': attr_template['id'],
                        'name': attr_template['id']
                    }
                elif attr_group['kind'] in ['text']:
                    # NOTE: Labelbox does not supportText or dropdown classifications in export for video
                    diffgram_instance_format['attribute_groups'][attr_group['id']] = classification['answer']
                elif attr_group['kind'] in ['radio']:
                    attr_template = self.task_template.get_attribute_template_by_name(attr_group,
                                                                                      classification['answer']['title'])
                    diffgram_instance_format['attribute_groups'][attr_group['id']] = {
                        'display_name': classification['answer']['title'],
                        'value': classification['answer']['value'],
                        'id': attr_template['id'],
                        'name': attr_template['id']
                    }
        return diffgram_instance_format

    @_with_task_template
    def add_file_to_labelbox_dataset(self, diffgram_file, labelbox_dataset):
        data_row = None
        if diffgram_file.type == "image":
            if diffgram_file.image:
                data = self.image.serialize_for_source_control(self.session)
                data_row = labelbox_dataset.create_data_row(
                    row_data = data['url_signed'])
        if diffgram_file.type == "video":
            if diffgram_file.video:
                data = self.video.serialize_list_view(self.session, self.task_template.project)

            data_row = labelbox_dataset.create_data_row(
                row_data = data['file_signed_url'])
        return data_row

    def transform_labelbox_label_to_diffgram_instances(self):
        return

    @_with_task_template
    @_with_labelbox_project
    def set_webhook_for_task_template(self):
        """
            Creates a webhook on labelbox so Diffgram gets notified about new updates of the labels
            and we can act on it by updating our tasks data.
        :return:
        """
        query = """
            mutation CreateWebhook($projectId: ID!, $url: String!, $secret: String!) {
              createWebhook(data:{
                project:{
                  id: $projectId
                },
                url:$url,
                secret: $secret,
                topics:{set:[LABEL_CREATED, LABEL_UPDATED, LABEL_DELETED]}
                # topics:{set:[REVIEW_CREATED, REVIEW_UPDATED]}
              }){
                id
              }
            }
        """
        data = {
            'projectId': self.labelbox_project.uid,
            'url': settings.LABEL_BOX_WEBHOOKS_URL,
            'secret': settings.LABEL_BOX_SECRET
        }
        result = self.labelbox_connector.put_data({'action_type': 'execute',
                                                   'query': query,
                                                   'data': data,
                                                   'event_data': {}})
        logger.debug(f"Webhook for {self.labelbox_project.uid} succesfully created on Labelbox.")
        return result

    @_with_task_template
    def add_files_to_labelbox_dataset(self, diffgram_files = [], labelbox_dataset = None, force_create = False):
        """
            Adds the files to labelbox.
            Important! If you call this method multiple times, multiple versions of the same file will
            be created at labelbox, so use only on initialization of task templates.
        :param diffgram_files:
        :param labelbox_dataset:
        :param force_create: Ignore existing files and always create (useful for recreating a dataset that was deleted)
        :return:
        """
        if labelbox_dataset is None:
            return False
        file_urls = []
        diffgram_files_by_id = {}
        external_ids = []
        file_ids = [x.id for x in diffgram_files]

        datarow_external_maps = ExternalMap.get(
            session = self.session,
            file_id = file_ids,
            diffgram_class_string = 'file',
            type = 'labelbox',
            return_kind = 'all'
        )
        # To avoid querying external map each time on for loop.
        external_map_by_id = {ext_map.file_id: ext_map for ext_map in datarow_external_maps}
        data_row_ids = [external_map.external_id for external_map in datarow_external_maps if
                        external_map.external_id]
        result_datarows = self.labelbox_connector.fetch_data({
            'action_type': 'get_data_rows',
            'event_data': '',
            'dataset': labelbox_dataset,
            'data_row_ids': data_row_ids
        })
        labelbox_existing_data_rows = result_datarows['result']['datasets'][0]['dataRows']
        existing_data_rows_ids = [x['id'] for x in labelbox_existing_data_rows]
        deleted_data_rows = [row_id for row_id in data_row_ids if row_id not in existing_data_rows_ids]
        for diffgram_file in diffgram_files:
            # If we have a registered ID on labelbox, we skip file creation for this file.
            # We have to re-create it if it was deleted for some reason.
            diffgram_file_external_map = external_map_by_id.get(diffgram_file.id)
            if diffgram_file_external_map and diffgram_file_external_map.external_id and not force_create \
                and external_map_by_id.get(diffgram_file.id).external_id not in deleted_data_rows:
                logger.debug(f"File {diffgram_file.id} exists. Skipping..")
                continue
            if diffgram_file.type == "image":
                logger.debug(f"Adding image {diffgram_file.id}  in Labelbox")
                if diffgram_file.image:
                    data = diffgram_file.image.serialize_for_source_control(self.session)
                    data_row = {
                        labelbox.schema.data_row.DataRow.row_data: data['url_signed'],
                        'external_id': diffgram_file.id
                    }
                    # Cache in memory the file for updating labelbox ID's later
                    diffgram_files_by_id[diffgram_file.id] = diffgram_file
                    external_ids.append(str(diffgram_file.id))
                    file_urls.append(data_row)
            if diffgram_file.type == "video":
                if diffgram_file.video:
                    logger.debug(f"Adding video {diffgram_file.id}  in Labelbox")
                    data = diffgram_file.video.serialize_list_view(self.session, self.task_template.project)
                    data_row = {
                        labelbox.schema.data_row.DataRow.row_data: data['file_signed_url'],
                        'external_id': diffgram_file.id
                    }
                    # Cache in memory the file for updating labelbox ID's later
                    external_ids.append(str(diffgram_file.id))
                    diffgram_files_by_id[diffgram_file.id] = diffgram_file
                    file_urls.append(data_row)
        task = labelbox_dataset.create_data_rows(file_urls)
        # We want to wait since we're already deferring the creation process.
        task.wait_till_done()
        # Now update al Diffgram files with their labelbox data_row ID.
        query = """query($datasetId: ID!, $externalId: [String!]) {
                    datasets(where:{id: $datasetId }){
                      name
                      id
                      dataRows(where:{externalId_in: $externalId}){
                        id,
                        externalId
                      }
                    }
                }
        """
        data = {
            'datasetId': labelbox_dataset.uid,
            'externalId': external_ids
        }
        result = self.labelbox_connector.put_data({
            'action_type': 'execute',
            'event_data': [],
            'query': query,
            'data': data
        })

        created_datarows = result['result']['datasets'][0]['dataRows']

        for datarow in created_datarows:
            file = diffgram_files_by_id[int(datarow['externalId'])]
            file.default_external_map = ExternalMap.new(
                session = self.session,
                external_id = datarow['id'],
                file = file,
                diffgram_class_string = "file",
                type = "labelbox",
                add_to_session = True,
                flush_session = True
            )
            self.session.add(file)

        return task

    @_with_task_template
    @_with_labelbox_project
    def send_all_files_in_task_template(self):
        """
            Used for initial sync. Will go on all attached directories
            of the task template and create a dataset if doesn't exist
            and then send each file on the dataset to labelbox's dataset.
        :return:
        """
        datasets = self.task_template.get_attached_dirs(self.session)
        if not datasets:
            return

        for dataset in datasets:
            # Assumption here is that the labeling interface has already been checked so we assume we need to
            # create the dataset if it does not exits.
            logger.debug(f"Syncing dataset {dataset.nickname}-{dataset.id}  in Labelbox")
            if dataset.default_external_map:
                # Fetch dataset
                logger.debug('Dataset already exists... attaching.')
                dataset_id = dataset.default_external_map.external_id
                result = self.labelbox_connector.fetch_data(
                    {'action_type': 'get_dataset',
                     'event_data': {},
                     'dataset_id': dataset_id})
                force_create = False
                if result['exists']:
                    labelbox_dataset = result['result']
                    # Attach dataset to project
                    result_attach = self.labelbox_connector.put_data({
                        'action_type': 'attach_dataset',
                        'dataset': labelbox_dataset,
                        'project': self.labelbox_project,
                        'event_data': {}
                    })
                else:
                    logger.debug('Dataset not found, re-creating it...')
                    # If dataset was not found it may have been deleted. So we'll create it again.
                    force_create = True
                    # Create dataset
                    result = self.labelbox_connector.put_data({'action_type': 'create_dataset',
                                                               'name': dataset.nickname,
                                                               'event_data': {},
                                                               'project': self.labelbox_project})
                    labelbox_dataset = result['result']
                    # Now attach it
                    result_attach = self.labelbox_connector.put_data({
                        'action_type': 'attach_dataset',
                        'dataset': labelbox_dataset,
                        'project': self.labelbox_project,
                        'event_data': {}
                    })

                    dataset.default_external_map = ExternalMap.new(
                        session = self.session,
                        external_id = labelbox_dataset.uid,
                        dataset = dataset,
                        diffgram_class_string = "dataset",
                        type = "labelbox",
                        add_to_session = True,
                        flush_session = True
                    )
                    self.session.add(dataset)

                file_list = WorkingDirFileLink.file_list(self.session,
                                                         dataset.id,
                                                         limit = None)
                self.add_files_to_labelbox_dataset(diffgram_files = file_list,
                                                   labelbox_dataset = labelbox_dataset,
                                                   force_create = force_create)
            else:

                logger.debug('Dataset does not exist... creating.')
                # Create dataset
                result = self.labelbox_connector.put_data({'action_type': 'create_dataset',
                                                           'name': dataset.nickname,
                                                           'event_data': {},
                                                           'project': self.labelbox_project})
                labelbox_dataset = result['result']
                dataset.default_external_map = ExternalMap.new(
                    session = self.session,
                    external_id = labelbox_dataset.uid,
                    dataset = dataset,
                    url = f"https://app.labelbox.com/dataset/{labelbox_dataset.uid}",
                    diffgram_class_string = "dataset",
                    type = "labelbox",
                    add_to_session = True,
                    flush_session = True,
                )
                self.session.add(dataset)
                file_list = WorkingDirFileLink.file_list(self.session,
                                                         dataset.id,
                                                         limit = None)

                self.add_files_to_labelbox_dataset(diffgram_files = file_list, labelbox_dataset = labelbox_dataset)


@routes.route('/api/walrus/v1/webhooks/labelbox-webhook', methods = ['POST'])
def labelbox_web_hook_manager():
    """
        Webhook for receiving data on Diffgram once finished on labelbox.
        # NOTE: Labelbox does not supportText or dropdown classifications in export for videos.
    :return:
    """
    # First check if secret is correct
    payload = request.data
    secret = settings.LABEL_BOX_SECRET
    log = regular_log.default()
    computed_signature = hmac.new(bytearray(secret.encode('utf-8')), msg = payload,
                                  digestmod = hashlib.sha1).hexdigest()
    if request.headers['X-Hub-Signature'] != f"sha1={computed_signature}":
        error = 'Error: computed_signature does not match signature provided in the headers'
        logger.error('Error: computed_signature does not match signature provided in the headers')
        return error
    with sessionMaker.session_scope() as session:
        labelbox_event = request.headers['X-Labelbox-Event']
        payload = request.json
        logger.debug(f"Payload for labelbox webhooks: {payload}")
        labelbox_project_id = payload['project']['id']
        project_external_mapping = ExternalMap.get(
            session = session,
            external_id = labelbox_project_id,
            type = 'labelbox',
            diffgram_class_string = 'task_template'
        )
        if project_external_mapping:
            task_template = Job.get_by_id(session, project_external_mapping.job_id)
            if task_template:
                connection = task_template.interface_connection
                logger.debug(f"Connection for labelbox: {connection}")
                connector_manager = ConnectorManager(connection = connection, session = session)
                connector = connector_manager.get_connector_instance()
                connector.connect()
                sync_manager = LabelBoxSyncManager(
                    session = session,
                    task_template = task_template,
                    labelbox_project = None,
                    log = log,
                    labelbox_connector = connector
                )
                sync_manager.handle_task_creation_hook(payload)
                return jsonify({'message': 'OK.'})
            else:
                log['error']['task_template'] = 'Task template not found.'
                return jsonify(log)
        else:
            log['error']['labelbox_project'] = 'Labelbox external mapping not found.'
            return jsonify(log)
