#!/bin/bash
set -ex

test_container_name=${DISTELLI_APPNAME}:br-${DISTELLI_RELBRANCH}-${DISTELLI_RELREVISION:0:7}-${DISTELLI_BUILDNUM}

docker run --rm -it \
    -e CODECOV_TOKEN=$CODECOV_TOKEN \
    $test_container_name \
    tox
