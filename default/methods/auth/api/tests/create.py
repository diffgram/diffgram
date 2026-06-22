from methods.auth.api import new
from shared.helpers import sessionMaker

def test():
    """
    This function creates a new authentication object with the specified project string ID and permission level,
    and then prints out the serialized authentication object with its secret.
    
    Parameters:
    project_string_id (str): The unique string ID of the project associated with the authentication object.
    permission_level (str): The level of permission granted to the authentication object.
    
    The function uses the `sessionMaker` helper to create a new session, and then calls the `create` method of the `new`
    module from the `auth.api` package to create the authentication object. The authentication object is then serialized
    with its secret and printed to the console.
    """
    project_string_id = "sdk-test"
    permission_level = "Editor"
    with sessionMaker.session_scope() as session:
        auth = new.create(session, project_string_id, permission_level)
        print(auth.serialize_with_secret())
