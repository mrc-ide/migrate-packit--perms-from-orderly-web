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
        ow_roles = self.orderly_web.get_roles()
        ow_users = self.orderly_web.get_users()
        packit_users = self.packit.get_users()
        packit_roles = self.packit.get_roles()

        # We may be doing this migration with some users already existing with permissions in Packit - in fact we need
        # at least one ADMIN user to run these migrations. We will leave any existing Packit ADMIN users alone. For any
        # Packit users who are not currently ADMIN, we will clear their existing roles and permissions and replace them
        # with corresponding roles and permissions from Packit. Similarly, we will clear out any existing non-ADMIN roles
        # before replacing them with migrated roles from OW.

        # 1. Separate out existing admin and non-admin Packit get_users

        # 2. Delete any non-admin Packit users who do not also exist in OW

        # 3. For remaining Packit non-admin users, delete their existing (non-user) roles and directly held permissions

        # 4. In packit, create any OW users who do not yet exist.

        # 5. Delete any non-ADMIN, non-user roles from Packit

        # 6. Migrate non-ADMIN roles from OW

        # 7. For Packit non-admin users, migrate their roles and permissions from OW
