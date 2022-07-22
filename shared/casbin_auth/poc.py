import casbin
from shared.settings import settings
import casbin_sqlalchemy_adapter
from pathlib import Path

file_path = Path(__file__).resolve().parent
print('asdasd', file_path)
class DiffgramPermissions:
    enforcer: casbin.Enforcer

    def __init__(self):
        adapter = casbin_sqlalchemy_adapter.Adapter(settings.DATABASE_URL)
        self.enforcer = casbin.Enforcer(f"{file_path}/model.conf", adapter)
        self.role_manager = self.enforcer.get_role_manager()

    def test_file_relations(self):
        # 1. Configure Roles
        # Here user can be a user ID or Role
        self.enforcer.add_policy("dataset:viewer", "dataset:1", "view")
        self.enforcer.add_policy("dataset:editor", "dataset:1", "view")
        self.enforcer.add_policy("dataset:editor", "dataset:1", "edit")

        # 2. Assign Roles
        self.enforcer.add_role_for_user("alice", "dataset:viewer")
        self.enforcer.add_role_for_user("bob", "dataset:viewer")

        # 3. Set inheritance relations
        self.role_manager.add_link("dataset:1:viewer", "file:1:viewer", "g1")
        self.role_manager.add_link("dataset:1:viewer", "file:2:viewer", "g1")
        self.role_manager.add_link("dataset:1:viewer", "file:3:viewer", "g1")

        assert self.enforcer.enforce("alice", "dataset:1", "view") == True
        assert self.enforcer.enforce("alice", "dataset:1", "edit") == False

        print('CASBIN ASSERTIONS SUCCESS :) ')