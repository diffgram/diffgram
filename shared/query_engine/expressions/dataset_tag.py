from shared.query_engine.expressions.expressions import CompareExpression
from sqlalchemy.orm.session import Session
from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement
from shared.database.source_control.file import File
from shared.database.source_control.working_dir import WorkingDirFileLink
from sqlalchemy.orm import aliased
from sqlalchemy.sql import Selectable
from shared.database.tag.tag import Tag, DatasetTag


class DatasetTagCompareExpression(CompareExpression):

    def build_expression_subquery(self, session):
        query_op: QueryElement = self.query_op
        scalar_op: QueryElement = self.scalar_op

        # Get Values from query elements
        raw_scalar_value = scalar_op.raw_value
        sql_column = query_op.column
        sql_compare_operator = self.operator.operator_value
        tag_id_list = []

        for tag_name in raw_scalar_value:
            tag_name = tag_name.strip('\"')
            tag_name = tag_name.strip('\'')
            tag = Tag.get(session = session, name = tag_name, project_id = self.project_id)
            if tag:
                tag_id_list.append(tag.id)

        AliasFile = aliased(File)
        new_filter_subquery = session.query(AliasFile.id) \
            .join(WorkingDirFileLink, WorkingDirFileLink.file_id == File.id) \
            .join(DatasetTag, DatasetTag.dataset_id == WorkingDirFileLink.working_dir_id) \
            .filter(sql_compare_operator(sql_column, tag_id_list)).subquery(name = "ds_tag_compare")

        self.subquery = new_filter_subquery
