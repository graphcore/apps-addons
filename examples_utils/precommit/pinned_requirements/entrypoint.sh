#!/bin/bash

SCRIPT_DIR=$(dirname $0)
SCRIPT_PATH=$(realpath $SCRIPT_DIR/pinned_requirements.py)

pushd $SCRIPT_DIR/../../../ > /dev/null

python3 -m pip install -r requirements.txt > /dev/null
python3 -m pip install -r requirements-precommit.txt > /dev/null

MODULE_ROOT=$(pwd)
popd > /dev/null
python3 $SCRIPT_PATH $@
exit $?
