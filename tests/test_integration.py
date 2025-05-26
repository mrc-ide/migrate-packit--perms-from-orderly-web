from migrate_packit_perms_from_orderly_web.migrate import Migrate
from migrate_packit_perms_from_orderly_web.orderly_web_permissions import OrderlyWebPermissions
from migrate_packit_perms_from_orderly_web.packit_permissions import PackitPermissions
from migrate_packit_perms_from_orderly_web.map_permissions import build_packit_perm

def create_sut():
    montagu_url="https://localhost/api"
    orderly_web_url="https://localhost/reports"
    packit_api_url = "https://localhost/packit/api"
    user="test.user@example.com"
    password="password"
    disable_verify = True

    # arrange - create migrate sut
    ow = OrderlyWebPermissions(montagu_url, orderly_web_url, user, password, disable_verify)
    packit = PackitPermissions(packit_api_url, disable_verify)
    return Migrate(ow, packit)

def assert_packit_users(users, expected_usernames):
    usernames = list(map(lambda u: u["username"], users))
    assert sorted(expected_usernames) == sorted(usernames)

def permission_matches(permission, name, packit_id = None):
    return permission == build_packit_perm(name, packit_id)

def assert_packit_user_matches(packit_user, username, email, display_name, roles):
    assert packit_user["username"] == username
    assert packit_user["email"] == email
    assert packit_user["displayName"] == display_name
    user_roles = list(map(lambda r: r["name"], packit_user["roles"]))
    assert sorted(user_roles) == sorted(roles + [username]) # expect user role too


def test_migrate():
    sut = create_sut()

    sut.prepare_migrate()

    # Sanity test - check expected published report version count
    published_report_versions = sut.published_report_versions
    assert len(published_report_versions["minimal"]) == 1
    assert len(published_report_versions["html"]) == 1
    assert len(published_report_versions["other"]) == 2
    assert len(published_report_versions["interactive"]) == 0
    assert len(published_report_versions["use_resource"]) == 1

    # Sanity test: check expected users and packets before we migrate
    assert_packit_users(sut.packit.get_users(), ["test.user"])

    # Test expected roles and users to create
    assert sut.packit_admin_users == ["test.user"]

    assert len(sut.packit_roles_to_create.keys()) == 2

    # Developer role:
    # reports.review => packet.read (global), packet.manage (global), outpack.read
    # users.manage => user.manage
    developer_perms = sut.packit_roles_to_create["developer"]
    assert len(developer_perms) == 4
    assert permission_matches(developer_perms[0], "packet.read")
    assert permission_matches(developer_perms[1], "packet.manage")
    assert permission_matches(developer_perms[2], "outpack.read")
    assert permission_matches(developer_perms[3], "user.manage")

    # Funder role:
    # packet.read: "other" published version packets * 2
    # packet.read: "use_resource" published version * 1
    funder_perms = sut.packit_roles_to_create["funder"]
    assert len(funder_perms) == 3
    assert permission_matches(funder_perms[0], "packet.read", published_report_versions["other"][0])
    assert permission_matches(funder_perms[1], "packet.read", published_report_versions["other"][1])
    assert permission_matches(funder_perms[2], "packet.read", published_report_versions["use_resource"][0])

    assert len(sut.packit_users_to_create.keys()) == 2

    dev_user = sut.packit_users_to_create["dev.user"]
    assert dev_user["roles"] == ["developer"]
    # Dev user direct perms:
    # report.run => packet.run, outpack.read
    dev_user_perms = dev_user["direct_permissions"]
    assert len(dev_user_perms) == 2
    assert permission_matches(dev_user_perms[0], "packet.run")
    assert permission_matches(dev_user_perms[1], "outpack.read")

    funder_user = sut.packit_users_to_create["funder.user"]
    assert funder_user["roles"] == ["funder"]
    # Funder user direct perms
    # packet.read: html * 1
    # packet.read: minimal * 1
    funder_user_perms = funder_user["direct_permissions"]
    assert len(funder_user_perms) == 2
    assert permission_matches(funder_user_perms[0], "packet.read", published_report_versions["html"][0])
    assert permission_matches(funder_user_perms[1], "packet.read", published_report_versions["minimal"][0])

    sut.migrate_permissions()

    # Check expected users after we migrate
    users = sut.packit.get_users()
    assert_packit_users(users, ["dev.user", "funder.user", "test.user" ])
    assert_packit_user_matches(users[0], "dev.user", "dev.user@example.com", "Dev User", ["developer"])
    assert_packit_user_matches(users[1], "funder.user", "funder.user@example.com", "Funder User", ["funder"])
    # TODO: permissions!




