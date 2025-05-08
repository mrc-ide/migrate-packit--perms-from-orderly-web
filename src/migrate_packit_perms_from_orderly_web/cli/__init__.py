import click

from migrate_packit_perms_from_orderly_web.__about__ import __version__


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="migrate packit perms from orderly web")
@click.option("--orderly_web_url", envvar="MIGRATE_OW_URL", prompt="OrderlyWeb url", help="Base url of OrderlyWeb")
@click.option("--packit_api_url", envvar="MIGRATE_PACKIT_API_URL", prompt="Packit API url", help="Base url of Packit API")
@click.option("--user", envvar="MIGRATE_USER", prompt="Username", help="Admin user for doing migration")
@click.option("--password", envvar="MIGRATE_PASSWORD", prompt="Password", help="Password for admin user", hide_input=True)
def migrate_perms(orderly_web_url, packit_api_url, user, password):
    click.echo("Placeholder for migrating permissions from orderly web to packit")
    click.echo(f"OW is at {orderly_web_url}")
    click.echo(f"Packit API is at {packit_api_url}")
    click.echo(f"user is {user}")
