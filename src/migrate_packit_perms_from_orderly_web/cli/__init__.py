import click

from migrate_packit_perms_from_orderly_web.__about__ import __version__


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="migrate packit perms from orderly web")
def migrate_perms():
    click.echo("Placeholder for migrating permissions from orderly web to packit")
