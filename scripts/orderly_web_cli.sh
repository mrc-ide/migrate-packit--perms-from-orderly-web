#!/usr/bin/env bash

image=vimc/orderly-web-user-cli:master
docker run --rm -v montagu_orderly_volume:/orderly --network montagu_proxy $image $@
