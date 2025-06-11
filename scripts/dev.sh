#!/usr/bin/env bash
set -ex
here=$(dirname $0)

export MIGRATE_MONTAGU_URL=https://localhost/api
export MIGRATE_OW_URL=https://localhost/reports
export MIGRATE_PACKIT_API_URL=https://localhost/packit/api
export MIGRATE_USER=test.user@example.com
export MIGRATE_PASSWORD=password

hatch env run -- migrate-perms --disable_verify