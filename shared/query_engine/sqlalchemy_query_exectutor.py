from lark.visitors import Visitor
from shared.query_engine.diffgram_query import DiffgramQuery
from abc import ABC, abstractmethod
from shared.query_engine.diffgram_query_exectutor import BaseDiffgramQueryExecutor


class SqlAlchemyQueryExecutor(BaseDiffgramQueryExecutor):
    """
        The Diffgram Query Object is a tree visitors that
        can be traversed to generate relevant output for different
        usecases. This object is the input for classes that implement
        the DiffgramQueryExecutor.
    """

    def __init__(self, diffgram_query: DiffgramQuery):
        self.diffgram_query = diffgram_query

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

    def compare_expr(self, *args):
        print('visting compare_expr: Not Implemented yet.')
