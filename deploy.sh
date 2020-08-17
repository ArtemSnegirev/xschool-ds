#!/usr/bin/env sh

set -e

pdoc --html --force --output-dir docs projects/workload_scoring/lib.py
mv docs/lib.html docs/index.html

git add -A
git commit -m "$1"

git push origin master
