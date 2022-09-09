from shared.database.auth.api import Auth_api
from shared.database.auth.member import Member
from shared.database.project import Project
import random
import string
from shared.database import hashing_functions
from shared.regular import regular_methods
from shared.permissions.project_permissions import Project_permissions
def create_random_string(length):
    return ''.join(random.choice(string.ascii_lowercase + \
                                 string.digits) for x in range(length))


def add_auth_to_session(session, user):
    cookie_hash = hashing_functions.make_secure_val(user.id)
    # Set the user session for request permissions.
    session['user_id'] = cookie_hash
    return session
def create_project_auth(project, session, role = "Editor"):
    auth = Auth_api()
    session.add(auth)

    member = Member()
    session.add(member)
    session.flush()
    member.kind = "api"



    member.auth_api = auth
    auth.member_id = member.id


    auth.permission_level = role
    auth.project_string_id = project.project_string_id

    auth.is_live = True

    if auth.is_live == True:
        auth.client_id = "LIVE__"
    else:
        auth.client_id = "TEST__"

    auth.client_id += create_random_string(length=20)
    auth.client_secret = create_random_string(length=60)

    auth.project_id = project.id

    regular_methods.commit_with_rollback(session)
    Project_permissions.assign_project_roles(
        session = session,
        project = project,
        member_id = auth.member_id,
        role_name = role.lower(),
        log = {}
    )
    regular_methods.commit_with_rollback(session)
    return auth
