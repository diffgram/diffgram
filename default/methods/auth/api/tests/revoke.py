
from methods.auth.api import revoke
from shared.helpers import sessionMaker


def test():

	project_string_id = ""
	client_id = ""
	#client_id = None
	#client_id = "123"

	with sessionMaker.session_scope() as session:
		result = revoke.by_client_id(session, project_string_id, client_id)
		print(result)
