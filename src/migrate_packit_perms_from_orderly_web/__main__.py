import sys
from migrate import something, another

if __name__ == "__main__":
    from migrate_packit_perms_from_orderly_web.cli import migrate_perms

    sys.exit(migrate_perms())
