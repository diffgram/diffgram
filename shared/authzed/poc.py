from authzed.api.v1 import Client, WriteSchemaRequest
from grpcutil import insecure_bearer_token_credentials
from authzed.api.v1 import (
    Client,
    ObjectReference,
    Relationship,
    RelationshipUpdate,
    SubjectReference,
    WriteRelationshipsRequest,
)

SCHEMA = """definition blog/user {}

definition blog/post {
    relation reader: blog/user
    relation writer: blog/user

    permission read = reader + writer
    permission write = writer
}"""

client = Client(
    "localhost:50051",
    # For SpiceDB behind TLS, use:
    # bearer_token_credentials("diffgram"),
    insecure_bearer_token_credentials("diffgram"),
)


def write_schema():
    resp = client.WriteSchema(WriteSchemaRequest(schema = SCHEMA))


def write_rel():
    resp = client.WriteRelationships(
        WriteRelationshipsRequest(
            updates = [
                # Emilia is a Writer on Post 1
                RelationshipUpdate(
                    operation = RelationshipUpdate.Operation.OPERATION_CREATE,
                    relationship = Relationship(
                        resource = ObjectReference(object_type = "blog/post", object_id = "1"),
                        relation = "writer",
                        subject = SubjectReference(
                            object = ObjectReference(
                                object_type = "blog/user",
                                object_id = "emilia",
                            )
                        ),
                    ),
                ),
                # Beatrice is a Reader on Post 1
                RelationshipUpdate(
                    operation = RelationshipUpdate.Operation.OPERATION_CREATE,
                    relationship = Relationship(
                        resource = ObjectReference(object_type = "blog/post", object_id = "1"),
                        relation = "reader",
                        subject = SubjectReference(
                            object = ObjectReference(
                                object_type = "blog/user",
                                object_id = "beatrice",
                            )
                        ),
                    ),
                ),
            ]
        )
    )

    print(resp.written_at.token)
