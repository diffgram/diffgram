from shared.database_setup_supporting import *
from shared.helpers.sessionMaker import session_factory
from lark import Lark, Transformer, v_args
from lark.exceptions import UnexpectedCharacters, UnexpectedToken
from sqlalchemy import func
from shared.query_engine.diffgram_query import DiffgramQuery
from shared.query_engine.grammar import grammar_definition
from shared.regular import regular_log
from shared.shared_logger import get_shared_logger
from shared.permissions.project_permissions import Project_permissions
logger = get_shared_logger()

ENTITY_TYPES = ['labels', 'file', 'instance', 'dataset', 'issues']
class QueryCreator:
    """
        Responsible for creating a DiffgramQuery based on the defined syntax.
    """


    def __init__(self, session, project, member, directory = None):
        self.project = project
        self.session = session
        self.member = member
        self.directory = directory
        # Additional security check just for sanity
        Project_permissions.by_project_core(
            project_string_id = self.project.project_string_id,
            Roles = ["admin", "Editor", "Viewer", "allow_if_project_is_public"],
            apis_project_list = [],
            apis_user_list = ['security_email_verified']
        )
        self.log = regular_log.default()
        self.parser = Lark(grammar_definition,
                                          parser = 'lalr',
                                          transformer = None)

    def get_suggestions(self, query_string):
        suggest_type = 'entities'
        if query_string == '':
            return ENTITY_TYPES, suggest_type
        try:
            result = self.parser.parse(query_string)
            # If the query is correct we try the interactive parser to see next possible tokens of valid query.
            interactive = self.parser.parse_interactive(query_string)
            interactive.exhaust_lexer()
            print('AAAAA', interactive.accepts())
            suggestions = [x for x in interactive.accepts() if x != '$END']
            suggest_type = 'boolean_operator'
            return suggestions, suggest_type
        except UnexpectedCharacters as chars_exception:
            if type(chars_exception) == UnexpectedCharacters:
                if chars_exception.char == '.':
                    last_token = chars_exception.state.value_stack[len(chars_exception.state.value_stack) - 1]
                    suggestions = []
                    print('LAST TOKEN', last_token, chars_exception.state.value_stack)
                    num_nested = len(last_token.value.split('.'))
                    if last_token.type == 'COMPARE_OP':
                        suggestions.append('$number')
                        suggestions.append('$text')
                        suggest_type = 'text'
                        return suggestions, suggest_type
                    if num_nested == 1:
                        if last_token.value in ['label', 'labels']:
                            # Show available labels in project.
                            labels = self.project.get_label_list(self.session, directory = self.project.directory_default)
                            for label in labels:
                                suggestions.append(label['label']['name'])
                            suggest_type = 'labels'
                        elif last_token.value in ['file', 'files']:
                            # TODO: add metadata suggestions
                            suggestions = ['date', 'tag']
                            suggest_type = 'file_data'
                        elif last_token.value in ['instance', 'instances']:
                            suggestions = ['type', 'count', 'tag', 'model', 'model_run']
                            suggest_type = 'instance_data'
                        elif last_token.value in ['issues', 'issue']:
                            suggestions = ['status', 'count']
                            suggest_type = 'issues_data'
                    elif num_nested ==2:
                        entity = last_token.value.split('.')[0]
                        if entity in ['label', 'labels']:
                            suggestions.append('$operator')
                            suggest_type = 'operator'
                    return suggestions, suggest_type
                else:
                    print('NOT ENDING IN .')
            return [], None
        except UnexpectedToken as token_exception:
            suggestions = []
            print('TOKEN ', token_exception.accepts)
            token_type = [t for t in token_exception.accepts]
            if 'COMPARE_OP' in token_type:
                suggestions.append('$operator')
                suggest_type = 'operator'
                return suggestions, suggest_type
            elif 'NAME' in token_type:
                suggestions = ENTITY_TYPES
                suggest_type = 'text'
                return suggestions, suggest_type
            for x in self.parser.terminals:
                print(x.user_repr())
            logger.error('Unexpected token {}'.format(str(token_exception)))
            return False, None

    def create_query(self, query_string):
        try:
            tree = self.parser.parse(query_string)
            # print(tree.pretty())
            return DiffgramQuery(tree, self.project, self.member, directory = self.directory)
        except Exception as e:
            self.log['error']['parser'] = str(e)
