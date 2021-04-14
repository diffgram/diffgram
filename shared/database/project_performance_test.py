# OPENCORE - ADD
from default.methods.regular.regular_api import *
from shared import database_setup_supporting	
from shared.helpers.performance import explain_postgres
from shared.database.video.sequence import Sequence


def primary_key(project_id):
	with sessionMaker.session_scope() as session:
		query = session.query(Project).filter(
				Project.id == project_id)
		explain_results = session.execute(explain_postgres(query)).first()
		print(explain_results)


def foreign_key(project_string_id):
	with sessionMaker.session_scope() as session:
		query = session.query(Project).filter(
				Project.project_string_id == project_string_id)
		explain_results = session.execute(explain_postgres(query)).first()
		print(explain_results)

def run_with_explain(session, query):
	explain_results = session.execute(explain_postgres(query)).first()
	print(explain_results)



project_id = 1625
primary_key(project_id)

project_string_id = "sample_project_48e7003e-2b24-40ec-9786-70d67fb66360"
foreign_key(project_string_id)

"""
Without index
('Index Scan using project_pkey on project  (cost=0.28..8.29 rows=1 width=429) (actual time=0.034..0.035 rows=1 loops=1)',)
('Seq Scan on project  (cost=0.00..118.24 rows=1 width=429) (actual time=0.677..1.246 rows=1 loops=1)',)

With Index

('Index Scan using project_pkey on project  (cost=0.28..8.29 rows=1 width=429) (actual time=0.035..0.036 rows=1 loops=1)',)
('Index Scan using index__project_string_id on project  (cost=0.00..8.02 rows=1 width=429) (actual time=0.066..0.066 rows=1 loops=1)',

1.246 vs 0.066   19x improvement

"""""""""