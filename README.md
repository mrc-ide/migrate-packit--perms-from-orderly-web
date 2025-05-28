# migrate-packit-perms-from-orderly-web

This application can be used for one-off migration of user permissions from OrderlyWeb to Packit. It is
primarily intended to be used for migrating Montagu users and may require some adaptation for other installations with
other auth types. 

This is a hatch application. To run, it is recommended to install from local source in a hatch shell. Scripts are 
provided which install local sources for running against local dev environment, and against uat. 

The entry point is a [click](https://click.palletsprojects.com/en/stable/) CLI application which uses environment variables
for required values such as OrderlyWeb and Packit URLs - if these values are not set, they are requested as user input. 

Migration is done in two stages: first, the details of the users and roles to be created in Packit are determined and
displayed in the console. The user then has the opportunity to cancel or continue with the actual migration. 

To run migrations you must have admin permission on both OrderlyWeb and Packit. Migrations will only run if Packit is
"clean" i.e. if there are no non-ADMIN users or roles. Permissions of ADMIN users will not be changed by the migrations. 

Python modules in `src` implement the main migration logic, mapping of OrderlyWeb to Packit permissions and HTTP
interaction with OrderlyWeb and with Packit. There is also a `login_ow_users` module in the `run_dev` folder supporting 
programmatic login of test users in local dev environment (more details below).

## Running migrations

### Local dev environment

To set up a test environment, and initialise OrderlyWeb:
1. `hatch shell`
2. `./scripts/run-dependencies`

As well as starting all required docker containers, this creates an ADMIN user in OrderlyWeb, `test.user`, and two 
non-ADMIN users, `dev.user` and `funder.user`, with roles and direct permissions which can be migrated. 

It is necessary to `hatch shell` before running deps because we make use of `orderly_web_permissions`  in `src` to log the 
migrating users into OrderlyWeb. This is the easiest way to get the user initialised in OW with correct user name
matching the user name in Montagu. We can't use the OrderlyWeb CLI script as usual because this simply uses the email
for both user name and email fields, and we want to test Montagu-style users where these are different. 

To run the migrations (in a second console):
1. `hatch shell`
2. `./scripts/dev.sh` - this script installs the latest source and sets environment variables for local dev before running the migration. 

Once migration has run successfully, you should be able to login to https://localhost as funder.user@example.com or
dev.user@example.com and see that the user has the expected access in Packit as detailed in the deps script (e.g. limited
read access for the funder user).

### Montagu UAT
1. `hatch shell`
2. `./scripts/uat.sh` - this script sets the urls as required. You will need to log in with your UAT username and password, and will
    need to have Admin role in Packit. 

### Other environments

1. Install from local source:
```console
hatch shell
hatch build
pip install dist/migrate_packit_perms_from_orderly_web-<version>.tar.gz
```
..where `<version>` can be found in `src/migrate_packit_perms_from_orderly_web/__about__.py`

2. Run migrations: `migrate-perms`

This will prompt for urls etc - alternatively you can export these as environment variables - see 
`src/migrate_packit_perms_from_orderly_web/cli` for details. 

## Automated Tests

There is a full integration test of the migration logic, and a unit test of the permission mapping in `tests`.
The integration test runs the migration, changing the state of Packit. So we need to re-run dependencies to set up the
original Packit state every time the integration test is re-run.

To run tests: `hatch test`

There is no CI set up for this project, so tests are just run locally. 

## Further oddities
- While working on this project, you may frequently find yourself re-running dependencies. This tears down OrderlyWeb and 
  Montagu, but leaves the `outpack` folder behind as I was having problems removing that in script because of its permissions. 
  This means that packets can proliferate for users with global read permission! But users with limited read permissions should
  just see packets corresponding to the most recent published OrderlyWeb published versions.  
- When running locally, we need to tell python `requests` to chill out about self-signed certificates, by setting the `verify`
  parameter to False, hence the MIGRATE_DISABLE_VERIFY setting, which should only be set to True for the local environment. 