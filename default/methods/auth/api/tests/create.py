
from methods.auth.api import new
from shared.helpers import sessionMaker


def test():

	project_string_id = "sdk-test"
	permission_level = "Editor"
	with sessionMaker.session_scope() as session:
		auth = new.create(session, project_string_id, permission_level)
		print(auth.serialize_with_secret())


