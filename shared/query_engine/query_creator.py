from parsimonious.grammar import Grammar
from lark import Lark, Transformer, v_args


@v_args(inline = True)  # Affects the signatures of the methods
class DiffgramQueryProcessor(Transformer):

    def expr(self, a, b, c):
        print('ON EXPR', a, b, c)

    def op(self):
        print('ON OP')


class QueryCreator:
    """
        Responsible for creating a DiffgramQuery based on the defined syntax.
    """
    grammar_definition = """
        expr: term {or term}
        term: factor{and factor}
        factor: compare_expr
        compare_op: ">" | "<" | "=" | "!=" | ">=" | "<="
        or: "or"
        
        %import common.CNAME -> NAME 
    """

    def __init__(self, query_string):
        query_parser = Lark(self.grammar_definition, parser = 'lalr', transformer = DiffgramQueryProcessor())
        self.build_query = query_parser.parse
        self.query_string = query_string

    def create_query(self):
        return self.build_query(self.query_string)



