#!/bin/bash
export DISTELLI_BUILDNUM=1234
export DISTELLI_RELREVISION=abcd1234
export DISTELLI_RELBRANCH=master
export DISTELLI_APPNAME=catracking

./distelli/build.sh
./distelli/prerelease.sh
