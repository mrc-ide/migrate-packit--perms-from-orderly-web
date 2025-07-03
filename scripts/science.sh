#!/usr/bin/env bash
set -ex
here=$(dirname $0)

echo "MIGRATING ORDERLY WEB PERMISSIONS TO PACKIT ON SCIENCE"

export MIGRATE_MONTAGU_URL=https://science.montagu.dide.ic.ac.uk/api
export MIGRATE_OW_URL=https://science.montagu.dide.ic.ac.uk/reports
export MIGRATE_PACKIT_API_URL=https://science.montagu.dide.ic.ac.uk/packit/api
export MIGRATE_USER=
export MIGRATE_PASSWORD=

hatch env run migrate-perms