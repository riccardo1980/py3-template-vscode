#!/usr/bin/env bash
set -e

SRCS="{{cookiecutter.package_name}}"
TEST_SRCS="tests"

[ -d $SRCS ] || (echo "Run this script from project root"; exit 1)

set -x

black setup.py $SRCS $TEST_SRCS
isort setup.py $SRCS $TEST_SRCS
mypy setup.py $SRCS $TEST_SRCS
flake8 setup.py $SRCS $TEST_SRCS