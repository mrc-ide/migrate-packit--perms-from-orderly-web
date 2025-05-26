#!/usr/bin/env bash

set -ex
here=$(dirname $0)
export ORG=vimc

function cleanup() {
    docker compose down || true
}

cleanup

# This traps errors and Ctrl+C
trap cleanup EXIT

docker volume rm montagu_orderly_volume -f
docker compose pull
docker compose up -d

# Start montagu and orderly-web
docker compose exec api mkdir -p /etc/montagu/api/
docker compose exec api touch /etc/montagu/api/go_signal
docker compose exec orderly-web-web mkdir -p /etc/orderly/web
docker compose cp $here/orderlywebconfig.properties orderly-web-web:/etc/orderly/web/config.properties
docker compose exec orderly-web-web touch /etc/orderly/web/go_signal
docker compose exec orderly-web-web touch /etc/orderly/web/go_signal
docker compose exec orderly touch /orderly_go

# Wait for the montagu database
docker compose exec db montagu-wait.sh 120

# Migrate the montagu database
migrate_image=$ORG/montagu-migrate:master
docker pull $migrate_image
docker run --rm --network=montagu_proxy $migrate_image

# Always generate orderly-web report test database
rm demo -rf
rm git -rf
docker pull $ORG/orderly:master
docker run --rm \
  --entrypoint create_orderly_demo.sh \
  -u $UID \
  -v $PWD:/orderly \
  -w "/orderly" \
  $ORG/orderly:master \
  "."

# Copy the demo db file to top level
docker compose cp $PWD/demo/orderly.sqlite orderly-web-web:/orderly/orderly.sqlite

# Migrate the orderlyweb tables
ow_migrate_image=$ORG/orderlyweb-migrate:master
docker pull $ow_migrate_image
docker run --rm --network=montagu_proxy \
  -v montagu_orderly_volume:/orderly \
  $ow_migrate_image

# Migrate orderly reports to outpack
orderly_outpack_migrate_image=mrcide/outpack.orderly:main
docker pull $orderly_outpack_migrate_image

docker run \
  -v ./demo:/orderly \
  -v ./outpack:/outpack \
  $orderly_outpack_migrate_image /orderly /outpack --once

# Add test user to montagu
export NETWORK=montagu_proxy

# TODO: use vars for shared user details

$here/montagu_cli.sh add "Test User" test.user \
    test.user@example.com password \
    --if-not-exists

$here/montagu_cli.sh addRole test.user user
$here/montagu_cli.sh addRole test.user admin

# Add test user to orderly_web
$here/orderly_web_cli.sh add-users test.user@example.com
$here/orderly_web_cli.sh grant test.user@example.com */reports.read
$here/orderly_web_cli.sh grant test.user@example.com */reports.review
$here/orderly_web_cli.sh grant test.user@example.com */users.manage

# copy helper scripts into packit-db
docker compose cp $here/packit-db/add-permission-to-role orderly-web-packit-db:/bin/add-permission-to-role
docker compose cp $here/packit-db/add-user-to-role orderly-web-packit-db:/bin/add-user-to-role
docker compose cp $here/packit-db/create-role orderly-web-packit-db:/bin/create-role

# Add test (admin) user to packit
PACKIT_DB=montagu-orderly-web-packit-db-1
docker exec $PACKIT_DB create-preauth-user --username "test.user" --email "test.user@example.com" --displayname "Test User" --role "ADMIN"

# Add some other example users and roles which we can test the migration against
# Montagu/OW
# Add non-admin users who do not exist in packit yet, should be created
$here/montagu_cli.sh add "Funder User" funder.user \
    funder.user@example.com password \
    --if-not-exists
$here/montagu_cli.sh addRole funder.user user
#$here/orderly_web_cli.sh add-users funder.user@example.com

$here/montagu_cli.sh add "Dev User" dev.user \
    dev.user@example.com password \
    --if-not-exists
$here/montagu_cli.sh addRole dev.user user

# Log in to OW as the users to force them to be created with Montagu name - using the OW CLI creates with email only so the
# users are not linked with the Montagu users correctly.
# Subsequent CLI calls must also identify users by email not by username
python ./src/migrate_packit_perms_from_orderly_web/run_dev/login_ow_users.py
#./scripts/testpy.sh

# Grant perms to users and roles. NB OW user roles are identified by email not username

# minimal has one published and two unpublished versions, html has one published
# So funder.user should have two direct packet read permissions
$here/orderly_web_cli.sh grant funder.user@example.com report:minimal/reports.read
$here/orderly_web_cli.sh grant funder.user@example.com report:html/reports.read

$here/orderly_web_cli.sh grant dev.user@example.com */reports.run

#
# Add two non-admin roles
$here/orderly_web_cli.sh add-groups funder developer

# Give different perms to the roles than those the users have directly
$here/orderly_web_cli.sh grant developer */reports.review */users.manage
# other has two published and two unpublished versions, interactive has one unpublished, use_resource has one published.
# So funder role should have three packet read perms
$here/orderly_web_cli.sh grant funder report:other/reports.read report:interactive/reports.read report:use_resource/reports.read */documents.read

# Add non-admin users to their group roles
$here/orderly_web_cli.sh add-members developer dev.user@example.com
$here/orderly_web_cli.sh add-members funder funder.user@example.com

# PACKIT - uncomment to test error case only
# Add a non-admin role. Migration should not run if this is present
#docker exec $PACKIT_DB create-role "runner"
#docker exec $PACKIT_DB add-permission-to-role --role "runner" --permission "packet.run"

# Add a non-admin user. Migration should not run if this is present
#docker exec $PACKIT_DB create-preauth-user --username "packit.only.user" --email "packit.only.user@example.com" --displayname "Packit Only User" --role "runner"

echo "Dependencies are running. Press Ctrl+C to teardown."
sleep infinity


