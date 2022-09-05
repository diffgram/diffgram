from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement, QueryEntity
from shared.query_engine.expressions.expressions import CompareExpression, CompareOperator
from shared.query_engine.sql_alchemy_query_elements.scalar import ScalarQueryElement
from shared.query_engine.sql_alchemy_query_elements.file import FileQueryElement
from shared.query_engine.sql_alchemy_query_elements.attribute import AttributeQueryElement
from shared.query_engine.sql_alchemy_query_elements.dataset import DatasetQuery
from shared.query_engine.sql_alchemy_query_elements.dataset_tag import TagDatasetQueryElement
from shared.query_engine.sql_alchemy_query_elements.labels import LabelsQueryElement
from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement
from lark import Token
from typing import List


class TestQueryElement(testing_setup.DiffgramBaseTestCase):
    """



    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestQueryElement, self).setUp()
        project_data = data_mocking.create_project_with_context(
            {
                'users': [
                    {'username': 'Test',
                     'email': 'test@test.com',
                     'password': 'diffgram123',
                     }
                ]
            },
            self.session
        )
        self.project = project_data['project']
        self.project_data = project_data
        self.auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        self.member = self.auth_api.member

    def test_determine_if_reserved_word(self):
        reserved_words: List[str] = ['label', 'attribute', 'file', 'dataset_id', 'dataset_tag', 'list']
        q_elm = QueryElement()
        for w in reserved_words:
            res = q_elm.determine_if_reserved_word(w)
            self.assertTrue(res)
        res = q_elm.determine_if_reserved_word('something else')
        self.assertFalse(res)

    def test_new_error(self):
        # Test error invalid keyword
        query_element, log = QueryElement.new(
            session = self.session,
            log = regular_log.default(),
            project_id = self.project.id,
            token = Token(value = "something", type_ = "something")
        )

        self.assertEqual(list(log['error'].keys()), ['is_reserved_word'])
        self.assertIsNone(query_element)

    def test_new_scalar(self):
        # Test scalar
        query_element, log = QueryElement.new(
            session = self.session,
            log = regular_log.default(),
            project_id = self.project.id,
            token = Token(value = "'something'", type_ = "something")
        )

        self.assertEqual(list(log['error'].keys()), [])
        self.assertIsNotNone(query_element)
        self.assertEqual(type(query_element), ScalarQueryElement)
        self.assertIsNotNone(query_element.project_id)
        self.assertIsNotNone(query_element.log)
        self.assertIsNotNone(query_element.query_entity.key, "scalar")

    def test_new_file(self):
        # Test file
        query_element, log = QueryElement.new(
            session = self.session,
            log = regular_log.default(),
            project_id = self.project.id,
            token = Token(value = "file.something", type_ = "something")
        )

        self.assertEqual(list(log['error'].keys()), [])
        self.assertIsNotNone(query_element)
        self.assertEqual(type(query_element), FileQueryElement)
        self.assertIsNotNone(query_element.project_id)
        self.assertIsNotNone(query_element.log)
        self.assertIsNotNone(query_element.query_entity.key, "file")

    def test_attribute(self):
        attr = data_mocking.create_attribute_template_group({
            'name': f'something',
            'project_id': self.project.id,
            'kind': 'select'
        }, self.session)
        query_element, log = QueryElement.new(
            session = self.session,
            log = regular_log.default(),
            project_id = self.project.id,
            token = Token(value = "attribute.something", type_ = "something")
        )

        self.assertEqual(list(log['error'].keys()), [])
        self.assertIsNotNone(query_element)
        self.assertEqual(type(query_element), AttributeQueryElement)
        self.assertIsNotNone(query_element.project_id)
        self.assertIsNotNone(query_element.log)
        self.assertIsNotNone(query_element.query_entity.key, "attribute")

    def test_dataset(self):
        # Test file
        query_element, log = QueryElement.new(
            session = self.session,
            log = regular_log.default(),
            project_id = self.project.id,
            token = Token(value = "dataset.id", type_ = "something")
        )

        self.assertEqual(list(log['error'].keys()), [])
        self.assertIsNotNone(query_element)
        self.assertEqual(type(query_element), DatasetQuery)
        self.assertIsNotNone(query_element.project_id)
        self.assertIsNotNone(query_element.log)
        self.assertIsNotNone(query_element.query_entity.key, "dataset_id")

    def test_dataset_tag(self):
        # Test file
        query_element, log = QueryElement.new(
            session = self.session,
            log = regular_log.default(),
            project_id = self.project.id,
            token = Token(value = "dataset.tag", type_ = "something")
        )

        self.assertEqual(list(log['error'].keys()), [])
        self.assertIsNotNone(query_element)
        print('type(query_element)', type(query_element))
        self.assertEqual(type(query_element), TagDatasetQueryElement)
        self.assertIsNotNone(query_element.project_id)
        self.assertIsNotNone(query_element.log)
        self.assertIsNotNone(query_element.query_entity.key, "dataset_tag")


    def test_label(self):
        # Test file
        label = data_mocking.create_label({
            'name': 'robot',
        }, self.session)
        label_file = data_mocking.create_label_file({
            'label': label,
            'project_id': self.project.id
        }, self.session)
        query_element, log = QueryElement.new(
            session = self.session,
            log = regular_log.default(),
            project_id = self.project.id,
            token = Token(value = "label.robot", type_ = "something")
        )

        self.assertEqual(list(log['error'].keys()), [])
        self.assertIsNotNone(query_element)
        self.assertEqual(type(query_element), LabelsQueryElement)
        self.assertIsNotNone(query_element.project_id)
        self.assertIsNotNone(query_element.log)
        self.assertIsNotNone(query_element.query_entity.key, "dataset_tag")
