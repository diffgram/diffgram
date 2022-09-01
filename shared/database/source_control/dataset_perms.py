from enum import Enum


class DatasetPermissions(Enum):
    dataset_view = 'dataset_view'
    dataset_edit = 'dataset_edit'
    dataset_delete = 'dataset_delete'
    dataset_list = 'dataset_list'
    dataset_invite_user = 'dataset_invite_user'


class DatasetDefaultRoles(Enum):
    """
        Warning! Changing any of these roles requires developer
        to create an alembic migration. Otherwise, default roles and
        stored db roles mapping won't match.
    """

    dataset_viewer = 'dataset_viewer'
    dataset_editor = 'dataset_editor'
    dataset_admin = 'dataset_admin'


DatasetRolesPermissions = {
    'dataset_viewer': [
        DatasetPermissions.dataset_view.value,
    ],
    'dataset_editor': [
        DatasetPermissions.dataset_view.value,
        DatasetPermissions.dataset_edit.value,
    ],
    'dataset_admin': [
        DatasetPermissions.dataset_invite_user.value,
        DatasetPermissions.dataset_invite_user.value,
    ],
}
