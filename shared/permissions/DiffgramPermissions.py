from authzed.api.v1 import (
    CheckPermissionRequest,
    CheckPermissionResponse,
    Client,
    ObjectReference,
    SubjectReference,
)
from grpcutil import insecure_bearer_token_credentials

SCHEMA = """
definition diffgram/user {}

definition diffgram/project {
    relation reader: diffgram/user
    relation writer: diffgram/user
    relation super_admin: diffgram/user

    permission list = reader + writer + 
    permission create = writer
    permission delete = admin
    permission make_public = admin
}"""

class DiffgramPermissions:
    authzed_client: Client

    def __init__(self):
        client = Client(
            "localhost:50051",
            insecure_bearer_token_credentials("diffgram"),
        )
        self.authzed_client = client

    def create_default_roles(self):
        pass
