from shared.database_setup_supporting import *
from shared.helpers.sessionMaker import session_factory
from lark import Lark, Transformer, v_args
from sqlalchemy import func


@v_args(inline = True)  # Affects the signatures of the methods
class DiffgramQueryProcessor(Transformer):
    conditions = []

    def expr(self, a, b, c):
        print('ON EXPR', a, b, c)

    def start(self, a):
        print('ON start', a)
        return

    def factor(self, a):
        print('ON factor', a)

    def term(self, a):
        print('ON term', a)

    def compare_op(self):
        print('ON compare_op')

    def compare_expr(self, a, b, c):
        print('on compare_expr', a, b, c)
        self.conditions.push(

        )


class QueryCreator:
    """
        Responsible for creating a DiffgramQuery based on the defined syntax.
    """
    grammar_definition = """
        start: expr
        expr: term [OR term]
        term: factor [AND factor]
        factor: compare_expr
        compare_expr: NAME COMPARE_OP NAME
        COMPARE_OP: ">" | "<" | "=" | "!=" | ">=" | "<="
        OR: "or"
        AND: "and"
        NAME: CNAME ["." CNAME]+ | NUMBER
        %import common.CNAME 
        %import common.NUMBER
        _WHITESPACE: /[ \t]+/ 
        %ignore _WHITESPACE
    """

    def __init__(self, query_string):
        query_parser = Lark(self.grammar_definition, parser = 'lalr', transformer = DiffgramQueryProcessor())
        self.build_query = query_parser.parse
        self.query_string = query_string

    def create_query(self):
        return self.build_query(self.query_string)


def get_files_by_instance_count(session):
    instance_list_count = (session.query(func.count(Instance.id)).filter(
        Instance.file_id == File.id,

    ))
    file_list = session.query(File).filter(File.project_id == 1, instance_list_count.as_scalar() > 4)
