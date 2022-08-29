from enum import Enum


class DatasetPermissions(Enum):
    dataset_view = 'dataset_view'
    dataset_edit = 'dataset_edit'
    dataset_delete = 'dataset_delete'
    dataset_list = 'dataset_list'
    dataset_invite_user = 'dataset_invite_user'


class DatasetDefaultRoles(Enum):
    viewer = 'viewer'
    editor = 'editor'
    admin = 'admin'


class DatasetRolesPermissions(Enum):
    viewer = [
        DatasetPermissions.dataset_view.value,
    ]
    editor = [
        DatasetPermissions.dataset_view.value,
        DatasetPermissions.dataset_edit.value,
    ]
    admin = [
        DatasetPermissions.dataset_invite_user.value,
        DatasetPermissions.dataset_invite_user.value,
    ]

