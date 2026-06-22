from methods.auth.api import revoke
from shared.helpers import sessionMaker

def test():
    # This function tests the revoke.by_client_id function using a specific project string ID and client ID

    # Set the project string ID to an empty string
    project_string_id = ""

    # Set the client ID to an empty string (this could be changed to a specific client ID for testing)
    client_id = ""
    #client_id = None  # This would result in no client ID being passed to the revoke.by_client_id function
    #client_id = "123"  # This would set the client ID to the string value "123" for testing

    # Create a session using the sessionMaker helper function
    with sessionMaker.session_scope() as session:
        # Call the revoke.by_client_id function, passing in the session, project string ID, and client ID
        result = revoke.by_client_id(session, project_string_id, client_id)

        # Print the result of the revoke.by_client_id function
        print(result)
