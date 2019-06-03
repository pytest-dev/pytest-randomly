#!/bin/sh
set -ex
export CUSTOM_COMPILE_COMMAND="./compile.sh"
python3.5 -m piptools compile --generate-hashes "$@" -o py35.txt
python3.6 -m piptools compile --generate-hashes "$@" -o py36.txt
python3.7 -m piptools compile --generate-hashes "$@" -o py37.txt
