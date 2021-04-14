# OPENCORE - ADD
from default.methods.regular.regular_api import *
from shared import database_setup_supporting	
from shared.helpers.performance import explain_postgres
from shared.database.attribute.attribute_template import Attribute_Template


def primary_key(id):
	with sessionMaker.session_scope() as session:
		query = session.query(Attribute_Template).filter(
				Attribute_Template.id == id)
		explain_results = session.execute(explain_postgres(query)).first()
		print(explain_results)


def foreign_key(group_id):
	with sessionMaker.session_scope() as session:
		query = session.query(Attribute_Template).filter(
				Attribute_Template.group_id == group_id)
		explain_results = session.execute(explain_postgres(query)).first()
		print(explain_results)

def run_with_explain(session, query):
	explain_results = session.execute(explain_postgres(query)).first()
	print(explain_results)



id = 484
primary_key(id)

group_id = 394
foreign_key(group_id)

"""
Without index
('Index Scan using attribute_template_pkey on attribute_template  (cost=0.27..8.29 rows=1 width=93) (actual time=0.051..0.051 rows=1 loops=1)',)
('Seq Scan on attribute_template  (cost=0.00..10.46 rows=2 width=93) (actual time=0.085..0.087 rows=3 loops=1)',)

With Index


"""""""""