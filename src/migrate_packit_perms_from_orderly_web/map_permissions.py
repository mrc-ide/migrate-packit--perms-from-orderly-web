REPORTS_READ = "reports.read"
REPORTS_REVIEW = "reports.review"

OUTPACK_READ = "outpack.read"
PACKET_READ = "packet.read"

def unpack_ow_perm(ow_perm):
    return ow_perm["name"], ow_perm["scope_prefix"], ow_perm["scope_id"]

def is_reviewer(ow_perms):
    # util to check if user with these perms is a reviewer - we assume any review perm implies global review
    for ow_perm in ow_perms:
        name, prefix, id = unpack_ow_perm(ow_perm)
        if name == REPORTS_REVIEW:
            return True
    return False

def is_global_reader(ow_perms):
    # util to check if user with these perms has global read permission
    for ow_perm in ow_perms:
        name, prefix, id = unpack_ow_perm(ow_perm)
        if name == REPORTS_READ and prefix is None:
            return True
    return False

def build_packit_perm(name, packet_id = None):
    return {
        "permission": name,
        "packetId": packet_id,
        "packetGroupId": None,
        "tagId": None
    }

class MapPermissions:
    def __init__(self, published_report_versions):
        self.published_report_versions = published_report_versions

    def append_permission(self, permission_source, permission):
        self._packit_perms.append(permission)
        self._permissions_csv_file.add_row(self._permission_owner, permission_source, permission["permission"], permission["packetId"])

    def append_packet_read_perms_for_published_report_versions(self, report_name, permission_source):
        for version in self.published_report_versions[report_name]:
            self.append_permission(permission_source, build_packit_perm(PACKET_READ, version))

    def map_ow_permissions_to_packit_permissions(self, ow_perms, permission_owner, permissions_csv_file):
        # reports.run => packet.run, outpack.read
        # users.manage => user.manage
        # reports.review => packet.read (global), packet.manage (global), outpack.read
        # reports.read (global) => packet.read (packet) for all published versions
        #                            (if not reviewer who will already be getting global read)
        # reports.read (report) => packet.read (packet) for all published versions in that report
        #                            (if not reviewer or global reader who will already be getting all relevant read perms)
        # Notes:
        # - OW supports report-level review permission but in practice this is a global perm, so we only check for global here
        # - Similarly, version-level read access is not being used in practice so we only process global and report level read perm
        # - We are ignoring pinned reports manage permission as this is not implemented as a user feature in packit yet - we
        #   will assign this perm as required.

        self._packit_perms = []
        self._permission_owner = permission_owner
        self._permissions_csv_file = permissions_csv_file
        outpack_read_already_granted = False
        for ow_perm in ow_perms:
            ow_perm_name,  ow_perm_scope_prefix, ow_perm_scope_id = unpack_ow_perm(ow_perm)

            match ow_perm_name:
                case "reports.run":
                    self.append_permission(ow_perm_name, build_packit_perm("packet.run"))
                    if not outpack_read_already_granted:
                        self.append_permission(ow_perm_name, build_packit_perm(OUTPACK_READ))
                        outpack_read_already_granted = True
                case "users.manage":
                    self.append_permission(ow_perm_name, build_packit_perm("user.manage"))
                case "reports.review":
                    self.append_permission(ow_perm_name, build_packit_perm(PACKET_READ))
                    self.append_permission(ow_perm_name, build_packit_perm("packet.manage"))
                    if not outpack_read_already_granted:
                        self.append_permission(ow_perm_name, build_packit_perm(OUTPACK_READ))
                        outpack_read_already_granted = True
                case "reports.read":
                    if not is_reviewer(ow_perms):
                        if ow_perm_scope_prefix == "report" and not is_global_reader(ow_perms):
                            self.append_packet_read_perms_for_published_report_versions(ow_perm_scope_id, f"{ow_perm_name}:{ow_perm_scope_id}")
                        elif ow_perm_scope_prefix is None:
                            for report_name in self.published_report_versions:
                                self.append_packet_read_perms_for_published_report_versions(report_name, ow_perm_name)

        return self._packit_perms
