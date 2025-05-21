from migrate_packit_perms_from_orderly_web.orderly_web_permissions import OrderlyWebPermissions
from migrate_packit_perms_from_orderly_web.packit_permissions import PackitPermissions

class Migrate:
    def __init__(self, orderly_web: OrderlyWebPermissions, packit: PackitPermissions):
        print("initialising migration...")
        self.orderly_web = orderly_web
        self.packit = packit

    def prepare_migrate(self):
        print("doing migration")
        self.orderly_web.authenticate()
        self.packit.authenticate(self.orderly_web.montagu_token)
        self.ow_roles = self.orderly_web.get_roles()
        self.ow_users = self.orderly_web.get_users()
        self.packit_users = self.packit.get_users()
        self.packit_roles = self.packit.get_roles()

        print("OW USERS")
        print(self.ow_users)

        # We may be doing this migration with some users already existing with permissions in Packit - in fact we need
        # at least one ADMIN user to run these migrations. We will leave any existing Packit ADMIN users alone. For any
        # Packit users who are not currently ADMIN, we will clear their existing roles and permissions and replace them
        # with corresponding roles and permissions from Packit. Similarly, we will clear out any existing non-ADMIN roles
        # before replacing them with migrated roles from OW.


        # PHASE 1: PREPARE PACKIT CHANGES
        # 1. Separate out existing admin and non-admin Packit get_users

        ow_user_emails = list(map(lambda u: u["email"], self.ow_users))
        print(f"OW users: {ow_user_emails}")
        self.packit_admin_users = []
        self.packit_users_to_delete = []
        self.packit_users_to_migrate = []
        for user in self.packit_users:
            username = user["username"]
            email = user["email"]
            admin_roles = list(filter(lambda r: r["name"] == "ADMIN", user["roles"]))
            if len(admin_roles):
                self.packit_admin_users.append(username)
                continue
            if email in ow_user_emails:
                self.packit_users_to_migrate.append(username)
            else:
                self.packit_users_to_delete.append(username)

        # We will create any OW users who do not yet exist in Packiit
        self.packit_users_to_create = []
        # keep a list of the full OW user objects we want to recreate as packit users
        self.ow_users_to_create_in_packit = []
        packit_user_emails = list(map(lambda u: u["email"], self.packit_users))
        for ow_user in self.ow_users:
            username = ow_user["username"]
            email = ow_user["email"]
            if email not in packit_user_emails:
                # TODO: What's going on with OW usernames? Why would they be "unknown"? Is this actually the case for
                # any of our real environments?
                # TODO: check with real names against last logged in time? Is this a real problem on prod for current-ish users?
                to_create = username if username != "unknown" else email
                self.packit_users_to_create.append(to_create)
                self.ow_users_to_create_in_packit.append(ow_user)


    def migrate_permissions(self):
        print("Doing migration!")

        # 2. Delete any non-admin Packit users who do not also exist in OW
        for username in self.packit_users_to_delete:
            print(f"Deleting user: {username}")
            self.packit.delete_user(username)

        # 3. For remaining Packit non-admin users, delete their existing (non-user) roles and directly held permissions

        # 4. In packit, create any OW users who do not yet exist.
        for ow_user in self.ow_users_to_create_in_packit:
            print(f"SEEMS IFFY: {ow_user}")
            keys = list(ow_user.keys())
            print(f"Keys are {keys}")
            email = ow_user["email"]
            username = ow_user["username"]
            display_name = ow_user["display_name"]
            username_to_create = username if username != "unknown" else email
            print(f"Creating user: {username_to_create} (email: {email}, display name: {display_name}) ")
            self.packit.create_user(username_to_create, email, display_name, [])

        # 5. Delete any non-ADMIN, non-user roles from Packit

        # 6. Migrate non-ADMIN roles from OW

        # 7. For Packit non-admin users, migrate their roles and permissions from OW
