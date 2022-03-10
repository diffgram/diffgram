# OPENCORE - ADD
from methods.regular.regular_api import logger
from methods.task.task_template.task_template_after_launch_strategies.task_template_after_launch_strategy import \
    TaskTemplateAfterLaunchStrategy
from shared.utils import job_dir_sync_utils
from methods.connectors.connectors import ConnectorManager
from methods.task.task_template.task_template_after_launch_strategies.standard_task_template_after_launch_strategy import \
    StandardTaskTemplateAfterLaunchStrategy
from shared.database.external.external import ExternalMap
from methods.regular.regular_api import *


class ScaleAITaskTemplateAfterLaunchStrategy(TaskTemplateAfterLaunchStrategy):

    def create_scale_ai_project(self, connector):
        result_project = connector.put_data({
            'action_type': 'create_project',
            'name': self.task_template.name,
            'type': 'annotation',
            'event_data': {},
        })

        return result_project['result']

    def create_scale_ai_project_mapping(self, scale_ai_project, connection):
        external_map = ExternalMap.new(
            session=self.session,
            job=self.task_template,
            external_id=scale_ai_project['name'],
            connection=connection,
            diffgram_class_string='task_template',
            type=connection.integration_name,
            url=f"https://dashboard.scale.com/test/tasks?project={scale_ai_project['name']}",
            add_to_session=True,
            flush_session=True
        )
        # Commented to bottom to avoid circular dependencies on job.
        self.task_template.default_external_map = external_map

        logger.debug(f"Created ScaleAI Project {scale_ai_project['name']}")

    def execute_after_launch_strategy(self):
        """
            This strategy will create a project on scale AI for user to send tasks into
            it when task is launched.
        :return:
        """
        scale_ai_project = None
        try:
            # TODO: ADD LABELBOX LOGIC HERE
            # We don't check perms here because we assume this was checked on the task template creation.
            # Otherwise, we would need request context here, which we don't have.
            connection = self.task_template.interface_connection
            logger.debug(f"Connection for ScaleAI: {connection}")
            connector_manager = ConnectorManager(connection=connection, session=self.session)
            connector = connector_manager.get_connector_instance()
            connector.connect()

            # We create a project
            scale_ai_project = self.create_scale_ai_project(connector)

            external_map = self.create_scale_ai_project_mapping(scale_ai_project, connection)

            logger.info(
                'ScaleAITaskTemplateAfterLaunchStrategy for Task Template ID: {} completed successfully.'.format(
                    self.task_template.id))
            logger.debug('Proceding to standard task template launch...')

            # Now create tasks as usual.
            standard_strategy = StandardTaskTemplateAfterLaunchStrategy(
                session=self.session,
                task_template=self.task_template,
                log=self.log
            )
            standard_strategy.execute_after_launch_strategy()

        except Exception as e:
            logger.exception(e)
            raise(e)
