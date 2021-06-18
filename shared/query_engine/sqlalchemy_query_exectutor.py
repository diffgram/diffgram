from lark.visitors import Visitor
from shared.query_engine.diffgram_query import DiffgramQuery
from abc import ABC, abstractmethod
from shared.database.source_control.file import File
from shared.database.annotation.instance import Instance
from sqlalchemy import func
from shared.query_engine.diffgram_query_exectutor import BaseDiffgramQueryExecutor
from shared.shared_logger import get_shared_logger
import operator
logger = get_shared_logger()

class SqlAlchemyQueryExecutor(BaseDiffgramQueryExecutor):
    """
        The Diffgram Query Object is a tree visitors that
        can be traversed to generate relevant output for different
        usecases. This object is the input for classes that implement
        the DiffgramQueryExecutor.
    """


    def __init__(self, session, diffgram_query: DiffgramQuery):
        self.diffgram_query = diffgram_query
        self.session = session
        self.final_query = self.session.query(File).filter(
            File.project_id == self.diffgram_query.project.id
        )
    def expr(self, *args):
        print('visting expr: Not Implemented yet.')

    def start(self, *args):
        print('visting start: Not Implemented yet.')
        return self.final_query

    def factor(self, *args):
        print('visting factor: Not Implemented yet.')

    def term(self, *args):
        print('visting term: Not Implemented yet.')

    def compare_op(self):
        print('visting compare_op: Not Implemented yet.')

    def __determine_entity_type(self, name_token):
        value = name_token.value
        value = value.split('.')[0]
        return value

    def get_compare_op(self, token):
        if token.value == '>':
            return operator.gt
        if token.value == '<':
            return operator.lt
        if token.value == '=':
            return operator.eq
        if token.value == '!=':
            return operator.ne
        if token.value == '>=':
            return operator.ge
        if token.value == '<=':
            return operator.le

    def __parse_value(self, token):
        """
            Transforms the token into an integer or appropriate diffgram value (instance count, issue count, etc)
        :param token:
        :return:
        """
        # First try to convert into int.
        try:
            result = int(token.value)
            return result
        except ValueError:
            pass

        # If value is not a number then it's a variable name (such as a label name)
        # TODO: for now we assume no "nested" names are allowed. In other words, the dot syntax just has 1 level deep.
        label_name = token.value.split('.')[1]
        label_file = File.get_by_label_name(session = self.session,
                                            label_name = label_name,
                                            project_id = self.diffgram_query.project.id)
        instance_list_count_subquery = (self.session.query(func.count(Instance.id)).filter(
            Instance.file_id == File.id,
            Instance.label_file_id == label_file.id

        ))
        return instance_list_count_subquery.as_scalar()

    def compare_expr(self, *args):
        local_tree = args[0]
        print('children', local_tree.children)
        if len(local_tree.children) == 3:
            children = local_tree.children
            name1 = children[0]
            compare_op = children[1]
            name2 = children[2]
            entity_type = self.__determine_entity_type(name1)
            print('entyt typeee', entity_type)
            if entity_type == 'labels':
                if len(name1.value.split('.')) == 1:
                    logger.error('Error with token: {}. Should specify the label name or global count'.format(name1.vale))
                else:
                    value_1 = self.__parse_value(name1)
                    value_2 = self.__parse_value(name2)
                    if type(value_1) == int and type(value_1) == int:
                        logger.error('Error: at least 1 value must be a label.')
                    print('val1', value_1, 'val2', value_2)
                    self.final_query = self.final_query.filter(
                        self.get_compare_op(compare_op)(
                            value_1,
                            value_2
                        )
                    )
                    print('new final query is', self.final_query)


    def execute_query(self):
        """
            Entrypoint for building the end query. This uses the diffgram query
            object and accesses the tree so it can be visited.

            The main assumption here is that the tree will have the nodes that corresponds to the
            grammar defined in grammar.py
        :return:
        """
        self.visit(self.diffgram_query.tree)
        return self.final_query

