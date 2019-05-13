#!/bin/sh
set -ex
export CUSTOM_COMPILE_COMMAND="./requirements-compile.sh"
python3.5 -m piptools compile "$@" -o requirements/py35.txt
python3.6 -m piptools compile "$@" -o requirements/py36.txt
python3.7 -m piptools compile "$@" -o requirements/py37.txt
