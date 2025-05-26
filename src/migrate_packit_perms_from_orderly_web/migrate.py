from migrate_packit_perms_from_orderly_web.orderly_web_permissions import OrderlyWebPermissions
from migrate_packit_perms_from_orderly_web.packit_permissions import PackitPermissions
from migrate_packit_perms_from_orderly_web.map_permissions import MapPermissions

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

        # REPORT VERSIONS
        self.published_report_versions = self.orderly_web.get_published_report_versions()

        map_perms = MapPermissions(self.published_report_versions)
        self.packit_users_to_create = {}
        # keep a list of the full OW user objects we want to recreate as packit users
        #self.ow_users_to_create_in_packit = []
        # Match on email against existing Packit ADMIN users as OW can have username set to "unknown" if user has not logged in
        packit_user_emails = list(map(lambda u: u["email"], self.packit_users))
        for ow_user in self.ow_users:
            username = ow_user["username"]
            email = ow_user["email"]
            if email not in packit_user_emails:
                # NB Some usernames in OW are "unknown" for users who have never logged in. We do not migrate perms in
                # case as it won't work without the Montagu user name
                #to_create = username if username != "unknown" else email
                if username == "unknown":
                    print(f"Not migrating never logged in user: {email}")
                else:
                    roles = map(lambda u: u["source"], ow_user["role_permissions"])
                    roles = list(set(roles)) # dedupe

                    packit_perms = map_perms.map_ow_permissions_to_packit_permissions(ow_user["direct_permissions"])
                    self.packit_users_to_create[username] = {
                        "email": ow_user["email"],
                        "display_name": ow_user["display_name"],
                        "direct_permissions": packit_perms,
                        "roles": roles
                    }

        # ROLES
        packit_non_admin_roles = list(filter(lambda r: r["name"] != "ADMIN" and not r["isUsername"], self.packit_roles))
        if len(packit_non_admin_roles):
            raise Exception(f"Found non-ADMIN roles in Packit: {packit_non_admin_roles}. {clear_out_msg}")
        ow_roles_to_create_in_packit = list(filter(lambda r: r["name"] != "Admin", self.ow_roles))

        self.packit_roles_to_create = {}
        for ow_role in ow_roles_to_create_in_packit:
            role_name = ow_role["name"]
            #print(f"MAPPING FOR {ow_role}")
            packit_perms = map_perms.map_ow_permissions_to_packit_permissions(ow_role["permissions"])
            self.packit_roles_to_create[role_name] = packit_perms

    def migrate_permissions(self):
        # 1. Create roles, and set their permissions - we do this in a separate step because only global perms can be
        # specified on role creation
        for role, permissions in self.packit_roles_to_create.items():
            print(f"Creating role: {role}")
            self.packit.create_role(role)
            print(f"Setting permissions on role {role}: {permissions}")
            self.packit.set_permissions_on_role(role, permissions)

        # 2. Create users, with their roles, and set direct permissions
        for username, user_details in self.packit_users_to_create.items():
            email = user_details["email"]
            display_name = user_details["display_name"]
            roles = user_details["roles"]
            print(f"Creating user: {username} (email: {email}, display name: {display_name}, roles: {roles}) ")
            self.packit.create_user(username, email, display_name, roles)
            permissions = user_details["direct_permissions"]
            print(f"Setting permissions on user {username}: {permissions}")
            self.packit.set_permissions_on_role(username, permissions)



