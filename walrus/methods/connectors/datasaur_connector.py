# OPENCORE - ADD
from methods.regular.regular_api import *
from shared.connection.connectors.connectors_base import Connector, with_connection
from dataclasses import dataclass
from functools import wraps
from shared.database.external.external import ExternalMap
from shared.database.task.job.job_working_dir import JobWorkingDir
from shared.utils.task import task_complete
from methods.connectors.connectors import ConnectorManager
import uuid
from shared.database.task.job.job_working_dir import JobWorkingDir
from google.cloud import storage
import os
import shutil
from methods.input.packet import enqueue_packet
from shared.database.connection.connection import Connection
from shared.utils.task.task_complete import task_complete
import random
import threading
from sqlalchemy import and_
from sqlalchemy.orm import aliased
import requests

def with_datasaur_exception_handler(f):
    def wrapper(*args):
        log = regular_log.default()
        try:
            res = f(*args)
            return res
        except Exception as e:
            log['error'][
                'auth_credentials'] = 'Error connecting to Datasaur. Please check you private API key is correct.'
            log['error']['exception_details'] = str(e)
            return {'log': log}

    return wrapper


class DatasaurClient:
    access_token = None
    expires_in = None
    API_URL = 'https://datasaur.ai/graphql'
    BASE_URL = 'https://datasaur.ai'

    def __init__(self, client_id, client_secret):
        self.gcs = storage.Client()
        self.bucket = self.gcs.get_bucket(settings.CLOUD_STORAGE_BUCKET)
        self.client_id = client_id
        self.client_secret = client_secret
        self.__gen_new_token()

    def download_file_locally(self, diffgram_file, dir='/tmp'):
        random_name = str(uuid.uuid4())
        dir_path = '{}/{}'.format(dir, random_name)
        full_path = '{}/{}/{}'.format(dir, random_name, diffgram_file.text_file.original_filename)
        os.umask(0)
        os.makedirs(os.path.dirname(full_path), mode=0o777, exist_ok=True)
        blob = self.bucket.blob(diffgram_file.get_blob_path())
        with open(full_path, 'wb') as file_obj:

            try:
                self.gcs.download_blob_to_file(
                    blob_or_uri=blob,
                    file_obj=file_obj)
            except Exception as e:
                print(e)
                return
        return full_path, dir_path

    def __gen_new_token(self):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post('https://datasaur.ai/api/oauth/token', headers=headers, data=params)
        response_data = response.json()
        self.access_token = response_data['access_token']
        self.time_generated = datetime.datetime.now()
        self.expires_in = response_data['expires_in']
        return self.access_token

    def get_file_export(self, file_id):
        # TODO REMOVE AND IMPLEMENT A TOKEN REFRESH MECHANISM
        access_token = self.get_access_token()
        headers = {
            'Authorization': 'Bearer {}'.format(access_token),
            'Content-Type': 'application/json'
        }
        data = {
            'query': "query ExportTextProjectDocumentQuery($input: ExportTextProjectDocumentInput!) { result: exportTextProjectDocument(input: $input) {    redirect  fileUrl  queued    __typename  }}",
            'variables': {
                "input": {
                    "documentId": file_id,
                    "fileName": 'temp',
                    "format": "json_advanced",
                    "method": "FILE_STORAGE"
                }
            }
        }
        response = requests.post(self.API_URL, headers=headers, data=json.dumps(data))
        data = response.json()
        # Added to prevent race condition.
        # (Somehow their API sometimes does not have their file on S3 when the return response)
        time.sleep(0.9)
        url = data['data']['result']['fileUrl']
        r = requests.get(url.encode('utf-8'))
        json_data = r.json()
        return json_data

    def get_project_files_list(self, project_id):
        # TODO REMOVE AND IMPLEMENT A TOKEN REFRESH MECHANISM
        access_token = self.get_access_token()
        headers = {
            'Authorization': 'Bearer {}'.format(access_token),
            'Content-Type': 'application/json'
        }
        data = {
            'query': """
                query GetProjectCabinetQuery($input: GetProjectCabinetInput) {
                    cabinet: getProjectCabinet(input: $input) {
                      ...DocumentCabinetFragment
                      documents {
                        ...TextDocumentBasicFragment
                        __typename
                      }
                      __typename
                    }
                    }

                  fragment DocumentCabinetFragment on DocumentCabinet {
                    id
                    lastOpenedDocumentId
                    __typename
                    }

                  fragment TextDocumentBasicFragment on TextDocument {
                    id
                    fileName
                    name
                    originId
                    __typename
                    }
            """,
            'variables': {
                "input": {
                    "projectId": project_id,
                    "role": "LABELER"
                }
            }
        }
        response = requests.post(self.API_URL, headers=headers, data=json.dumps(data))
        data = response.json()
        return data

    def delete_project(self, project_id=None):
        access_token, expires = self.get_access_token()
        query = """
            mutation DeleteProjectMutation($input: DeleteProjectInput!) {
              project: deleteProject(input: $input) {
                id
                team {
                  id
                  __typename
                }
                __typename
              }
              }
        """
        data = {
            "operationName": "DeleteProjectMutation",
            "variables": json.dumps({"input": {"projectId": "{}".format(project_id)}}),
            "query": query,
        }
        headers = {
            'Authorization': 'Bearer {}'.format(access_token),
            # 'Content-Type': 'application/json'
        }
        response = requests.post(self.API_URL, headers=headers, data=data)
        data = response.json()
        return data

    def get_access_token(self):
        now = datetime.datetime.now()
        time_diff = (now - self.time_generated).total_seconds()
        # Check if token has expired
        if time_diff > (self.expires_in - 300):
            return self.__gen_new_token()
        else:
            return self.access_token

    def get_project(self, project_id):
        access_token = self.get_access_token()
        query = """
            query GetProjectQuery($input: GetProjectInput!) {
              project: getProject(input: $input) {
                ...ProjectFragment
                __typename
              }
              }

            fragment ProjectFragment on Project {
              id
              assignees {
                ...ProjectAssigneeFragment
                __typename
              }
              createdDate
              isOwnerMe
              isReviewByMeAllowed
              name
              settings {
                ...ProjectSettingsFragment
                __typename
              }
              status
              team {
                id
                name
                members {
                  ...TeamMemberFragment
                  __typename
                }
                __typename
              }
              type
              updatedDate
              __typename
              }

            fragment UserFragment on User {
              id
              username
              name
              email
              package
              profilePicture
              allowedActions
              displayName
              __typename
              }

            fragment ProjectAssigneeFragment on ProjectAssignment {
              teamMember {
                ...TeamMemberFragment
                __typename
              }
              documentIds
              __typename
              }

            fragment TeamMemberFragment on TeamMember {
              id
              user {
                ...UserFragment
                __typename
              }
              role {
                id
                name
                __typename
              }
              isDeleted
              invitationEmail
              invitationStatus
              joinedDate
              __typename
              }

            fragment ProjectSettingsFragment on ProjectSettings {
              consensus
              enableEditLabelSet
              enableEditSentence
              __typename
              }
        """
        data = {
            "variables": json.dumps({"input": {"projectId": str(project_id)}}),
            "query": query,
        }
        headers = {
            'Authorization': 'Bearer {}'.format(access_token),
            # 'Content-Type': 'application/json'
        }
        response = requests.post(self.API_URL, headers=headers, data=data)
        data = response.json()
        return data

    def get_projects_list(self, status_list=("COMPLETE", "CREATED", "IN_PROGRESS")):
        access_token = self.get_access_token()
        headers = {
            'Authorization': 'Bearer {}'.format(access_token),
            'Content-Type': 'application/json'
        }
        data = {
            'query': """
                    query GetProjectRecentsQuery($input: GetProjectsPaginatedInput!) {
                      result: getProjects(input: $input) {
                        totalCount
                        nodes {
                          ...ProjectRecentFragment
                          __typename
                        }
                        pageInfo {
                          nextCursor
                          prevCursor
                          __typename
                        }
                        __typename
                      }
                      }

                    fragment ProjectRecentFragment on Project {
                      id
                      assignees {
                        teamMember {
                          id
                          user {
                            ...UserFragment
                            __typename
                          }
                          __typename
                        }
                        __typename
                      }
                      createdDate
                      isOwnerMe
                      name
                      status
                      type
                      updatedDate
                      __typename
                      }

                    fragment UserFragment on User {
                      id
                      username
                      name
                      email
                      package
                      profilePicture
                      allowedActions
                      displayName
                      __typename
                      }

            """,
            "variables": json.dumps(
                {
                    "input": {
                        "filter": {
                            "statuses": status_list
                        },
                        "page": {
                            "take": 10000,
                            "skip": 0
                        }
                    }
                }
            ),
        }
        response = requests.post(self.API_URL, headers=headers, data=json.dumps(data))
        data = response.json()
        return data

    def create_label_set(self, name, labels_data):
        """
            Create a label set in datasaur
        :param labels_data: array containing {"name": "", "color": ""} values
        :return:
        """
        tag_items = []
        for label in labels_data:
            tag_items.append({
                "id": label['uuid'],
                "parentId": None,
                "desc": label['name'],
                "color": label['color'],
                "tagName": label['name']
            })

        query = """
            mutation CreateLabelSetMutation($input: CreateLabelSetInput!) {
              createLabelSet(input: $input) {
                ...LabelSetFragment
                __typename
              }
            }

            fragment LabelSetFragment on LabelSet {
              id
              name
              tagItems {
                ...TagItemFragment
                __typename
              }
              lastUsedBy {
                name
                __typename
              }
              __typename
              }

            fragment TagItemFragment on TagItem {
              id
              parentId
              color
              desc
              tagName
              __typename
            }
        """
        vars_json = json.dumps(
            {
                "input": {
                    "name": name,
                    "tagItems": tag_items,
                }
            }
        )
        data = {
            "operationName": "CreateLabelSetMutation",
            "variables": vars_json,
            "query": query,
        }
        headers = {
            'Authorization': 'Bearer {}'.format(self.get_access_token()),
            # 'Content-Type': 'application/json'
        }
        response = requests.post(self.API_URL, headers=headers, data=data)
        data = response.json()
        return data['data']

    def create_project(self,
                       project_name=None,
                       all_tokens_must_be_labeled=False,
                       allow_arc_drawing=True,
                       auto_scroll=True,
                       allow_multi_labels=True,
                       text_label_max_token_length=999999,
                       allow_character_based_labeling=False,
                       kind="TOKEN_BASED",
                       consensus=1,
                       enable_edit_label_set=True,
                       enable_edit_sentence=True,
                       assignee_emails=[],
                       label_set_id=None,
                       download_files=True,
                       diffgram_files=[]):

        # TODO REMOVE AND IMPLEMENT A TOKEN REFRESH MECHANISM
        access_token = self.get_access_token()
        download_dir = '/tmp'
        assignees_data = []
        for email in assignee_emails:
            assignees_data.append({
                "email": email,
                "documentNames": [file.name for file in diffgram_files]
            })
        documents_data = []
        dirs = []
        for file in diffgram_files:
            if download_files:
                file_name, dir = self.download_file_locally(dir=download_dir,
                                                            diffgram_file=file)
                dirs.append(dir)
            else:
                file_name = file.text_file.original_filename
            documents_data.append({
                'name': str(file.id),
                'file': None,
                'fileName': file_name
            })

        query = """
        mutation LaunchTextProjectMutation($input: LaunchTextProjectInput!) {
                      launchTextProject(input: $input) {
                        id
                        rootDocumentId
                        settings {
                          consensus
                          enableEditLabelSet
                          enableEditSentence
                          __typename
                        }
                        __typename
                      }
                    } 
        """
        vars_json = {
            "input": {
                "projectCreationId": str(uuid.uuid4()),
                # "rootDocumentId": str(uuid.uuid4()),
                'type': 'NER',
                "name": project_name,
                "documentSettings": {
                    'allTokensMustBeLabeled': all_tokens_must_be_labeled,
                    'allowArcDrawing': allow_arc_drawing,
                    'autoScrollWhenLabeling': auto_scroll,
                    'allowMultiLabels': allow_multi_labels,
                    'textLabelMaxTokenLength': text_label_max_token_length,
                    'allowCharacterBasedLabeling': allow_character_based_labeling,
                    'kind': kind,
                },

                "projectSettings": {
                    "consensus": consensus,
                    "enableEditLabelSet": enable_edit_label_set,
                    "enableEditSentence": enable_edit_sentence
                },
                "assignees": [
                    {
                        "email": "",
                    }

                ],
                "documents": documents_data,
                "labelSetId": label_set_id
            }
        }

        data = {
            "operations": json.dumps(
                {
                    "operationName": "LaunchTextProjectMutation",
                    "variables": vars_json,
                    "query": query,
                }
            )
        }
        map = {}
        raw_files = [open(elm['fileName'], 'rb') for elm in documents_data]
        files_data = {}
        i = 1
        for file in raw_files:
            map[str(i)] = ["variables.input.documents.{}.file".format(i - 1)]
            files_data[str(i)] = file
            i += 1
        data['map'] = json.dumps(map)
        headers = {
            'Authorization': 'Bearer {}'.format(access_token),
        }
        response = requests.post(self.API_URL,
                                 headers=headers,
                                 data=data,
                                 files=files_data,
                                 params={'operation': 'LaunchTextProjectMutation'})

        data = response.json()
        for file in raw_files:
            file.close()
        for dir in dirs:
            shutil.rmtree(dir)  # delete file
        return data


