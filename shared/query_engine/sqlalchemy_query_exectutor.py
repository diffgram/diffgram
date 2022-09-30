from shared.query_engine.diffgram_query import DiffgramQuery
from shared.database.source_control.file import File
from shared.query_engine.diffgram_query_exectutor import BaseDiffgramQueryExecutor
from shared.shared_logger import get_shared_logger
from shared.regular import regular_log
from sqlalchemy.orm import aliased
from lark import Token
from shared.database.source_control.working_dir import WorkingDirFileLink
from shared.permissions.project_permissions import Project_permissions
from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement, CompareOperator, QueryEntity
from shared.query_engine.expressions.expressions import CompareExpression, AndExpression, OrExpression, \
    Factor

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
        self.and_expression = None
        self.or_expression = None
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
        if regular_log.log_has_error(self.log):
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
        if regular_log.log_has_error(self.log):
            return
        if len(args) == 1:
            local_tree = args[0]
            expressions = []
            if not self.or_expression:
                self.or_expression = OrExpression(expression_list = [])
            for child in local_tree.children:
                if hasattr(child, 'and_expression'):
                    expressions.append(child.and_expression)
                    self.or_expression.add_expression(child.and_expression)
                    # Reset and expressions list
                    self.and_expression = AndExpression(expression_list = [])
            local_tree.or_expression = self.or_expression
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
        if regular_log.log_has_error(self.log):
            return
        if len(args) == 1:

            local_tree = args[0]
            if not self.and_expression:
                self.and_expression = AndExpression(expression_list = [])
            expression_list = []
            for child in local_tree.children:
                if hasattr(child, 'factor'):
                    factor = child.factor
                    expression_list.append(factor.filter_value)
                    self.and_expression.add_expression(factor.filter_value)

            local_tree.and_expression = self.and_expression
        else:
            logger.error(f"Invalid child count for term. Must be 1 and is {len(args)}")
            self.log['error']['term'] = 'Invalid child count for factor. Must be 1'

    def factor(self, *args):
        if regular_log.log_has_error(self.log):
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
        values = []
        for token in local_tree.children:
            s = token.value
            try:
                int_val = int(s)
                values.append(int_val)
            except ValueError as verr:
                values.append(s)
        local_tree.value = values
        return local_tree

    def __build_query_element(self, token: Token) -> QueryElement:
        query_element, self.log = QueryElement.new(
            session = self.session,
            log = self.log,
            project_id = self.diffgram_query.project.id,
            token = token
        )
        return query_element

    def __validate_expression(self, compare_expression: CompareExpression):
        """
            This functions has the responsibility of checking that the expression operators
            are semantically valid for each of the different contexts.
        :param compare_expression:
        :return:
        """
        if compare_expression is None:
            error_string = "Error compare expression must not be None"
            logger.error(error_string)
            self.log['error']['compare_expr'] = error_string
            return False
        entity_type_left: QueryEntity = QueryEntity.new(compare_expression.left_raw)
        entity_type_right: QueryEntity = QueryEntity.new(compare_expression.right_raw)
        compare_op_token: Token = compare_expression.compare_op_raw
        if len(entity_type_left.full_key.split('.')) == 1:
            error_string = f"Error with entity: {entity_type_left.key}. Should specify the label name or global count"
            logger.error(error_string)
            self.log['error']['compare_expr'] = error_string
            return False

        if "file" in [entity_type_left, entity_type_right]:
            value_1 = self.__build_query_element(compare_expression.left_raw)
            value_2 = self.__build_query_element(compare_expression.right_raw)

            if compare_op_token.value not in ["=", "!="]:
                error_string = 'Invalid operator for file entity {}, valid operators are {}'.format(
                    compare_expression.operator_raw.value,
                    str(["=", "!="]))
                logger.error(error_string)
                self.log['error']['compare_expr'] = error_string
                return False

            if type(value_1) == int and type(value_2) == int:
                logger.error('Error: at least 1 value must be a label.')

        return True

    def init_compare_expression(self, children) -> CompareExpression:

        compare_expression, self.log = CompareExpression.new(
            session = self.session,
            left_raw = children[0],
            compare_op_raw = children[1],
            right_raw = children[2],
            project_id = self.diffgram_query.project.id,
            log = self.log
        )
        return compare_expression

    def compare_expr(self, *args):
        if len(self.log['error'].keys()) > 0:
            logger.error(self.log)
            return

        local_tree = args[0]
        if len(local_tree.children) != 3:
            self.log['error']['compare_expr'] = f"Invalid compare expression {str(args)}"

        children = local_tree.children

        compare_expression: CompareExpression = self.init_compare_expression(children)
        if regular_log.log_has_error(self.log):
            msg = f'Error creating expression {self.log}'
            logger.error(msg)
            return

        if not self.__validate_expression(compare_expression):
            return
        compare_expression.build_expression_subquery(session = self.session)
        if regular_log.log_has_error(self.log):
            msg = f'Error build_expression_subquery() {self.log}'
            logger.error(msg)
            return

        local_tree.compare_expression = compare_expression

        self.conditions.append(compare_expression)

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

        logger.info(str(self.final_query))

        return self.final_query, self.log
