import click

from migrate_packit_perms_from_orderly_web.__about__ import __version__
from migrate_packit_perms_from_orderly_web.migrate import Migrate, get_displayable_permissions
from migrate_packit_perms_from_orderly_web.orderly_web_permissions import OrderlyWebPermissions
from migrate_packit_perms_from_orderly_web.packit_permissions import PackitPermissions

@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="migrate packit perms from orderly web")
@click.option("--montagu_url", envvar="MIGRATE_MONTAGU_URL", prompt="Montagu url", help="Base url of Montagu API")
@click.option("--orderly_web_url", envvar="MIGRATE_OW_URL", prompt="OrderlyWeb url", help="Base url of OrderlyWeb")
@click.option("--packit_api_url", envvar="MIGRATE_PACKIT_API_URL", prompt="Packit API url", help="Base url of Packit API")
@click.option("--user", envvar="MIGRATE_USER", prompt="Username", help="Admin user for doing migration")
@click.option("--password", envvar="MIGRATE_PASSWORD", prompt="Password", help="Password for admin user", hide_input=True)
@click.option("--disable_verify", is_flag=True, envvar="MIGRATE_DISABLE_VERIFY", prompt="Disable certificate verify (localhost only)", help="Disable certificate verify (localhost only)", default=False)
def migrate_perms(montagu_url, orderly_web_url, packit_api_url, user, password, disable_verify):
    click.echo(f"Montagu is at {montagu_url}")
    click.echo(f"OrderlyWeb is at {orderly_web_url}")
    click.echo(f"Packit is at {packit_api_url}")
    click.echo(f"user is {user}")
    click.echo(f"disable_verify is {disable_verify}")
    ow = OrderlyWebPermissions(montagu_url, orderly_web_url, user, password, disable_verify)
    packit = PackitPermissions(packit_api_url, disable_verify)
    m = Migrate(ow, packit)
    m.prepare_migrate()
    # Flag up changes which will be made to the user and give them the chance to cancel
    click.echo("")
    click.echo(f"Found the following published report version counts:")
    for name, versions in m.published_report_versions.items():
        click.echo(f"{name}: {len(versions)}")
    click.echo("")

    click.echo(f"Not modifying Packit ADMIN users: {m.packit_admin_users}")
    click.echo(f"Creating new users in Packit:")
    for username, user_details in m.packit_users_to_create.items():
        click.echo(f"Username: {username}")
        click.echo(f"Email: {user_details["email"]}")
        click.echo(f"Display name: {user_details["display_name"]}")
        click.echo(f"Roles: {user_details["roles"]}")
        click.echo(f"Direct permissions: {get_displayable_permissions(user_details["direct_permissions"])}")
        click.echo("")

    click.echo(f"Creating new roles in Packit:")
    for role, permissions in m.packit_roles_to_create.items():
        click.echo(f"Name: {role}")
        click.echo(f"Permissions: {get_displayable_permissions(permissions)}")
        click.echo("")

    if click.confirm("Continue with migration?"):
        m.migrate_permissions()
        click.echo("Migration complete")
    else:
        click.echo("Migration cancelled")
