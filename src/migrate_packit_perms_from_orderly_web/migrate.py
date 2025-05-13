from migrate_packit_perms_from_orderly_web.orderly_web_permissions import OrderlyWebPermissions
from migrate_packit_perms_from_orderly_web.packit_permissions import PackitPermissions

class Migrate:
    def __init__(self, orderly_web: OrderlyWebPermissions, packit: PackitPermissions):
        print("initialising migration...")
        self.orderly_web = orderly_web
        self.packit = packit

    def migrate_permissions(self):
        print("doing migration")
        self.orderly_web.authenticate()
        self.packit.authenticate(self.orderly_web.montagu_token)
        roles = self.orderly_web.get_roles()
        users = self.orderly_web.get_users()
