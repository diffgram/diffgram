from enum import Enum


class FilePermissions(Enum):
    file_view = 'file_view'
    file_edit = 'file_edit'
    file_delete = 'file_delete'


class FileDefaultRoles(Enum):
    """
        Warning! Changing any of these roles requires developer
        to create an alembic migration. Otherwise, default roles and
        stored db roles mapping won't match.
    """

    file_viewer = 'file_viewer'
    file_editor = 'file_editor'
    file_admin = 'file_admin'


FileRolesPermissions = {
    'file_viewer': [
        FilePermissions.file_view.value,
    ],
    'file_editor': [
        FilePermissions.file_view.value,
        FilePermissions.file_edit.value,
    ],
    'file_admin': [
        FilePermissions.file_view.value,
        FilePermissions.file_edit.value,
        FilePermissions.file_delete.value,
    ],
}
