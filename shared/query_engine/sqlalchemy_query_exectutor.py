from lark.visitors import Visitor
from shared.query_engine.diffgram_query import DiffgramQuery
from abc import ABC, abstractmethod
from shared.query_engine.diffgram_query_exectutor import BaseDiffgramQueryExecutor
from shared.shared_logger import get_shared_logger

logger = get_shared_logger()

class SqlAlchemyQueryExecutor(BaseDiffgramQueryExecutor):
    """
        The Diffgram Query Object is a tree visitors that
        can be traversed to generate relevant output for different
        usecases. This object is the input for classes that implement
        the DiffgramQueryExecutor.
    """


    def __init__(self, diffgram_query: DiffgramQuery):
        self.diffgram_query = diffgram_query
        self.query_conditions = []

    def expr(self, *args):
        print('visting expr: Not Implemented yet.')

    def start(self, *args):
        print('visting start: Not Implemented yet.')

    def factor(self, *args):
        print('visting factor: Not Implemented yet.')

    def term(self, *args):
        print('visting term: Not Implemented yet.')

    def compare_op(self):
        print('visting compare_op: Not Implemented yet.')

    def __determine_entity_type(self, name_token):
        value = name_token.value
        value = value.splice('.')[0]
        return value

    def compare_expr(self, *args):
        print('visting compare_expr: Not Implemented yet.', args)
        if len(args) == 3:
            name1 = args[0]
            compare_op = args[1]
            name2 = args[1]
            entity_type = self.__determine_entity_type(name1)
            if entity_type == 'labels':
                if len(name1.value.split('.')) == 1:
                    logger.error('Error with token: {}. Should specify the label name or global count'.format(name1.vale))
                else:
                    label_name = name1.value.split('.')[1]
                    label_file =



