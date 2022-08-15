from shared.query_engine.diffgram_query import DiffgramQuery
from shared.database.source_control.file import File
from shared.query_engine.diffgram_query_exectutor import BaseDiffgramQueryExecutor
from shared.shared_logger import get_shared_logger
from shared.regular import regular_log
from sqlalchemy.orm import aliased
from shared.database.source_control.working_dir import WorkingDirFileLink
from shared.permissions.project_permissions import Project_permissions
from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement
from shared.query_engine.sql_alchemy_query_elements.expressions import CompareExpression, AndExpression, OrExpression, Factor

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
        self.final_query = self.session.query(File).filter(
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
                or_expression: OrExpression = child.or_expression
                self.final_query = self.final_query.filter(
                    or_expression.sql_or_statement
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
            expressions = []
            for child in local_tree.children:
                if hasattr(child, 'and_expression'):
                    expressions.append(child.and_expression)
            or_expr = OrExpression(expression_list = expressions)
            local_tree.or_expression = or_expr
            return local_tree
        else:
            logger.error(f"Invalid child count for expr. Must be 1 and is {len(args)}")
            self.log['error']['expr'] = 'Invalid child count for factor. Must be 1'

    def term(self, *args) -> AndExpression:
        """
            The term rule should join one or more conditions in an AND statement.
        :param args:
        :return:
        """
        if len(self.log['error'].keys()) > 0:
            return
        if len(args) == 1:
            local_tree = args[0]
            expression = []
            for child in local_tree.children:
                if hasattr(child, 'factor'):
                    factor = child.factor
                    expression.append(factor.filter_value)
            and_expr = AndExpression(expression_list=expression)
            local_tree.and_expression = and_expr
        else:
            logger.error(f"Invalid child count for term. Must be 1 and is {len(args)}")
            self.log['error']['term'] = 'Invalid child count for factor. Must be 1'

    def factor(self, *args):
        if len(self.log['error'].keys()) > 0:
            return
        if len(args) == 1:
            local_tree = args[0]
            if len(local_tree.children) == 1:
                compare_expr = local_tree.children[0].compare_expression
                AliasFile = aliased(File)
                filter_value = File.id.in_(compare_expr.subquery)
                result = Factor(filter_value = filter_value)
                local_tree.factor = result
                return local_tree
            else:
                logger.error('Invalid child count for factor. Must be 1')
                self.log['error']['factor'] = 'Invalid child count for factor. Must be 1'

    def array(self, args):
        local_tree = args
        id_values = []
        for token in local_tree.children:
            s = token.value
            try:
                int_val = int(s)
                id_values.append(int_val)
            except ValueError as verr:
                id_values.append(s)
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
            sub_value = name_token.value.split('.')[1]
            if sub_value == "tag":
                value = "dataset_tag"
            else:
                value = "dataset"
        return value

    def __parse_value(self, token) -> QueryElement:
        """
            Transforms the token into an integer or appropriate diffgram value (instance count, issue count, etc)
        :param token:
        :return:
        """
        entity_type = self.__determine_entity_type(token)
        query_element, self.log = QueryElement.generate_query_element(
            session = self.session,
            log = self.log,
            project_id = self.diffgram_query.project.id,
            entity_type = entity_type,
            token = token
        )
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

    def compare_expr(self, *args) -> QueryElement:
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

                compare_operator = None
                compare_expression, self.log = CompareExpression.build_expression_from_entity_type(
                    session = self.session,
                    log = self.log,
                    project_id = self.diffgram_query.project.id,
                    entity_type = entity_type,
                    value_1 = value_1,
                    value_2 = value_2,
                    compare_op = compare_op
                )

                local_tree.compare_expression = compare_expression

                if len(self.log['error'].keys()) > 0:
                    msg = f'Error generating expression {self.log}'
                    logger.error(msg)

                self.conditions.append(compare_operator)
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
