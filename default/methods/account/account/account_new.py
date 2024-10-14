from methods.regular import regular_api
from shared.database.account import Account
from shared.database.project import Project

def update_project_account(session, account_id, project_id):
    account = Account.get_by_id(session, account_id)
    if not account:
        return None

    project = Project.get_by_id(session, project_id)
    if not project:
        return None

    project.account = account
    session.commit()

    regular_api.log_activity(session, account, f'updated account for project {project.name}')
    return project


from methods.regular import regular_api
from shared.database.account import Account
from shared.database.project import Project

def update_project_account(session, account_id, project_id):
    """
    Updates the account for a given project.

    Args:
        session (Session): The database session.
        account_id (int): The ID of the account.
        project_id (int): The ID of the project.

    Returns:
        Project: The updated project object.
    """
    account = Account.get_by_id(session, account_id)
    if not account:
        return None

    project = Project.get_by_id(session, project_id)
    if not project:
        return None

    project.account = account
    session.commit()

    regular_api.log_activity(session, account, f'updated account for project {project.name}')
    return project
