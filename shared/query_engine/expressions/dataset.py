from shared.query_engine.expressions.expressions import CompareExpression
from sqlalchemy.orm.session import Session
from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement
from shared.database.source_control.file import File
from shared.database.source_control.working_dir import WorkingDir
from shared.database.project import Project
from sqlalchemy.orm import aliased
from sqlalchemy.sql import Selectable
from sqlalchemy.sql.expression import and_, or_


class DatasetCompareExpression(CompareExpression):

    def build_expression_subquery(self, session) -> Selectable:
        query_op: QueryElement = self.query_op
        scalar_op: QueryElement = self.scalar_op

        # Get Values from query elements
        raw_scalar_value = scalar_op.raw_value
        sql_column = query_op.column
        sql_compare_operator = self.operator.operator_value

        can_view = WorkingDir.can_member_view_datasets(session = session, project = self.project, dataset_ids = raw_scalar_value, member = self.member)
        
        if not can_view:
            # TODO: How to handle this better? Should we throw? 
            # # Also seems like an awkard place to do validation in general, is there a better place? Difficulty is that we need access to the dataset ids to do this validation.
            self.log['error']['unauthorized'] = f'You do not have access to these datasets'

        AliasFile = aliased(File)
        # self.subquery = session.query(AliasFile.id) \
        #     .join(WorkingDirFileLink, WorkingDirFileLink.file_id == File.id) \
        #     .filter(sql_compare_operator(sql_column, raw_scalar_value),
        #             File.project_id == self.project_id,
        #             File.state != 'removed').subquery(name = "ds_compare")
        self.expression = sql_compare_operator(sql_column, raw_scalar_value)
        return self.expression
