# OPENCORE - ADD
from default.methods.regular.regular_api import *
from shared import database_setup_supporting	
from shared.helpers.performance import explain_postgres
from shared.database.input import Input


def foreign_key(processing_deferred):
	with sessionMaker.session_scope() as session:
		query = session.query(Input).filter(
				Input.processing_deferred == processing_deferred)
		explain_results = session.execute(explain_postgres(query)).first()
		print(explain_results)

def run_with_explain(session, query):
	explain_results = session.execute(explain_postgres(query)).first()
	print(explain_results)


foreign_key(processing_deferred = True)

"""

"""""""""