import os
from migrate_packit_perms_from_orderly_web.orderly_web_permissions import OrderlyWebPermissions
from migrate_packit_perms_from_orderly_web.packit_permissions import PackitPermissions
from migrate_packit_perms_from_orderly_web.map_permissions import MapPermissions
from migrate_packit_perms_from_orderly_web.permissions_csv_file import PermissionsCsvFile
from migrate_packit_perms_from_orderly_web.user_roles_csv_file import UserRolesCsvFile

class Migrate:
    def __init__(self, orderly_web: OrderlyWebPermissions, packit: PackitPermissions):
        self.orderly_web = orderly_web
        self.packit = packit

    def prepare_migrate(self):
        self.orderly_web.authenticate()
        self.packit.authenticate(self.orderly_web.montagu_token)
        self.ow_roles = self.orderly_web.get_roles()
        self.ow_users = self.orderly_web.get_users()
        self.packit_users = self.packit.get_users()
        self.packit_roles = self.packit.get_roles()

        # Refuse to run migration if there are any non-ADMIN users in Packit
        clear_out_msg = "Clear out non-admin Packit users and roles before running migration."
        ow_user_emails = list(map(lambda u: u["email"], self.ow_users))
        self.packit_admin_users = []
        for user in self.packit_users:
            username = user["username"]
            email = user["email"]
            admin_roles = list(filter(lambda r: r["name"] == "ADMIN", user["roles"]))
            if len(admin_roles):
                self.packit_admin_users.append(username)
            else:
                raise Exception(f"Found non-ADMIN user {username} in Packit. {clear_out_msg}")

        # Get all published report versions
        self.published_report_versions = self.orderly_web.get_published_report_versions()
        nonexistent_packets = self.packit.check_packets_exist(self.published_report_versions)
        if (len(nonexistent_packets)):
            print(f"WARNING: The following {len(nonexistent_packets)} expected packets do not exist, and will not have related permissions created. "
            + f"There may have been an issue with migrating packets from OrderlyWeb.\n {nonexistent_packets}")

        map_perms = MapPermissions(self.published_report_versions)

        # USERS
        self.packit_users_to_create = {}
        # Match on email against existing Packit ADMIN users as OW can have username set to "unknown" if user has not logged in
        packit_user_emails = list(map(lambda u: u["email"], self.packit_users))
        user_perms_csv_file = PermissionsCsvFile()
        user_roles_csv_file = UserRolesCsvFile()
        for ow_user in self.ow_users:
            username = ow_user["username"]
            email = ow_user["email"]
            if email not in packit_user_emails:
                # NB Some usernames in OW are "unknown" for users who have never logged in. We do not migrate perms in
                # case as it won't work without the Montagu user name
                if username == "unknown":
                    print(f"Not migrating never logged in user: {email}")
                else:
                    # Use "source" in "role_permissions" to determine which roles a user belong to - but need to be careful
                    # as "source" sometimes contains multiple role names, separated by ", "
                    roles = []
                    for perm in ow_user["role_permissions"]:
                        sources = perm["source"].split(", ")
                        for source in sources:
                            # The Admin role in Packit is SHOUTY
                            if source.upper() == "ADMIN":
                                source = "ADMIN"
                            if source not in roles:
                                roles.append(source)
                                user_roles_csv_file.add_row(username, source)

                    packit_perms = map_perms.map_ow_permissions_to_packit_permissions(
                        ow_user["direct_permissions"],
                        username,
                        user_perms_csv_file
                    )
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
        role_perms_csv_file = PermissionsCsvFile()
        for ow_role in ow_roles_to_create_in_packit:
            role_name = ow_role["name"]
            packit_perms = map_perms.map_ow_permissions_to_packit_permissions(
                ow_role["permissions"],
                role_name,
                role_perms_csv_file
            )
            self.packit_roles_to_create[role_name] = packit_perms

        # write out csv files
        print("Writing full details to /csv")
        dir = "csv"
        if not os.path.exists(dir):
            os.makedirs(dir)
        user_perms_csv_file.write(f"{dir}/user_direct_perms.csv")
        role_perms_csv_file.write(f"{dir}/role_perms.csv")
        user_roles_csv_file.write(f"{dir}/user_roles.csv")
        print("Finished writing csv files")


    def migrate_permissions(self):
        # 1. Create roles, and set their permissions - we do this in a separate step because only global perms can be
        # specified on role creation
        for role, permissions in self.packit_roles_to_create.items():
            print(f"Creating role: {role}")
            self.packit.create_role(role)
            print(f"Setting permissions on role {role}: {len(permissions)} permissions")
            self.packit.set_permissions_on_role(role, permissions)

        # 2. Create users, with their roles, and set direct permissions
        for username, user_details in self.packit_users_to_create.items():
            email = user_details["email"]
            display_name = user_details["display_name"]
            roles = user_details["roles"]
            print(f"Creating user: {username} (email: {email}, display name: {display_name}, roles: {roles}) ")
            self.packit.create_user(username, email, display_name, roles)
            permissions = user_details["direct_permissions"]
            print(f"Setting permissions on user {username}: {len(permissions)} permissions")
            self.packit.set_permissions_on_role(username, permissions)


def get_displayable_permissions(permissions):
    # give some feedback to user on what permissions will be created for a user or role without overwhelming the console
    # if there are multiple packet-specific permissions, show first 5 then "and N more"
    global_perms = []
    packet_read_to_display = []
    packet_read_overspill_count = 0
    for perm in permissions:
        packet_id = perm["packetId"]
        name = perm["permission"]
        if packet_id is None:
            global_perms.append(name)
        else:
            if name != "packet.read":
                print(f"Unexpected scoped permission: {permission}")
            elif len(packet_read_to_display) < 5:
                packet_read_to_display.append(packet_id)
            else:
                packet_read_overspill_count = packet_read_overspill_count + 1
    global_display = "" if len(global_perms) == 0 else f"global: {global_perms} "
    packet_scoped_display = "" if len(packet_read_to_display) == 0 else f"scoped packet.read: {packet_read_to_display}"
    overspill_display = "" if packet_read_overspill_count == 0 else f" and {packet_read_overspill_count} more"
    return f"{global_display}{packet_scoped_display}{overspill_display}"


