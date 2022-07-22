from spicedb.api.v1 import Client, WriteSchemaRequest
from grpcutil import insecure_bearer_token_credentials
from spicedb.api.v1 import (
    Client,
    ObjectReference,
    Relationship,
    RelationshipUpdate,
    SubjectReference,
    WriteRelationshipsRequest,
    CheckPermissionRequest,
    CheckPermissionResponse
)


class DiffgramPermissions:
    authzed_client: Client

    def __init__(self):
        self.authzed_client = Client(
            "localhost:50051",
            # For SpiceDB behind TLS, use:
            # bearer_token_credentials("diffgram"),
            insecure_bearer_token_credentials("diffgram"),
        )

    def has_permission(self,
                       subject_type: str,
                       subject_id: str,
                       object_type: str,
                       object_id: str,
                       permission: str) -> [bool, str]:
        subject = SubjectReference(
            object = ObjectReference(
                object_type = subject_type,
                object_id = subject_id,
            )
        )
        object_ref = ObjectReference(object_type = object_type, object_id = object_id)

        resp = self.authzed_client.CheckPermission(
            CheckPermissionRequest(
                resource = object_ref,
                permission = permission,
                subject = subject,
            )
        )

        return resp.permissionship == CheckPermissionResponse.PERMISSIONSHIP_HAS_PERMISSION, resp.checked_at.token

    def add_permission(self, subject_type: str, subject_id: str, object_type: str, object_id: str, permission: str):
        resp = self.authzed_client.WriteRelationships(
            WriteRelationshipsRequest(
                updates = [
                    RelationshipUpdate(
                        operation = RelationshipUpdate.Operation.OPERATION_TOUCH,
                        relationship = Relationship(
                            resource = ObjectReference(object_type = object_type, object_id = object_id),
                            relation = permission,
                            subject = SubjectReference(
                                object = ObjectReference(
                                    object_type = subject_type,
                                    object_id = subject_id,
                                )
                            ),
                        ),
                    )
                ]
            )
        )
        return resp

    def test_rels(self):
        self.add_permission(
            subject_type = "diffgram/user",
            subject_id = "pablo",
            object_type = "diffgram/dataset",
            object_id = "1",
            permission = "reader"
        )
        self.add_permission(
            subject_type = "diffgram/user",
            subject_id = "anthony",
            object_type = "diffgram/dataset",
            object_id = "1",
            permission = "writer"
        )

        assert self.has_permission(
            subject_type = "diffgram/user",
            subject_id = "anthony",
            object_type = "diffgram/dataset",
            object_id = "1",
            permission = "write"
        )[0] == True
        assert self.has_permission(
            subject_type = "diffgram/user",
            subject_id = "anthony",
            object_type = "diffgram/dataset",
            object_id = "1",
            permission = "read"
        )[0] == True
        assert self.has_permission(
            subject_type = "diffgram/user",
            subject_id = "pablo",
            object_type = "diffgram/dataset",
            object_id = "1",
            permission = "write"
        )[0] == False

        print("AUTHZED PERMISSIONS SUCCESS!")
