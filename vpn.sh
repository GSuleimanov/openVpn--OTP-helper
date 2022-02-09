#!/bin/sh
parent_path="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
python3 $parent_path/sample/main.py "$@"