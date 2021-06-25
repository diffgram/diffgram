from lark.visitors import Visitor
from shared.query_engine.diffgram_query import DiffgramQuery
from abc import ABC, abstractmethod
from shared.database.source_control.file import File
from shared.database.annotation.instance import Instance
from sqlalchemy import func
from shared.query_engine.diffgram_query_exectutor import BaseDiffgramQueryExecutor
from shared.shared_logger import get_shared_logger
import operator
from shared.regular import regular_log
from sqlalchemy.sql.expression import and_, or_
from shared.database.source_control.working_dir import WorkingDirFileLink
from shared.permissions.project_permissions import Project_permissions
from shared.query_engine.query_creator import ENTITY_TYPES
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
        self.log = regular_log.default()
        self.session = session
        self.final_query = self.session.query(File).join(WorkingDirFileLink, WorkingDirFileLink.file_id == File.id).filter(
            File.project_id == self.diffgram_query.project.id,
            File.state != 'removed',
            File.type.in_(['video', 'image'])
        )
        if diffgram_query.directory:
            self.final_query = self.final_query.filter(
                WorkingDirFileLink.working_dir_id == self.diffgram_query.directory.id
            )
        # Additional security check just for sanity
        Project_permissions.by_project_core(
            project_string_id = self.diffgram_query.project.project_string_id,
            Roles = ["admin", "Editor", "Viewer", "allow_if_project_is_public"],
            apis_project_list = [],
            apis_user_list = ['security_email_verified']
        )
        self.conditions = []
        self.valid = False

    def start(self, *args):
        if len(self.log['error'].keys()) > 0:
            return
        self.valid = False
        if len(args) == 1:
            local_tree = args[0]
            if len(local_tree.children) == 1:
                child = local_tree.children[0]
                self.final_query = self.final_query.filter(
                    child.or_statement
                )
                self.valid = True
                return self.final_query

            else:
                error_msg = 'Invalid children number for start: Must have only 1 and has {}'.format(len(local_tree.children))
                logger.error(error_msg)
                self.log['error']['start'] = error_msg
        else:
            logger.error('Invalid child count for start. Must be 1 and is {}'.format(len(args)))
            self.log['error']['start'] = 'Invalid child count for factor. Must be 1'
        return self.final_query

    def expr(self, *args):
        """
            The expr rule should join one or more conditions in an OR statement.
        :param args:
        :return:
        """
        if len(self.log['error'].keys()) > 0:
            return
        if len(args) == 1:
            local_tree = args[0]
            conditions = []
            for child in local_tree.children:
                if hasattr(child, 'and_statement'):
                    conditions.append(child.and_statement)
            local_tree.or_statement = or_(*conditions)
            return local_tree
        else:
            logger.error('Invalid child count for expr. Must be 1 and is {}'.format(len(args)))
            self.log['error']['expr'] = 'Invalid child count for factor. Must be 1'

    def term(self, *args):
        """
            The term rule should join one or more conditions in an AND statement.
        :param args:
        :return:
        """
        if len(self.log['error'].keys()) > 0:
            return
        if len(args) == 1:
            local_tree = args[0]
            conditions = []
            for child in local_tree.children:
                if hasattr(child, 'query_condition'):
                    conditions.append(child.query_condition)
            local_tree.and_statement = and_(*conditions)
            return local_tree
        else:
            logger.error('Invalid child count for term. Must be 1 and is {}'.format(len(args)))
            self.log['error']['term'] = 'Invalid child count for factor. Must be 1'

    def factor(self, *args):
        if len(self.log['error'].keys()) > 0:
            return
        if len(args) == 1:
            local_tree = args[0]
            if len(local_tree.children) == 1:
                local_tree.query_condition = local_tree.children[0].query_condition
                return local_tree
            else:
                logger.error('Invalid child count for factor. Must be 1')
                self.log['error']['factor'] = 'Invalid child count for factor. Must be 1'

    def __determine_entity_type(self, name_token):
        try:
            int(name_token.value)
            return int
        except ValueError:
            pass
        # If it is not an int then it should be a string entity type (like "file" or "labels")
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
        entity_type = self.__determine_entity_type(token)
        if entity_type == 'labels':
            label_name = token.value.split('.')[1]
            label_file = File.get_by_label_name(session = self.session,
                                                label_name = label_name,
                                                project_id = self.diffgram_query.project.id)
            if not label_file:
                # Strip underscores
                label_name = label_name.replace('_', ' ')
                label_file = File.get_by_label_name(session = self.session,
                                                    label_name = label_name,
                                                    project_id = self.diffgram_query.project.id)
            if not label_file:
                error_string = 'Label {} does not exists'.format(str(label_name))
                logger.error(error_string)
                self.log['error']['label_name'] = error_string
                return

            instance_list_count_subquery = (self.session.query(func.count(Instance.id)).filter(
                or_(
                   and_(
                       Instance.file_id == File.id,
                       Instance.label_file_id == label_file.id,
                   ),
                    and_(
                        Instance.parent_file_id == File.id,
                        Instance.label_file_id == label_file.id
                    )
                )

            ))
            return instance_list_count_subquery.as_scalar()
        elif entity_type == 'file':
            # Case for metadata
            metadata_key = token.value.split('.')[1]
            return File.file_metadata[metadata_key].astext
        else:
            return token.value

    def __validate_expression(self, token1, token2, operator):
        """
            This functions has the reponsability of checking that the expression operators
            are semantically valid for each of the different contexts.
        :param token1:
        :param token2:
        :param operator:
        :return:
        """

        entity_type1 = self.__determine_entity_type(token1)
        entity_type2 = self.__determine_entity_type(token2)
        if len(token1.value.split('.')) == 1:
            error_string = 'Error with token: {}. Should specify the label name or global count'.format(token1.value)
            logger.error(error_string)
            self.log['error']['compare_expr'] = error_string
            return False

        if "file" in [entity_type1, entity_type2]:
            value_1 = self.__parse_value(token1)
            value_2 = self.__parse_value(token2)

            if operator.value not in ["=", "!="]:
                error_string = 'Invalid operator for file entity {}, valid operators are {}'.format(operator.value,
                                                                                                    str(["=", "!="]))
                logger.error(error_string)
                self.log['error']['compare_expr'] = error_string
                return False

            if type(value_1) == int and type(value_2) == int:
                logger.error('Error: at least 1 value must be a label.')

        return True



    def compare_expr(self, *args):
        if len(self.log['error'].keys()) > 0:
            return
        local_tree = args[0]
        if len(local_tree.children) == 3:
            children = local_tree.children
            name1 = children[0]
            compare_op = children[1]
            name2 = children[2]
            entity_type = self.__determine_entity_type(name1)

            if self.__validate_expression(name1, name2, compare_op):
                value_1 = self.__parse_value(name1)
                value_2 = self.__parse_value(name2)
                if len(self.log['error'].keys()) > 0:
                    return
                self.conditions.append(
                    self.get_compare_op(compare_op)(
                        value_1,
                        value_2
                    )
                )
                if entity_type == "labels":
                    local_tree.query_condition = self.get_compare_op(compare_op)(value_1, value_2)
                    # self.final_query = self.final_query.filter(
                    #     self.get_compare_op(compare_op)(
                    #         value_1,
                    #         value_2
                    #     )
                    # )
                    return local_tree
                elif entity_type == 'file':
                    local_tree.query_condition = self.get_compare_op(compare_op)(value_1, str(value_2))
                    # self.final_query = self.final_query.filter(
                    #     self.get_compare_op(compare_op)(
                    #         value_1,
                    #         str(value_2) # TODO: asummption that we just accept JSON string comparison (no numbers)
                    #     )
                    # )
                    return local_tree
            else:
                return

        else:
            self.log['error']['compare_expr'] = 'Invalid compare expression {}'.format(str(args))

    def execute_query(self):
        """
            Entrypoint for building the end query. This uses the diffgram query
            object and accesses the tree so it can be visited.

            The main assumption here is that the tree will have the nodes that corresponds to the
            grammar defined in grammar.py
        :return:
        """
        self.visit(self.diffgram_query.tree)
        if len(self.conditions) == 0 or len(self.log['error'].keys()) > 0 or not self.valid:
            logger.error('Invalid query. Please check your syntax and try again.')
            return None, self.log
        return self.final_query, self.log
