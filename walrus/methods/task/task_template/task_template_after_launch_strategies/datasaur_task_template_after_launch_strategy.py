# OPENCORE - ADD
from methods.regular.regular_api import logger
from methods.task.task_template.task_template_after_launch_strategies.task_template_after_launch_strategy import \
    TaskTemplateAfterLaunchStrategy
from shared.utils import job_dir_sync_utils
from methods.connectors.connectors import ConnectorManager
from shared.database.external.external import ExternalMap
import uuid
from methods.task.task_template.task_template_after_launch_strategies.standard_task_template_after_launch_strategy import \
    StandardTaskTemplateAfterLaunchStrategy
import traceback


class DatasaurTaskTemplateAfterLaunchStrategy(TaskTemplateAfterLaunchStrategy):
    def create_datasaur_labelset(self, label_data, connector):
        result = connector.put_data({
            'action_type': 'create_label_set',
            'name': f"labelset-{self.task_template.name}-{self.task_template.id}",
            'event_data': {},
            'label_data': label_data
        })
        return result

    def create_datasaur_project(self, connector, label_set, files_to_process):

        result = connector.put_data({
            'action_type': 'create_project',
            'name': self.task_template.name,
            'event_data': {},
            'label_set_id': label_set['id'],
            'project_name': self.task_template.name,
            'files': files_to_process,
            'kind': 'TOKEN_BASED'
        })
        return result

    def get_project_files_list(self, connector, datasaur_project):
        project_files_results = connector.fetch_data({
            'action_type': 'get_project_files_list',
            'project_id': datasaur_project['id'],
            'event_data': {},

        })
        return project_files_results

    def execute_after_launch_strategy(self):
        """
            This strategy will attach files from sync directories and creates tasks in
            Diffgram for each of them.
        :return:
        """
        datasaur_project = None
        connection = self.task_template.interface_connection
        logger.debug(f"Connection for Datasaur: {connection}")
        connector_manager = ConnectorManager(connection=connection, session=self.session)
        connector = connector_manager.get_connector_instance()
        connector.connect()
        try:

            label_data = []
            for label_element in self.task_template.label_dict.get('label_file_list_serialized', []):
                element = {
                    'uuid': str(uuid.uuid4()),
                    'diffgram_label_file': label_element['id'],
                    'name': f"{label_element['label']['name']}",
                    'color': label_element['colour']['hex'].upper(),
                }
                label_data.append(element)

            # First we need to build a label set
            label_set_result = self.create_datasaur_labelset(label_data, connector)
            label_set = label_set_result['result']['createLabelSet']
            logger.debug(f"Created label_set {label_set}")
            if label_set.get('id'):
                logger.info('Datasaur Labelset created succesfully ID:'.format(label_set['id']))
                ExternalMap.new(
                    session=self.session,
                    job=self.task_template,
                    external_id=label_set['id'],
                    connection=connection,
                    diffgram_class_string='',
                    type=f"{connection.integration_name}_label_set",
                    url='',
                    add_to_session=True,
                    flush_session=True
                )
                # Now save mappings for created labels
                for label_element in label_data:
                    ExternalMap.new(
                        session=self.session,
                        job=self.task_template,
                        file_id=label_element['diffgram_label_file'],
                        external_id=label_element['uuid'],
                        connection=connection,
                        diffgram_class_string='label_file',
                        type=f"{connection.integration_name}_label",
                        url='',
                        add_to_session=True,
                        flush_session=True
                    )

            # Now we create a project
            files_to_process = self.task_template.get_attached_files(self.session, type='text')
            files_to_process_by_id = {}
            if len(files_to_process) == 0:
                raise Exception('Task template has no files in attached folder. Stopping Datasaur launch strategy.')

            for file in files_to_process:
                files_to_process_by_id[str(file.id)] = file
            print('files_to_process_by_id', files_to_process_by_id)
            result = self.create_datasaur_project(connector, label_set, files_to_process)
            logger.debug(f"Create datasaur Project result: {result}")
            if 'result' in result:
                datasaur_project = result['result']
                ExternalMap.new(
                    session=self.session,
                    job=self.task_template,
                    external_id=datasaur_project['id'],
                    connection=connection,
                    diffgram_class_string='task_template',
                    type=f"{connection.integration_name}_project",
                    url=f"https://datasaur.ai/projects/{datasaur_project['id']}/",
                    add_to_session=True,
                    flush_session=True,
                )
                logger.debug('Created Datasaur Project.')
                # Save file ID's mappings
                project_files_results = self.get_project_files_list(connector, datasaur_project)
                print('qweqwe', project_files_results)
                project_files = project_files_results['result']['documents']
                for file in project_files:
                    diffgram_file = files_to_process_by_id[file['name']]
                    ExternalMap.new(
                        session=self.session,
                        job=self.task_template,
                        external_id=file['id'],
                        file=diffgram_file,
                        connection=connection,
                        diffgram_class_string='file',
                        type=f"{connection.integration_name}_file",
                        url='',
                        add_to_session=True,
                        flush_session=True,
                    )
                # Now create tasks as usual.
                logger.info(
                    'DatasaurTaskTemplateAfterLaunchStrategy for Task Template ID: {} completed successfully.'.format(
                        self.task_template.id))
                logger.debug('Proceding to standard task template launch...')
                standard_strategy = StandardTaskTemplateAfterLaunchStrategy(
                    session=self.session,
                    task_template=self.task_template,
                    log=self.log
                )
                standard_strategy.execute_after_launch_strategy()

            else:
                logger.error('Error from connector: Rolling back project creation...')
                raise Exception(result)

        except Exception as e:
            logger.error(f"Error during datasaur launch strategy. {traceback.format_exc()}")
            if datasaur_project:
                logger.error('Rolling back project creation...')
                result = connector.put_data({
                    'action_type': 'delete_project',
                    'project_id': datasaur_project['id'],
                    'event_data': {},
                })
            raise e
