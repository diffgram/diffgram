from enum import Enum


class ProjectPermissions(Enum):
    project_view = 'project_view'
    project_edit = 'project_edit'
    project_delete = 'project_delete'


class ProjectDefaultRoles(Enum):
    """
        Warning! Changing any of these roles requires developer
        to create an alembic migration. Otherwise, default roles and
        stored db roles mapping won't match.
    """

    viewer = 'viewer'
    editor = 'editor'
    admin = 'admin'
    annotator = 'annotator'


ProjectRolesPermissions = {
    'viewer': [
        ProjectPermissions.project_view.value,
    ],
    'annotator': [
        ProjectPermissions.project_view.value,
        ProjectPermissions.project_edit.value,
    ],
    'editor': [
        ProjectPermissions.project_view.value,
        ProjectPermissions.project_edit.value,
    ],
    'admin': [
        ProjectPermissions.project_view.value,
        ProjectPermissions.project_edit.value,
        ProjectPermissions.project_delete.value,
    ],
}
