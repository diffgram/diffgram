# OPENCORE - ADD
from methods.regular.regular_api import *
from methods.task.task_template.task_template_after_launch_strategies.task_template_after_launch_strategy import \
    TaskTemplateAfterLaunchStrategy
from methods.connectors.connectors import ConnectorManager
from methods.connectors.labelbox_connector import LabelBoxSyncManager
from methods.task.task_template.task_template_after_launch_strategies.standard_task_template_after_launch_strategy import \
    StandardTaskTemplateAfterLaunchStrategy
from shared.database.external.external import ExternalMap
from shared.regular.regular_log import result_has_error

class LabelboxTaskTemplateAfterLaunchStrategy(TaskTemplateAfterLaunchStrategy):
    LABELBOX_DIFFGRAM_TOOLS_MAPPING = {
        'box': 'rectangle',
        'polygon': 'polygon'
    }
    # Label attribute --> classification mapping
    LABELBOX_DIFFGRAM_CLASSIFICATIONS_MAPPING = {
        'multiple_select': 'checklist',
        'radio': 'radio',
        'text': 'text',
        'select': 'dropdown'
    }

    def __create_tools_from_task_templates(self):
        result = []
        for label_element in self.task_template.label_dict['label_file_list_serialized']:

            element = {
                'name': '{}'.format(label_element['label']['name']),
                'color': label_element['colour']['hex'].upper(),
                'tool': self.LABELBOX_DIFFGRAM_TOOLS_MAPPING[self.task_template.instance_type],
                'required': False,

            }
            """
                Attribute format for labelbox classifications(24/8/2020).:
                'classifications': [{'required': True,
                                     'instructions': 'radio classiff',
                                     'name': 'radio_classiff',
                                     'type': 'radio',
                                     'options': [{'label': 'test1', 'value': 'test1'},
                                                {'label': 'test2', 'value': 'test2'},
                                                {'label': 'test3', 'value': 'test3'}]},
                                    {'required': True,
                                     'instructions': 'checklist classifd',
                                     'name': 'checklist_classifd',
                                     'type': 'checklist',
                                     'options': [{'label': 'option1', 'value': 'option1'},
                                                    {'label': 'option2', 'value': 'option2'},
                                                    {'label': 'option3', 'value': 'option3'}]},
                                    {'required': True,
                                     'instructions': 'test classficactiin: question?',
                                     'name': 'test_classficactiin:_question?',
                                     'type': 'text',
                                     'options': []},
                                    {'required': True,
                                     'instructions': 'dropdown',
                                     'name': 'dropdown',
                                     'type': 'dropdown',
                                     'options': [{'label': 'dropdown op1', 'value': 'dropdown_op1'},
                                                 {'label': 'dropdown opt2', 'value': 'dropdown_opt2'},
                                                 {'label': 'dropdown opt3', 'value': 'dropdown_opt3'}]}]}]
            """
            # Add attribute groups as nested classifications for labelbox.
            if label_element.get('attribute_group_list') and len(label_element.get('attribute_group_list')) > 0:
                attribute_groups = label_element.get('attribute_group_list')
                element['classifications'] = []
                for attribute in attribute_groups:
                    group = {
                        'required': False,
                        'name': attribute.get('name'),
                        'instructions': attribute.get('prompt'),
                        'type': self.LABELBOX_DIFFGRAM_CLASSIFICATIONS_MAPPING[attribute.get('kind')],
                        'options': [
                            {'label': opt.get('name'), 'value': opt.get('name')}
                            for opt in attribute['attribute_template_list']
                        ]
                    }
                    element['classifications'].append(group)
            result.append(element)
        return result

    def save_label_instance_ontology_mapping(self, ontology, connection):
        """
            Saves the relationships betweend ID's of Diffgram label instances
            and ID's of the featureNode ID's in the onthology.
        :param ontology:
        :return:
        """
        mapping = {}
        tools = ontology['project']['ontology']['normalized']['tools']
        for tool in tools:
            diffgram_label_file = self.task_template.get_label_file_by_name(tool['name'])
            diffgram_label_file_id = self.task_template.get_label_file_by_name(tool['name'])['id']
            # Feature schema ID was removed from API. Using name instead
            # feature_schema_id = tool['featureSchemaId']
            feature_schema_id = tool['name']
            mapping[feature_schema_id] = {'label_id': diffgram_label_file_id, 'attributes': {}}
            ExternalMap.new(session=self.session,
                            file_id=diffgram_label_file_id,
                            external_id=feature_schema_id,
                            type=connection.integration_name,
                            diffgram_class_string='label_file',
                            connection=connection,
                            add_to_session=True)
            if tool.get('classifications', None):
                classifications = tool.get('classifications', None)
                for classification in classifications:
                    attribute_group = self.task_template.get_attribute_group_by_name(diffgram_label_file,
                                                                                     classification['name'])
                    diffgram_attribute_group_id = attribute_group['id']
                    # feature_schema_id = classification['featureSchemaId']
                    # Changing to name since feature schema was removed.
                    feature_schema_id = classification['name']
                    ExternalMap.new(session=self.session,
                                    external_id=feature_schema_id,
                                    file_id=diffgram_label_file_id,
                                    attribute_template_group_id=diffgram_attribute_group_id,
                                    type=connection.integration_name,
                                    diffgram_class_string='label_file',
                                    connection=connection,
                                    add_to_session=True)
        return mapping

    def create_labelbox_project(self, connector):

        result = connector.put_data({
            'action_type': 'create_project',
            'name': self.task_template.name,
            'event_data': {},
        })
        if result_has_error(result):
            raise Exception('Failed to setup labelbox project. {}'.format(str(result)))
        if 'result' in result:
            labelbox_project = result['result']
        else:
            logger.error(result)
        return labelbox_project

    def create_labelbox_project_mapping(self, labelbox_project, connection):
        external_map = ExternalMap.new(
            session=self.session,
            job=self.task_template,
            external_id=labelbox_project.uid,
            connection=connection,
            diffgram_class_string='task_template',
            type=connection.integration_name,
            url='https://app.labelbox.com/projects/{}/overview'.format(labelbox_project.uid),
            add_to_session=True,
            flush_session=True
        )
        # Commented to bottom to avoid circular dependencies on job.
        self.task_template.default_external_map = external_map

        logger.debug('Created Labelbox Project {}'.format(labelbox_project.uid))
        return external_map

    def get_labelbox_frontend(self, connector):
        result = connector.fetch_data({
            'action_type': 'get_default_frontend',
            'event_data': {},
        })
        if result_has_error(result):
            raise Exception('Failed to setup labelbox frontend. {}'.format(str(result)))
        frontend = result['result']
        logger.debug('Created Labelbox Frontend.')
        return frontend

    def create_ontology(self, connector, frontend, labelbox_project):
        options = {"tools": self.__create_tools_from_task_templates(), "classifications": []}
        options = json.dumps(options)
        result = connector.put_data({
            'action_type': 'setup_ontology',
            'frontend': frontend,
            'ontology': options,
            'project': labelbox_project,
            'event_data': {},
        })
        if result_has_error(result):
            raise Exception('Failed to setup labelbox onthology. {}'.format(str(result)))
        logger.debug('Created Labelbox Project Ontology.')
        # Now save ontology relations
        query_ontology = """
            query($projectId: ID!) { 
                project (where: {id: $projectId }) { 
                    ontology { 
                        normalized 
                    } 
                }
            }
        """
        data = {'projectId': labelbox_project.uid}
        result_ontology = connector.put_data({'action_type': 'execute',
                                              'query': query_ontology,
                                              'data': data,
                                              'event_data': {}})
        ontology = result_ontology['result']
        return ontology

    def execute_after_launch_strategy(self):
        """
            This strategy will attach files from sync directories and creates tasks in
            Diffgram for each of them.
        :return:
        """
        labelbox_project = None
        try:
            # TODO: ADD LABELBOX LOGIC HERE
            # We don't check perms here because we assume this was checked on the task template creation.
            # Otherwise, we would need request context here, which we don't have.
            connection = self.task_template.interface_connection
            logger.debug('Connection for labelbox: {}'.format(connection))
            connector_manager = ConnectorManager(connection=connection, session=self.session)
            connector = connector_manager.get_connector_instance()
            connector.connect()

            # First we create a project
            labelbox_project = self.create_labelbox_project(connector)
            external_map = self.create_labelbox_project_mapping(labelbox_project, connection)

            # Now create labelbox frontend
            frontend = self.get_labelbox_frontend(connector)

            # Next, we specify an ontology based on the label_templates of the task template.
            # Note: for now all classifications wil be nested.
            ontology = self.create_ontology(connector, frontend, labelbox_project)
            self.save_label_instance_ontology_mapping(ontology, connection)

            # Then we create a dataset for the project, where we'll add all the files
            labelbox_sync_manager = LabelBoxSyncManager(
                session=self.session,
                labelbox_project=labelbox_project,
                task_template=self.task_template,
                log=self.log,
                labelbox_connector=connector
            )

            # We first set the webhook for this task template.
            labelbox_sync_manager.set_webhook_for_task_template()

            # Then we start adding all files to labelbox.
            labelbox_sync_manager.send_all_files_in_task_template()
            logger.info(
                'LabelboxTaskTemplateAfterLaunchStrategy for Task Template ID: {} completed successfully.'.format(
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
            # Rollback Delete Labelbox Project
            if labelbox_project is not None:
                if self.task_template.default_external_map:
                    self.task_template.default_external_map = None
                    self.session.delete(self.task_template.default_external_map)
                labelbox_project.delete()
                logger.debug('ROLLBACK. Deleted Labelbox Project {}'.format(labelbox_project.uid))
                # Allow time for rate limiter in case of a rate limit exception.
                time.sleep(5)
            raise e
