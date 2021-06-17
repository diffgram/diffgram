from shared.database_setup_supporting import *
from shared.helpers.sessionMaker import session_factory
from lark import Lark, Transformer, v_args
from lark.exceptions import UnexpectedCharacters, UnexpectedToken
from sqlalchemy import func


@v_args(inline = True)  # Affects the signatures of the methods
class DiffgramQueryProcessor(Transformer):
    conditions = []

    def expr(self, *args):
        print('ON EXPR', args)

    def start(self, *args):
        print('ON start', args)
        return

    def factor(self, *args):
        print('ON factor', args)

    def term(self, *args):
        print('ON term', args)

    def compare_op(self):
        print('ON compare_op')

    def compare_expr(self, *args):
        print('on compare_expr', args)
        self.conditions.append(
            args
        )


def show_next_possible_tokens(error):
    print('error', error)
    # print('ERROR HANDLER  :) TOKEN', error.interactive_parser)
    return True


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
        NAME: CNAME [DOT CNAME]+ | CNAME | NUMBER
        DOT: "."
        %import common.CNAME 
        %import common.NUMBER
        _WHITESPACE: /[ \t]+/ 
        %ignore _WHITESPACE
    """

    def __init__(self, session, project):
        self.project = project
        self.session = session
        self.parser = query_parser = Lark(self.grammar_definition,
                                          parser = 'lalr',
                                          transformer = DiffgramQueryProcessor())
        self.build_query = query_parser.parse

    def get_suggestions(self, query_string):
        if query_string == '':
            return ['annotations', 'labels', 'file', 'instance', 'dataset', 'issues']
        try:
            result = self.create_query(query_string)
            return result
        except UnexpectedCharacters as chars_exception:
            print('UnexpectedCharacters',chars_exception)
        except UnexpectedToken as token_exception:
            last_char_index = token_exception.state.state_stack[0]
            print('LAST index: ', last_char_index)
            print('LAST CHAR: ', query_string[last_char_index])
            print('token: ', token_exception.token)
            print('char: ', token_exception.char)
            print('line: ', token_exception.line)
            print('_terminals_by_name: ', token_exception._terminals_by_name)
            print('column: ', token_exception.column)
            print('accepts: ', token_exception.accepts)
            print('state: ', token_exception.state)
            print('state_stack: ', token_exception.state.state_stack)
            print('state: ', token_exception.state.value_stack)
            print('expected: ', token_exception.expected)
            print('considered_rules: ', token_exception.considered_rules)
            print('interactive_parser: ', token_exception.interactive_parser)
            print('interactive_parser accepts: ', token_exception.interactive_parser.accepts())
            print('interactive_parser choices: ', token_exception.interactive_parser.choices())
            print('interactive_parser choices: ', token_exception.interactive_parser.choices())
            print('_terminals_by_name: ', token_exception._terminals_by_name)
            print('token_history: ', token_exception.token_history)


    def create_query(self, query_string):
        return self.build_query(query_string, on_error = show_next_possible_tokens)


def get_files_by_instance_count(session):
    instance_list_count = (session.query(func.count(Instance.id)).filter(
        Instance.file_id == File.id,

    ))
    file_list = session.query(File).filter(File.project_id == 1, instance_list_count.as_scalar() > 4)
