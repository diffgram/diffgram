from shared.database_setup_supporting import *
from shared.helpers.sessionMaker import session_factory
from lark import Lark, Transformer, v_args
from lark.exceptions import UnexpectedCharacters, UnexpectedToken
from sqlalchemy import func
from shared.query_engine.diffgram_query import DiffgramQuery
from shared.query_engine.grammar import grammar_definition
from shared.regular import regular_log
from shared.shared_logger import get_shared_logger

logger = get_shared_logger()


class QueryCreator:
    """
        Responsible for creating a DiffgramQuery based on the defined syntax.
    """
    ENTITY_TYPES = ['labels', 'file', 'instance', 'dataset', 'issues']

    def __init__(self, session, project, member):
        self.project = project
        self.session = session
        self.member = member
        self.log = regular_log.default()
        self.parser = query_parser = Lark(grammar_definition,
                                          parser = 'lalr',
                                          transformer = None)
        self.build_query = query_parser.parse

    def get_suggestions(self, query_string):
        if query_string == '':
            return self.ENTITY_TYPES
        try:
            result = self.build_query(query_string)
            print('AAA', result)
            # If the query is correct we don't suggest anything
            return []
        except UnexpectedCharacters as chars_exception:
            if type(chars_exception) == UnexpectedCharacters:
                if chars_exception.char == '.':
                    last_token = chars_exception.state.value_stack[0]
                    suggestions = []
                    print('LAST TOKEN', last_token)
                    if last_token.value in ['label', 'labels']:
                        # Show available labels in project.
                        labels = self.project.get_label_list(self.session, directory = self.project.directory_default)
                        for label in labels:
                            suggestions.append(label['label']['name'])
                    elif last_token.value in ['file', 'files']:
                        # TODO: add metadata suggestions
                        suggestions = ['date', 'tag']
                    elif last_token.value in ['instance', 'instances']:
                        suggestions = ['type', 'count', 'tag', 'model', 'model_run']
                    elif last_token.value in ['issues', 'issue']:
                        suggestions = ['status', 'count']
                    return suggestions
            return []
        except UnexpectedToken as token_exception:
            logger.error('Unexpected token {}'.format(str(token_exception)))
            return False

    def create_query(self, query_string):
        try:
            tree = self.build_query(query_string)
            print(tree.pretty())
            return DiffgramQuery(tree, self.project, self.member)
        except Exception as e:
            self.log['error']['parser'] = str(e)
