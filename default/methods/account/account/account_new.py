from methods.regular.regular_api import *

from shared.database.account.account import Account


def update_project_account(session,
                           account,
                           project):
    project.account = account
