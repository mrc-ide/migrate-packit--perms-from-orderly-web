# migrate-packit-perms-from-orderly-web

This application is intended to be used for one-off migration of user permissions from OrderlyWeb to Packit. It is
primarily intended to be used for migrating Montagu users but may require some adaptation for other installations with
other auth types. 

## Installation

It is recommended to install from local source in a hatch shell:

```console
hatch shell
hatch build
pip install dist/migrate_packit_perms_from_orderly_web-<version>.tar.gz~~~~
```
..where `<version>` can be found in `src/migrate_packit_perms_from_orderly_web/__about__.py`

## Running migrations

TODO

`migrate-perms`
