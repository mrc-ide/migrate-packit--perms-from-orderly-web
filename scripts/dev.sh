#!/usr/bin/env bash
set -ex
here=$(dirname $0)

hatch build
pip install dist/migrate_packit_perms_from_orderly_web-0.0.1.tar.gz
export MIGRATE_MONTAGU_URL=https://localhost/api
export MIGRATE_OW_URL=https://localhost/reports
export MIGRATE_PACKIT_API_URL=https://localhost/packit/api
export MIGRATE_USER=test.user@example.com
export MIGRATE_PASSWORD=password
export MIGRATE_DISABLE_VERIFY=True # Whether to disable certificate checks - only set this to True for local testing

migrate-perms