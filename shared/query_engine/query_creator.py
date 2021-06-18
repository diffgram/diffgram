from shared.database_setup_supporting import *
from shared.helpers.sessionMaker import session_factory
from lark import Lark, Transformer, v_args
from lark.exceptions import UnexpectedCharacters, UnexpectedToken
from sqlalchemy import func
from shared.query_engine.diffgram_query import DiffgramQuery
from shared.query_engine.grammar import grammar_definition


@v_args(inline = True)  # Affects the signatures of the methods
class DiffgramQueryProcessor(Transformer):
    conditions = {'root': []}
    current_node = None


class QueryCreator:
    """
        Responsible for creating a DiffgramQuery based on the defined syntax.
    """

    def __init__(self, session, project, member):
        self.project = project
        self.session = session
        self.member = member
        self.parser = query_parser = Lark(grammar_definition,
                                          parser = 'lalr',
                                          transformer = None)
        self.build_query = query_parser.parse

    def get_suggestions(self, query_string):
        if query_string == '':
            return ['labels', 'file', 'instance', 'dataset', 'issues']
        try:
            result = self.create_query(query_string)
            # If the query is correct we don't suggest anything
            return []
        except UnexpectedCharacters as chars_exception:
            if type(chars_exception) == UnexpectedCharacters:
                if chars_exception.char == '.':
                    last_token = chars_exception.state.value_stack[0]
                    suggestions = []
                    if last_token.value in ['label', 'labels']:
                        # Show available labels in project.
                        labels = self.project.get_label_list(self.session, directory = self.project.directory_default)
                        for label in labels:
                            suggestions.append(label['label']['name'])
                    elif last_token.value == ['file', 'files']:
                        suggestions = ['date', 'metadata', 'tag']
                    elif last_token.value == ['instance', 'instances']:
                        suggestions = ['type', 'count', 'tag', 'model', 'model_run']
                    elif last_token.value == ['issues', 'issue']:
                        suggestions = ['status', 'count']
                    return suggestions
            return []
        except UnexpectedToken as token_exception:
            print('UNEXPECTED TOKEN')
            return

    def create_query(self, query_string):
        tree = self.build_query(query_string)
        return DiffgramQuery(tree, self.project, self.member)


def get_files_by_instance_count(session):
    instance_list_count_subquery = (session.query(func.count(Instance.id)).filter(
        Instance.file_id == File.id,

    ))
    file_list = session.query(File).filter(File.project_id == 1, instance_list_count_subquery.as_scalar() > 4)
