# migrate-packit-perms-from-orderly-web

This application is intended to be used for one-off migration of user permissions from OrderlyWeb to Packit. It is
primarily intended to be used for migrating Montagu users but may require some adaptation for other installations with
other auth types. 

## Installation

It is recommended to install from local source in a hatch shell:

```console
hatch shell
hatch build
pip install dist/migrate_packit_perms_from_orderly_web-<version>.tar.gz
```
..where `<version>` can be found in `src/migrate_packit_perms_from_orderly_web/__about__.py`

## Running migrations

TODO

`migrate-perms`

## Manual testing 

1. Run a local Montagu environment (no Montagu test data):
`./scripts/run-dependencies`
2. `hatch shell`
3. Build and install the migrations code, set environment variables to the local Montagu endpoints and credentials, and run `migrate-perms`: `./scripts/dev.sh`

# Integration test
1. Run dependencies: `./scripts/run-dependencies`
2. `hatch shell`
3. `hatch test`

NB The integration test runs the migration, changing the state of Packit. You should re-run dependencies to set up the 
original Packit state every time you re-run the integration test. 