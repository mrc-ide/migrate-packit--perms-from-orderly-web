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

    def append_packet_read_perms_for_published_report_versions(self, report_name, list_to_append):
        for version in self.published_report_versions[report_name]:
            list_to_append.append(build_packit_perm(PACKET_READ, version)) # It would be more efficient to build these in advance!

    def map_ow_permissions_to_packit_permissions(self, ow_perms):
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

        packit_perms = []
        outpack_read_already_granted = False
        for ow_perm in ow_perms:
            ow_perm_name,  ow_perm_scope_prefix, ow_perm_scope_id = unpack_ow_perm(ow_perm)

            match ow_perm_name:
                case "reports.run":
                    packit_perms.append(build_packit_perm("packet.run"))
                    if not outpack_read_already_granted:
                        packit_perms.append(build_packit_perm(OUTPACK_READ))
                case "users.manage":
                    packit_perms.append(build_packit_perm("user.manage"))
                case "reports.review":
                    packit_perms.append(build_packit_perm(PACKET_READ))
                    packit_perms.append(build_packit_perm("packet.manage"))
                    if not outpack_read_already_granted:
                        packit_perms.append(build_packit_perm(OUTPACK_READ))
                case "reports.read":
                    if not is_reviewer(ow_perms):
                        if ow_perm_scope_prefix == "report" and not is_global_reader(ow_perms):
                            self.append_packet_read_perms_for_published_report_versions(ow_perm_scope_id, packit_perms)
                        elif ow_perm_scope_prefix is None:
                            for report_name in self.published_report_versions:
                                self.append_packet_read_perms_for_published_report_versions(report_name, packit_perms)

        return packit_perms
