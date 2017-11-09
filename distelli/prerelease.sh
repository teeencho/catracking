#!/bin/bash
set -ex

test_container_name=catracking:br-${DISTELLI_RELBRANCH}-${DISTELLI_RELREVISION:0:7}-${DISTELLI_BUILDNUM}

docker run --rm \
    -e CODECOV_TOKEN=$CODECOV_TOKEN \
    $test_container_name \
    tox
