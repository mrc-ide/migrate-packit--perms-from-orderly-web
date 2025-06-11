#!/usr/bin/env bash

here=$(dirname $0)

image=vimc/montagu-cli:master
exec docker run --rm --network $NETWORK $image "$@"
