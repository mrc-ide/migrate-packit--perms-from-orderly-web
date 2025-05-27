#!/usr/bin/env bash
set -ex
here=$(dirname $0)

echo "MIGRATING ORDERLY WEB PERMISSIONS TO PACKIT ON UAT"

hatch build
pip install dist/migrate_packit_perms_from_orderly_web-0.0.1.tar.gz
export MIGRATE_MONTAGU_URL=https://uat.montagu.dide.ic.ac.uk/api
export MIGRATE_OW_URL=https://uat.montagu.dide.ic.ac.uk/reports
export MIGRATE_PACKIT_API_URL=https://uat.montagu.dide.ic.ac.uk/packit/api
export MIGRATE_USER=
export MIGRATE_PASSWORD=
export MIGRATE_DISABLE_VERIFY=False # Whether to disable certificate checks - only set this to True for local testing

migrate-perms