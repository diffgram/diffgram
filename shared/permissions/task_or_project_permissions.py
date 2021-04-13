# OPENCORE - ADD
from functools import wraps
from werkzeug.exceptions import Forbidden
from shared.permissions.task_permissions import Permission_Task
from shared.permissions.project_permissions import Project_permissions


class PermissionTaskOrProject:

    @staticmethod
    def by_task_or_project_wrapper(
            apis_user_list,
            apis_project_list = [],
            roles = []):
        """
            Validates permissions for project or fot task_id depending on which one is available
            on kwargs.
            This is just the wrapper
        """

        def wrapper(func):
            @wraps(func)
            def inner(*args, **kwds):
                task_id = kwds.get('task_id', None)
                project_string_id = kwds.get('project_string_id', None)
                
                by_task_or_project_result = PermissionTaskOrProject.by_task_or_project(
                    apis_user_list = apis_user_list,
                    apis_project_list = apis_project_list,
                    roles = roles,
                    task_id = task_id,
                    project_string_id = project_string_id
                    )

                if by_task_or_project_result is True:
                    return func(*args, **kwds)

                raise Forbidden("No access.")

            return inner

        return wrapper


    def by_task_or_project(
            apis_user_list,
            apis_project_list: list = [],
            roles: list = [],
            task_id: int = None,
            project_string_id: str = None
        ):

        task_permissions = None
        project_permissions = None

        if project_string_id:
            project_permissions = Project_permissions.by_project_core(
                project_string_id = project_string_id,
                Roles = roles,
                apis_project_list = apis_project_list,
                apis_user_list = apis_user_list
            )
            if project_permissions is True:
                return True
        if task_id:
            task_permissions = Permission_Task.by_task_id_core(task_id = task_id)
            if task_permissions is True:
                return True

        return False