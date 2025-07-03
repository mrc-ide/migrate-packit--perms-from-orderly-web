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

# Add test (admin) user to packit
PACKIT_DB=montagu-packit-db-1
docker exec $PACKIT_DB create-preauth-user --username "test.user" --email "test.user@example.com" --displayname "Test User" --role "ADMIN"

# Add some other example users and roles which we can test the migration against
# Montagu/OW
# Add non-admin users who do not exist in packit yet, should be created
$here/montagu_cli.sh add "Funder User" funder.user \
    funder.user@example.com password \
    --if-not-exists
$here/montagu_cli.sh addRole funder.user user

$here/montagu_cli.sh add "Dev User" dev.user \
    dev.user@example.com password \
    --if-not-exists
$here/montagu_cli.sh addRole dev.user user

# Add an admin user to OW who does not exist in Packit, to test admins can be migrated successfully
$here/montagu_cli.sh add "Admin User" admin.user \
    admin.user@example.com password \
    --if-not-exists

$here/montagu_cli.sh addRole admin.user user

# Log in to OW as the users to force them to be created with Montagu name - using the OW CLI creates with email only so the
# users are not linked with the Montagu users correctly.
# Subsequent OW CLI calls must also identify users by email not by username
hatch env run python ./src/migrate_packit_perms_from_orderly_web/run_dev/login_ow_users.py

# Grant perms to users and roles. NB OW user roles are identified by email not username

# minimal has one published and two unpublished versions, html has one published
# So funder.user should have two direct packet read permissions
$here/orderly_web_cli.sh grant funder.user@example.com report:minimal/reports.read
$here/orderly_web_cli.sh grant funder.user@example.com report:html/reports.read

$here/orderly_web_cli.sh grant dev.user@example.com */reports.run

# Add two non-admin roles
$here/orderly_web_cli.sh add-groups Funder Developer

# Give different perms to the roles than those the users have directly
$here/orderly_web_cli.sh grant Developer */reports.review */users.manage */reports.read
# other has two published and two unpublished versions, interactive has one unpublished, use_resource has one published.
# So funder role should have three packet read perms
$here/orderly_web_cli.sh grant Funder report:other/reports.read report:interactive/reports.read report:use_resource/reports.read */documents.read

# Add users to their group roles
$here/orderly_web_cli.sh add-members Developer dev.user@example.com
$here/orderly_web_cli.sh add-members Funder funder.user@example.com
$here/orderly_web_cli.sh add-members Admin admin.user@example.com

echo "Dependencies are running. Press Ctrl+C to teardown."
sleep infinity


