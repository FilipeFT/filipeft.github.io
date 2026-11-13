#!/bin/sh
# build.sh — the one command: validate, test, build, install.
#
# Runs build.py with --install, so the canvas is written — but only
# after every check passes. A failure prints its problems, writes
# nothing, and exits non-zero.
exec python3 "$(dirname "$0")/build.py" --install "$@"