class DatasaurConnector(Connector):

    @with_datasaur_exception_handler
    def connect(self):
        log = regular_log.default()
        client_id = self.auth_data['client_id']
        client_secret = self.auth_data['client_secret']
        self.connection_client = DatasaurClient(client_id, client_secret)
        return {'result': True}

    @with_datasaur_exception_handler
    @with_connection
    def __get_access_token(self, opts):
        token = self.connection_client.get_access_token()
        return {'result': token}

    @with_datasaur_exception_handler
    @with_connection
    def __get_projects_list(self, opts):
        status_list = opts.get('status_list', [])
        projects_list = self.connection_client.get_projects_list(status_list)
        return {'result': projects_list['data']['result']}

    @with_datasaur_exception_handler
    @with_connection
    def __get_project(self, opts):
        project_id = opts['project_id']
        project_data = self.connection_client.get_project(project_id)
        if 'errors' in project_data:
            return {'log': {'error': project_data['errors']}}
        return {'result': project_data['data']['project']}

    @with_connection
    def __sync_data_from_task_template(self, opts):
        task_template_id = opts['task_template_id']
        with sessionMaker.session_scope() as session:
            task_template = Job.get_by_id(session, job_id=task_template_id)
            sync_manager = DatasaurSyncManager(session=session)
            sync_manager.sync_projects_for_task_template(task_template)
            return {'result': True}

    @with_datasaur_exception_handler
    @with_connection
    def __get_projects_files_list(self, opts):
        project_id = opts['project_id']
        projects_list = self.connection_client.get_project_files_list(project_id)
        return {'result': projects_list['data']['cabinet']}

    @with_datasaur_exception_handler
    @with_connection
    def __get_file_export(self, opts):
        file_id = opts['file_id']
        file_export = self.connection_client.get_file_export(file_id)
        return {'result': file_export}

    @with_connection
    def __create_project(self, opts):
        files = opts['files']
        project_name = opts['project_name']
        label_set_id = opts['label_set_id']
        kind = opts['kind']
        project_result = self.connection_client.create_project(project_name=project_name,
                                                               all_tokens_must_be_labeled=False,
                                                               allow_arc_drawing=True,
                                                               auto_scroll=True,
                                                               allow_multi_labels=True,
                                                               text_label_max_token_length=999999,
                                                               allow_character_based_labeling=False,
                                                               kind=kind,
                                                               consensus=1,
                                                               enable_edit_label_set=True,
                                                               assignee_emails=[],
                                                               label_set_id=label_set_id,
                                                               diffgram_files=files)
        return {'result': project_result['data']['launchTextProject']}

    @with_datasaur_exception_handler
    @with_connection
    def __delete_project(self, opts):
        project_id = opts['project_id']
        project_result = self.connection_client.delete_project(project_id=project_id)
        return {'result': project_result}

    @with_datasaur_exception_handler
    @with_connection
    def __create_label_set(self, opts):
        label_data = opts['label_data']
        name = opts['name']
        label_set_data = self.connection_client.create_label_set(name, label_data)
        return {'result': label_set_data}

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
        if action_type == 'get_access_token':
            return self.__get_access_token(opts)
        if action_type == 'get_projects_list':
            return self.__get_projects_list(opts)
        if action_type == 'get_project':
            return self.__get_project(opts)
        if action_type == 'sync_data_from_task_template':
            return self.__sync_data_from_task_template(opts)
        if action_type == 'get_project_files_list':
            return self.__get_projects_files_list(opts)
        if action_type == 'get_file_export':
            return self.__get_file_export(opts)

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
        if action_type == 'create_label_set':
            return self.__create_label_set(opts)
        if action_type == 'delete_project':
            return self.__delete_project(opts)

    @with_connection
    def get_meta_data(self):
        raise NotImplementedError

    def test_connection(self):
        auth_result = self.connect()
        if 'log' in auth_result:
            return auth_result
        # Test fecthing projects
        token = self.__get_access_token({})
        logger.info('Datasaur connection success.')
        return token


