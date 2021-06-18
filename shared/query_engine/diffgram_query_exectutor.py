from lark.visitors import Visitor
from shared.query_engine.diffgram_query import DiffgramQuery
from abc import ABC, abstractmethod


class BaseDiffgramQueryExecutor(Visitor, ABC):
    """
        The Diffgram Query Object is a tree visitors that
        can be traversed to generate relevant output for different
        usecases. This object is the input for classes that implement
        the DiffgramQueryExecutor.
    """

    def __init__(self, diffgram_query: DiffgramQuery):
        self.diffgram_query = diffgram_query

    @abstractmethod
    def expr(self, *args):
        print('visting expr: Not Implemented yet.')

    @abstractmethod
    def start(self, *args):
        print('visting start: Not Implemented yet.')

    @abstractmethod
    def factor(self, *args):
        print('visting start: Not Implemented yet.')

    @abstractmethod
    def term(self, *args):
        print('visting start: Not Implemented yet.')

    @abstractmethod
    def compare_op(self):
        print('visting start: Not Implemented yet.')

    @abstractmethod
    def compare_expr(self, *args):
        print('visting start: Not Implemented yet.')

    @abstractmethod
    def execute_query(self):
        """
            Entrypoint for building the end query. This uses the diffgram query
            object and accesses the tree so it can be visited.

            The main assumption here is that the tree will have the nodes that corresponds to the
            grammar defined in grammar.py
        :return:
        """
        return self.visit(self.diffgram_query.tree)
