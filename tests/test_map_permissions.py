from migrate_packit_perms_from_orderly_web.map_permissions import MapPermissions, build_packit_perm

published_report_versions = {
    "r1": ["r1-v1", "r1-v2"],
    "r2": ["r2-v1"]
}
sut = MapPermissions(published_report_versions)

def test_build_packit_perm():
    assert build_packit_perm("test.perm") == {
        "permission": "test.perm",
        "packetId": None,
        "packetGroupId": None,
        "tagId": None
    }
    assert build_packit_perm("scoped.perm", "r1-v1") == {
        "permission": "scoped.perm",
        "packetId": "r1-v1",
        "packetGroupId": None,
        "tagId": None
    }

def test_map_users_manage():
    result = sut.map_ow_permissions_to_packit_permissions([
        { "name": "users.manage", "scope_prefix": None, "scope_id": "" }
    ])
    assert result == [build_packit_perm("user.manage")]

def test_map_reports_run():
    result = sut.map_ow_permissions_to_packit_permissions([
        { "name": "reports.run", "scope_prefix": None, "scope_id": "" }
    ])
    assert result == [
        build_packit_perm("packet.run"),
        build_packit_perm("outpack.read")
    ]

def test_map_reports_review():
    result = sut.map_ow_permissions_to_packit_permissions([
       { "name": "reports.review", "scope_prefix": None, "scope_id": "" }
    ])
    assert result == [
        build_packit_perm("packet.read"),
        build_packit_perm("packet.manage"),
        build_packit_perm("outpack.read")
    ]

def test_outpack_read_mapped_only_once():
    # reports.run and reports.review both grant outpack.read - should only do so once if user has both OW perms
    result = sut.map_ow_permissions_to_packit_permissions([
        { "name": "reports.review", "scope_prefix": None, "scope_id": "" },
        { "name": "reports.run", "scope_prefix": None, "scope_id": "" }
    ])
    assert result == [
        build_packit_perm("packet.read"),
        build_packit_perm("packet.manage"),
        build_packit_perm("outpack.read"),
        build_packit_perm("packet.run")
    ]

def test_global_reports_read_maps_all_published_if_not_reviewer():
    result = sut.map_ow_permissions_to_packit_permissions([
        { "name": "reports.read", "scope_prefix": None, "scope_id": "" }
    ])
    assert result == [
        build_packit_perm("packet.read", "r1-v1"),
        build_packit_perm("packet.read", "r1-v2"),
        build_packit_perm("packet.read", "r2-v1")
    ]

def test_scoped_reports_read_maps_scoped_published():
     result = sut.map_ow_permissions_to_packit_permissions([
          { "name": "reports.read", "scope_prefix": "report", "scope_id": "r1" }
     ])
     assert result == [
        build_packit_perm("packet.read", "r1-v1"),
        build_packit_perm("packet.read", "r1-v2")
     ]

def test_global_reports_read_no_effect_if_reviewer():
    result = sut.map_ow_permissions_to_packit_permissions([
        { "name": "reports.read", "scope_prefix": None, "scope_id": "" },
        { "name": "reports.review", "scope_prefix": None, "scope_id": "" }
    ])
    assert result == [
        build_packit_perm("packet.read"),
        build_packit_perm("packet.manage"),
        build_packit_perm("outpack.read")
    ]

def test_scoped_reports_read_no_effect_if_reviewer():
    result = sut.map_ow_permissions_to_packit_permissions([
        { "name": "reports.read", "scope_prefix": "report", "scope_id": "r1" },
        { "name": "reports.review", "scope_prefix": None, "scope_id": "" }
    ])
    assert result == [
        build_packit_perm("packet.read"),
        build_packit_perm("packet.manage"),
        build_packit_perm("outpack.read")
    ]

def test_scoped_reports_read_no_effect_if_global_reader():
    result = sut.map_ow_permissions_to_packit_permissions([
        { "name": "reports.read", "scope_prefix": None, "scope_id": "" },
        { "name": "reports.read", "scope_prefix": "report", "scope_id": "r1" }
    ])
    assert result == [
        build_packit_perm("packet.read", "r1-v1"),
        build_packit_perm("packet.read", "r1-v2"),
        build_packit_perm("packet.read", "r2-v1")
    ]

def test_unmapped_ow_perms_are_ignored():
    result = sut.map_ow_permissions_to_packit_permissions([
        { "name": "users.manage", "scope_prefix": None, "scope_id": "" },
        { "name": "documents.read", "scope_prefix": None, "scope_id": "" }
    ])
    assert result == [build_packit_perm("user.manage")]