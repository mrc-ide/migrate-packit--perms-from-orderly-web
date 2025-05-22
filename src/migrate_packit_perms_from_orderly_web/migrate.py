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



        # PHASE 1: PREPARE PACKIT CHANGES
        # 1. Separate out existing admin and non-admin Packit get_users
        clear_out_msg = "Clear out non-admin Packit users and roles before running migration."
        ow_user_emails = list(map(lambda u: u["email"], self.ow_users))
        print(f"OW users: {ow_user_emails}")
        self.packit_admin_users = []
        for user in self.packit_users:
            username = user["username"]
            email = user["email"]
            admin_roles = list(filter(lambda r: r["name"] == "ADMIN", user["roles"]))
            if len(admin_roles):
                self.packit_admin_users.append(username)
            else:
                raise Exception(f"Found non-ADMIN user {username} in Packit. {clear_out_msg}")

        self.packit_users_to_create = []
        # keep a list of the full OW user objects we want to recreate as packit users
        self.ow_users_to_create_in_packit = []
        # Match on email against existing Packit ADMIN users as OW can have username set to "unknown" if user has not logged in
        packit_user_emails = list(map(lambda u: u["email"], self.packit_users))
        for ow_user in self.ow_users:
            username = ow_user["username"]
            email = ow_user["email"]
            if email not in packit_user_emails:
                # TODO: What's going on with OW usernames? Why would they be "unknown"? Is this actually the case for
                # any of our real environments?
                # TODO: check with real names against last logged in time? Is this a real problem on prod for current-ish users?
                # This seems to only apply to users who have either never logged in to Montagu or not for many years - probably
                # not since OW was spun up. So I think the issue is that the Montagu user name is only transferred when
                # user actually logs in to Montagu.
                # This means that we're not doing a very realistic test if we don't have any migrating users who have Montagu
                # user names. Test for both! In our unit test - use OrderlyWebPermissions to log in to OW
                to_create = username if username != "unknown" else email
                self.packit_users_to_create.append(to_create)
                self.ow_users_to_create_in_packit.append(ow_user)

        # ROLES
        packit_non_admin_roles = list(filter(lambda r: r["name"] != "ADMIN" and not r["isUsername"], self.packit_roles))
        if len(packit_non_admin_roles):
            raise Exception(f"Found non-ADMIN roles in Packit: {packit_non_admin_roles}. {clear_out_msg}")
        self.ow_roles_to_create_in_packit = list(filter(lambda r: r["name"] != "Admin", self.ow_roles))
        self.packit_roles_to_create = list(map(lambda r: r["name"], self.ow_roles_to_create_in_packit))


    def migrate_permissions(self):
        print("Doing migration!")

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

        # 5. Delete any non-ADMIN, non-user roles from Packit which do not exist in OW

        # 6. Migrate non-ADMIN roles from OW

        # 7. For Packit non-admin users, migrate their roles and permissions from OW
