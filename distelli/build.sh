#!/bin/bash
set -e

docker \
    build \
    ${build_args} \
    --rm \
    -t catracking:br-${DISTELLI_RELBRANCH}-${DISTELLI_RELREVISION:0:7}-${DISTELLI_BUILDNUM} \
    .

echo "Testing container build is ready!"
