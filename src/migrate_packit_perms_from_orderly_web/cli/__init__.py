import click

from migrate_packit_perms_from_orderly_web.__about__ import __version__
from migrate_packit_perms_from_orderly_web.migrate import Migrate
from migrate_packit_perms_from_orderly_web.orderly_web_permissions import OrderlyWebPermissions
from migrate_packit_perms_from_orderly_web.packit_permissions import PackitPermissions

@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="migrate packit perms from orderly web")
@click.option("--montagu_url", envvar="MIGRATE_MONTAGU_URL", prompt="Montagu url", help="Base url of Montagu API")
@click.option("--orderly_web_url", envvar="MIGRATE_OW_URL", prompt="OrderlyWeb url", help="Base url of OrderlyWeb")
@click.option("--packit_url", envvar="MIGRATE_PACKIT_URL", prompt="Packit url", help="Base url of Packit")
@click.option("--user", envvar="MIGRATE_USER", prompt="Username", help="Admin user for doing migration")
@click.option("--password", envvar="MIGRATE_PASSWORD", prompt="Password", help="Password for admin user", hide_input=True)
@click.option("--disable_verify", is_flag=True, envvar="MIGRATE_DISABLE_VERIFY", prompt="Disable certificate verify (localhost only)", help="Disable certificate verify (localhost only)", default=False)
def migrate_perms(montagu_url, orderly_web_url, packit_url, user, password, disable_verify):
    click.echo(f"Montagu is at {montagu_url}")
    click.echo(f"OrderlyWeb is at {orderly_web_url}")
    click.echo(f"Packit is at {packit_url}")
    click.echo(f"user is {user}")
    click.echo(f"disable_verify is {disable_verify}")
    ow = OrderlyWebPermissions(montagu_url, orderly_web_url, user, password, disable_verify)
    packit = PackitPermissions(packit_url, disable_verify)
    m = Migrate(ow, packit)
    m.migrate_permissions()
