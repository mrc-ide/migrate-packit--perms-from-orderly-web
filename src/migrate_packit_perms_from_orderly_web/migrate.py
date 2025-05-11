from migrate_packit_perms_from_orderly_web.orderly_web_permissions import OrderlyWebPermissions

something="hello"
another="there"

class Migrate:
    def __init__(self, ow: OrderlyWebPermissions):
        print("initialising migration...")
        self.ow = ow

    def migrate_permissions(self):
        print("doing migration")
        self.ow.authenticate()
        roles = self.ow.get_roles()
        users = self.ow.get_users()
