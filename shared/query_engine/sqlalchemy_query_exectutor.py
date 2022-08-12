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
from sqlalchemy.sql.operators import in_op
from shared.database.source_control.working_dir import WorkingDirFileLink
from shared.permissions.project_permissions import Project_permissions
from shared.database.attribute.attribute_template_group import Attribute_Template_Group
from shared.query_engine.query_creator import ENTITY_TYPES
from shared.database.source_control.file_stats import FileStats
from shared.utils.attributes.attributes_values_parsing import get_file_stats_column_from_attribute_kind
from shared.database.tag.tag import DatasetTag
from shared.database.tag.tag import JobTag
from shared.query_engine.sql_alchemy_query_elements import QueryElement, Expression, LabelQueryElement, \
    AttributeQueryElement, DatasetQueryElement, FileQueryElement

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
        self.final_query = self.session.query(File).join(WorkingDirFileLink,
                                                         WorkingDirFileLink.file_id == File.id).filter(
            File.project_id == self.diffgram_query.project.id,
            File.state != 'removed',
            File.type.in_(['video', 'image'])
        )
        self.unfiltered_query = self.session.query(File.id).join(WorkingDirFileLink,
                                                                 WorkingDirFileLink.file_id == File.id).filter(
            File.project_id == self.diffgram_query.project.id,
            File.state != 'removed',
            File.type.in_(['video', 'image'])
        )

        # if diffgram_query.directory:
        #     self.final_query = self.final_query.filter(
        #         WorkingDirFileLink.working_dir_id == self.diffgram_query.directory.id
        #     )
        #     self.unfiltered_query = self.unfiltered_query.filter(
        #         WorkingDirFileLink.working_dir_id == self.diffgram_query.directory.id
        #     )
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
                error_msg = f"Invalid children number for start: Must have only 1 and has {len(local_tree.children)}"
                logger.error(error_msg)
                self.log['error']['start'] = error_msg
        else:
            logger.error(f"Invalid child count for start. Must be 1 and is {len(args)}")
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
            logger.error(f"Invalid child count for expr. Must be 1 and is {len(args)}")
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
            logger.error(f"Invalid child count for term. Must be 1 and is {len(args)}")
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

    def array(self, args):
        local_tree = args
        id_values = []
        for token in local_tree.children:
            id_values.append(int(token.value))
        local_tree.value = id_values
        return local_tree

    def __determine_entity_type(self, name_token):

        try:
            int(name_token.value)
            return int
        except AttributeError:
            return name_token.id_values
        except TypeError:
            pass
        except ValueError:
            pass
        # If it is not an int then it should be a string entity type (like "file" or "labels")

        value = name_token.value
        if type(value) == list:
            return list
        value = value.split('.')[0]
        if value == "label" or value == "labels":
            value = "labels"  # cast to plural
        if value == "attributes" or value == "attribute":
            value = "attribute"
        if value == "files" or value == "file":
            value = "file"
        if value == "dataset" or value == "datasets":
            value = "dataset"
        return value

    def get_compare_op(self, token) -> QueryElement:
        query_element = QueryElement()
        compare_operator = query_element.set_sql_operator_from_token(token)
        return query_element

    def __get_attribute_kind_from_token(self, token: str) -> str or None:
        attr_group_name = token.value.split('.')[1]
        attribute_group = Attribute_Template_Group.get_by_name_and_project(
            session = self.session,
            name = attr_group_name,
            project_id = self.diffgram_query.project.id
        )

        if not attribute_group:
            # Strip underscores
            attr_group_name = attr_group_name.replace('_', ' ')
            attribute_group = Attribute_Template_Group.get_by_name_and_project(
                session = self.session,
                name = attr_group_name,
                project_id = self.diffgram_query.project.id
            )
        if not attribute_group:
            error_string = f"Attribute Group {str(attr_group_name)} does not exists"
            logger.error(error_string)
            self.log['error']['attr_group_name'] = error_string
            return None
        return attribute_group.kind


    def __parse_value(self, token) -> QueryElement:
        """
            Transforms the token into an integer or appropriate diffgram value (instance count, issue count, etc)
        :param token:
        :return:
        """
        entity_type = self.__determine_entity_type(token)
        query_element, self.log = QueryElement.generate_query_element(entity_type = entity_type)
        return query_element

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
            error_string = f"Error with token: {token1.value}. Should specify the label name or global count"
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

    def __build_dataset_compare_expr(self, value_1, value_2, compare_op):
        if type(value_1) == int or type(value_1) == str or type(value_1) == list:
            scalar_op = value_1
            query_op = value_2
        else:
            query_op = value_1
            scalar_op = value_2

        compare_op_sql = self.get_compare_op(compare_op)
        new_filter_subquery = compare_op_sql(query_op, scalar_op)
        return new_filter_subquery

    def __build_label_compare_expression(self, value_1: any, value_2: any, compare_op: str):
        if type(value_1) == int or type(value_1) == str:
            scalar_op = value_1
            query_op = value_2
        else:
            query_op = value_1
            scalar_op = value_2
        sql_compare_operator = self.get_compare_op(compare_op)
        new_filter_subquery = (query_op.filter(
            sql_compare_operator(FileStats.count_instances, scalar_op)).subquery()
                               )
        condition_operator = in_op(File.id, new_filter_subquery)

        return condition_operator

    def __build_attribute_compare_expression(self, name1: str, name2: str, value_1: any, value_2: any, compare_op: str):
        if type(value_1) == int or type(value_1) == str:
            scalar_op = value_1
            query_op = value_2
            attribute_kind = self.__get_attribute_kind_from_token(name2)
        else:
            query_op = value_1
            scalar_op = value_2
            attribute_kind = self.__get_attribute_kind_from_token(name1)
        sql_compare_operator = self.get_compare_op(compare_op)
        file_stats_column = get_file_stats_column_from_attribute_kind(attribute_kind)
        if attribute_kind in ['radio', 'multiple_select', 'select', 'tree']:
            scalar_op = int(scalar_op)
        new_filter_subquery = (query_op.filter(
            sql_compare_operator(file_stats_column, scalar_op)).subquery()
                               )
        condition_operator = in_op(File.id, new_filter_subquery)
        return condition_operator

    def compare_expr(self, *args) -> QueryElement:
        if len(self.log['error'].keys()) > 0:
            return
        local_tree = args[0]
        result = QueryElement()
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


                compare_operator = None

                if entity_type == "labels":
                    label_condition_operator = self.__build_label_compare_expression(value_1, value_2, compare_op)
                    local_tree.query_condition = label_condition_operator
                    return local_tree
                elif entity_type == 'attribute':
                    attribute_condition_op = self.__build_attribute_compare_expression(
                        name1 = name1,
                        name2 = name2,
                        value_1 = value_1,
                        value_2 = value_2,
                        compare_op = compare_op
                    )
                    local_tree.query_condition = attribute_condition_op
                elif entity_type == "dataset":
                    condition_operator = self.__build_dataset_compare_expr(value_1, value_2, compare_op)
                    local_tree.query_condition = condition_operator
                elif entity_type == "tag":
                    column = self.__build_dataset_compare_expr(value_1, value_2, compare_op)

                    # Get tag id list from value 2?

                    junction_tag_list = DatasetTag.get_by_tag_ids(tag_id_list)
                    dataset_id_list = [junction_tag.dataset_id for junction_tag in junction_tag_list]

                    # Filter with column in dataset ID thing? dataset_id_list

                    # condition_operator = in_op(File.id, new_filter_subquery)

                    local_tree.query_condition = condition_operator
                elif entity_type == 'file':
                    condition_operator = self.get_compare_op(compare_op)(value_1, str(value_2))
                    local_tree.query_condition = condition_operator
                else:
                    msg = f'Invalid entity type {entity_type}'
                    raise Exception(msg)
                self.conditions.append(compare_operator)
                return local_tree
            else:
                return

        else:
            self.log['error']['compare_expr'] = f"Invalid compare expression {str(args)}"

    def execute_query(self):
        """
            Entrypoint for building the end query. This uses the diffgram query
            object and accesses the tree so it can be visited.

            The main assumption here is that the tree will have the nodes that corresponds to the
            grammar defined in grammar.py
        :return:
        """
        if self.diffgram_query.tree:
            self.visit(self.diffgram_query.tree)
            if len(self.conditions) == 0 or len(self.log['error'].keys()) > 0 or not self.valid:
                logger.error('Invalid query. Please check your syntax and try again.')
                return None, self.log
        return self.final_query, self.log
