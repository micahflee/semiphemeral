#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && cd .. && pwd )"
cd $DIR

# Delete old build
rm -rf build dist > /dev/null

# Make sure pipenv is good
pipenv install --dev

# Create new source and binary build
pipenv run python setup.py sdist bdist_wheel

# Upload to PyPI
pipenv run python -m twine upload dist/*
