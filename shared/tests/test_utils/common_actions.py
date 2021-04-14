# OPENCORE - ADD
from shared.database.auth.api import Auth_api
from shared.database.auth.member import Member
from shared.database.project import Project
import random
import string
from shared.database import hashing_functions

def create_random_string(length):
    return ''.join(random.choice(string.ascii_lowercase + \
                                 string.digits) for x in range(length))


def add_auth_to_session(session, user):
    cookie_hash = hashing_functions.make_secure_val(user.id)
    # Set the user session for request permissions.
    session['user_id'] = cookie_hash
    return session
def create_project_auth(project, session):
    auth = Auth_api()
    session.add(auth)

    member = Member()
    session.add(member)
    member.kind = "api"



    member.auth_api = auth
    auth.member_id = member.id

    auth.permission_level = 'Editor'
    auth.project_string_id = project.project_string_id
    auth.is_live = True

    if auth.is_live == True:
        auth.client_id = "LIVE__"
    else:
        auth.client_id = "TEST__"

    auth.client_id += create_random_string(length=20)
    auth.client_secret = create_random_string(length=60)

    auth.project_id = project.id

    # Careful we are placing this in the member not the auth
    # for now...
    session.commit()
    return auth