@dataclass
class DatasaurSyncManager:
    thread_sleep_time_min: int = settings.DATASAUR_SYNC_THREAD_SLEEP_TIME_MIN
    thread_sleep_time_max: int = settings.DATASAUR_SYNC_THREAD_SLEEP_TIME_MAX
    session: any = None
    """
        This class will contain all operations for sending and receiving files from
        datasaur.
    """

    def trigger_export_single_datasaur_file(
            self,
            datasaur_connector,
            file_id: int):

        file_export_data = datasaur_connector.fetch_data({
            'action_type': 'get_file_export',
            'event_data': {},
            'file_id': file_id
        })
        return file_export_data


    def fetch_instances_from_file(
            self,
            task_template,
            diffgram_file,
            file_id,
            datasaur_connector):

        file_export_data = self.trigger_export_single_datasaur_file(
            datasaur_connector = datasaur_connector,
            file_id = file_id)

        instance_list = []
        # We get the task based on file id since assumption for datasaur is file and task will be the same concept.
        task = self.session.query(Task).filter(
            Task.job_id == task_template.id,
            Task.file_id == diffgram_file.id
        ).first()
        if 'log' in file_export_data and 'error' in file_export_data['log']:
            logger.error('Error fetching export data {}'.format(file_export_data))
        label_items = file_export_data['result']['labelSet']['labelItems']
        label_items_by_id = {}
        for label in label_items:
            external_map_label = ExternalMap.get(
                session=self.session,
                job_id=task_template.id,
                external_id=label['id'],
                connection_id=task_template.interface_connection.id,
                diffgram_class_string='label_file',
                type='datasaur_label'
            )
            if external_map_label:
                label_items_by_id[label['id']] = label
                label_items_by_id[label['id']]['label_file_id'] = external_map_label.file_id
            else:
                logger.error('No label_file found for datasaur ID: {}'.format(label['id']))
                return

        sentences = file_export_data['result']['sentences']
        for sentence in sentences:
            instances = sentence['labels']
            for instance in instances:
                instance_map = ExternalMap.get(
                    session = self.session,
                    external_id = instance['id'],
                    diffgram_class_string = 'instance',
                    type = 'datasaur_instance',
                    return_kind = 'first')
                if not instance_map:
                    logger.debug('Creating Instance Map...')
                    instance_map = ExternalMap.new(
                        session=self.session,
                        job=task_template,
                        external_id=instance['id'],
                        connection=task_template.interface_connection,
                        diffgram_class_string='instance',
                        type='{}_instance'.format(
                            task_template.interface_connection.integration_name),
                        url='',
                        add_to_session=True,
                        flush_session=True)
                else:
                    logger.debug('Instance Map exists, proceding to update.')
                instance_list.append({
                    'start_sentence': instance['sidS'],
                    'end_sentence': instance['sidE'],
                    'start_token': instance['s'],
                    'end_token': instance['e'],
                    'start_char': instance['charS'],
                    'end_char': instance['charE'],
                    'sentence': sentence['id'],
                    'type': 'text_token',
                    'name': label_items_by_id[instance['l']]['labelName'],
                    'label_file_id': label_items_by_id[instance['l']]['label_file_id']
                })
        logger.debug('Enqueuing new instances....')
        # Create new packet to ensure to commit this
        if task and task_template and diffgram_file:
            enqueue_packet(project_string_id=task_template.project.project_string_id,
                           session=self.session,
                           media_url=None,
                           media_type='text',
                           job_id=task_template.id,
                           file_id=diffgram_file.id,
                           instance_list=instance_list,
                           task_id=task.id,
                           task_action='complete_task',
                           commit_input=True,
                           mode="update")
            logger.info('Updated Task {} from datasaur.'.format(task.id))

    def sync_projects_for_task_template(self, task_template):
        connection = task_template.interface_connection
        connector_manager = ConnectorManager(connection=connection, session=self.session)
        datasaur_connector = connector_manager.get_connector_instance()
        datasaur_connector.connect()
        project_map = ExternalMap.get(
            session = self.session,
            job_id = task_template.id,
            diffgram_class_string = 'task_template',
            type = 'datasaur_project',
            return_kind = 'first')
        if not project_map:
            logger.error('Could not find external map for task template {}'.format(task_template.id))
            return

        # Fetch all completed projects
        project_data = datasaur_connector.fetch_data({
            'action_type': 'get_project',
            'event_data': {},
            'project_id': project_map.external_id
        })
        # For each project, generate a export for all files.
        if 'log' in project_data:
            if 'error' in project_data['log']:
                logger.error('Error fetching datasaur project {}'.format(project_data['log']['error']))
                logger.error('Datasaur project ID {} not found. Maybe was deleted?'.format(project_map.external_id))
                return
        datasaur_project = project_data['result']
        logger.debug('Fetched project: {}'.format(datasaur_project))
        if project_map:
            task_template = project_map.job
            if datasaur_project['status'] != 'COMPLETE':
                logger.debug('Datasaur project {} is not completed. Skipping...'.format(datasaur_project['id']))
                return
            # Now get All files from the project
            files_map = ExternalMap.get(
                return_kind = 'all',
                session = self.session,
                job_id = task_template.id,
                diffgram_class_string = 'file',
                type = 'datasaur_file')
            for file_map in files_map:
                diffgram_file = file_map.file
                datasaur_file_id = file_map.external_id
                logger.debug('Syncing File from Datasaur {}'.format(diffgram_file.id))
                self.fetch_instances_from_file(task_template, diffgram_file, datasaur_file_id, datasaur_connector)
        else:
            logger.error('Could not find external map for task_template {}'.format(task_template.id))

    def perform_complete_projects_sync(self):
        """
            The function will perform the following:
                - Get all task template with a datasaur connection that have pending tasks to complete.
                - For each task template. It will fetch the completed projects from datasaur
                - From those projects it will generate an export for all the files
                - For each file it will create/update the instances that exists in the export on Diffgram.

            NOTE: THIS APPROACH HAS SCALABILITY ISSUES.
                - We shall push datasaur to create webhooks for when a instance is added or a project completed
                    in order to avoid duplicate work.
        :return:
        """
        self.log = regular_log.default()
        with sessionMaker.session_scope_threaded() as session:
            self.session = session
            # Get Task templates to Sync.
            # This are task template that still have uncompleted tasks and have a datasaur connection
            Job2 = aliased(Job)
            task_template_to_process = session.query(
                Job).join(Job2, and_(Job.id == Job2.id,
                                     Job.stat_count_complete < Job2.stat_count_tasks)) \
                .join(Connection).filter(
                Job.status != 'archived',
                Connection.integration_name == 'datasaur').all()
            task_template_to_process = list(task_template_to_process)
            # We do nothing if there are no more task templates to process
            if len(task_template_to_process) == 0:
                return
            for task_template in task_template_to_process:
                self.sync_projects_for_task_template(task_template)

    def start_sync_loop(self):
        """
            Starts an infinite loop for checking any new incoming files from any
            task template. Or pending files to send in the queue.
        :return:
        """
        # 5 workers going so might as well wait longer
        self.thread = threading.Thread(target=self.sync_check_loop)
        if settings.DIFFGRAM_SYSTEM_MODE != 'testing':
            self.thread.daemon = True  # Allow hot reload to work
            self.thread.start()

    def sync_check_loop(self):

        regular_methods.loop_forever_with_random_load_balancing(
            log_start_message='Starting DatasaurSyncManager Queue handler...',
            log_heartbeat_message='[DatasaurSyncManager heartbeat]',
            function_call=self.perform_complete_projects_sync,
            function_args={},
            thread_sleep_time_min=self.thread_sleep_time_min,
            thread_sleep_time_max=self.thread_sleep_time_max,
            logger=logger
            )