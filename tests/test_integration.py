from migrate_packit_perms_from_orderly_web.migrate import Migrate
from migrate_packit_perms_from_orderly_web.orderly_web_permissions import OrderlyWebPermissions
from migrate_packit_perms_from_orderly_web.packit_permissions import PackitPermissions

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

def assert_packit_users(packit, expected_usernames):
    users = packit.get_users()
    usernames = list(map(lambda u: u["username"], users))
    assert sorted(expected_usernames) == sorted(usernames)

def test_migrate():
    sut = create_sut()

    sut.prepare_migrate()
    assert sut.packit_admin_users == ["test.user"]
    assert sut.packit_users_to_delete == ["packit.only.user"]
    assert sut.packit_users_to_migrate == ["both.user"]
    assert sut.packit_users_to_create == ["ow.only.user@example.com"]

    # Check expected users before we migrate
    assert_packit_users(sut.packit, ["test.user", "packit.only.user", "both.user"])

    sut.migrate_permissions()

    # Check expected users after we migrate
    assert_packit_users(sut.packit, ["test.user", "both.user", "ow.only.user@example.com"])

