from shared.database.project_migration.project_migration import ProjectMigration
from shared.helpers.sessionMaker import session_scope_threaded
from sqlalchemy.orm.session import Session
from shared.shared_logger import get_shared_logger
from shared.connection.connection_strategy import ConnectionStrategy
from shared.connection.labelbox_connector import LabelboxConnector
from shared.helpers import sessionMaker
import threading
import traceback
logger = get_shared_logger()
import json
from shared.regular import regular_methods

class ExternalMigrationManager:
    project_migration: ProjectMigration
    session: Session

    def __init__(self, session: Session, project_migration: ProjectMigration):

        self.session = session
        self.project_migration = project_migration

    def __set_migration_failure(self, error_key, error_message):
        if not self.project_migration.error_log:
            self.project_migration.error_log = {}
        migration = ProjectMigration.get_by_id(self.session, self.project_migration.id)
        if migration.error_log is None:
            migration.error_log = {}
        migration.error_log = {}
        migration.error_log[error_key] = error_message
        migration.status = 'failed'
        self.session.add(migration)
        logger.error(error_message)

    def start_external_migration(self):
        """
            Initializes a new external migration of data, based on the ProjectMigration object
            given to the instance of this class.
        :return:
        """

        if not self.project_migration:
            logger.error('Project Migration Data not Provided. Migration aborted.')

            return

        logger.info(f'Starting Migration to Project {self.project_migration.project.project_string_id}')

        connection = self.project_migration.connection

        if connection.integration_name == 'labelbox':
            self.__start_labelbox_project_migration()
        else:
            message = f'Integration with {connection.integration_name} not supported. Aborting.'
            self.__set_migration_failure('integration', message)
            return

    def __start_labelbox_project_migration(self):
        labelbox_project_id = self.project_migration.external_mapping_project.external_id
        logger.info(f'Starting project migration from labelbox external project: {labelbox_project_id}')
        connection_strategy = ConnectionStrategy(
            connection_class = LabelboxConnector,
            session = self.session)
        connector, success = connection_strategy.get_connector(
            connection_id = self.project_migration.connection_id,
            check_perms = False)
        if not success:
            message = f'Failed to get Connector for ID {self.project_migration.connection_id}'
            self.__set_migration_failure('connector_creation', message)
        connection_result = connector.connect()
        if 'log' in connection_result:
            message = f'Cannot initialize connection {connection_result}'
            self.__set_migration_failure('connection_initialization', message)
            return
        result = None
        try:
            self.project_migration.status = 'in_progress'
            regular_methods.commit_with_rollback(self.session)
            result = connector.fetch_data(
                {
                    'action_type': 'import_project',
                    'event_data': {},
                    'project_string_id': self.project_migration.project.project_string_id,
                    'labelbox_project_id': labelbox_project_id,
                    'member_id': self.project_migration.member_created_id,
                    'project_migration_id': self.project_migration.id,

                }
            )

        except Exception as e:
            message = 'Project failed to migrate'
            logger.error(message)
            trace_data = traceback.format_exc()
            self.__set_migration_failure('failed_migration', trace_data)
            return

        logger.info('Project Migration Succesful.')
        self.project_migration.status = 'success'
        self.project_migration.percent_complete = 100
        self.session.add(self.project_migration)
        return result


def start_project_migration(project_migration_id):
    with sessionMaker.session_scope() as session:
        project_migration = ProjectMigration.get_by_id(session = session, id = project_migration_id)
        manager = ExternalMigrationManager(session = session, project_migration = project_migration)
        manager.start_external_migration()


def initialize_migration_threaded(project_migration_id):
    t = threading.Thread(
        target = start_project_migration,
        args = ((project_migration_id,))
    )
    t.start()
