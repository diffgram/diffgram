from authzed.api.v1 import (
    CheckPermissionRequest,
    CheckPermissionResponse,
    Client,
    ObjectReference,
    SubjectReference,
)
from grpcutil import insecure_bearer_token_credentials

client = Client(
    "localhost:50051",
    insecure_bearer_token_credentials("diffgram"),
)

emilia = SubjectReference(
    object=ObjectReference(
        object_type="blog/user",
        object_id="emilia",
    )
)
beatrice = SubjectReference(
    object=ObjectReference(
        object_type="blog/user",
        object_id="beatrice",
    )
)

post_one = ObjectReference(object_type="blog/post", object_id="1")

resp = client.CheckPermission(
    CheckPermissionRequest(
        resource=post_one,
        permission="read",
        subject=emilia,
    )
)
assert resp.permissionship == CheckPermissionResponse.PERMISSIONSHIP_HAS_PERMISSION

resp = client.CheckPermission(
    CheckPermissionRequest(
        resource=post_one,
        permission="write",
        subject=emilia,
    )
)
assert resp.permissionship == CheckPermissionResponse.PERMISSIONSHIP_HAS_PERMISSION

resp = client.CheckPermission(
    CheckPermissionRequest(
        resource=post_one,
        permission="read",
        subject=beatrice,
    )
)
assert resp.permissionship == CheckPermissionResponse.PERMISSIONSHIP_HAS_PERMISSION

resp = client.CheckPermission(
    CheckPermissionRequest(
        resource=post_one,
        permission="write",
        subject=beatrice,
    )
)
assert resp.permissionship == CheckPermissionResponse.PERMISSIONSHIP_NO_PERMISSION