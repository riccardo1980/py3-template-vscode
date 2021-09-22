#!/usr/bin/env bash
set -e

SRCS="{{cookiecutter.package_name}}"
TEST_SRCS=" tests"

[ -d $SRCS ] || (echo "Run this script from project root"; exit 1)

set -x

coverage run --source=$SRCS -m pytest $TEST_SRCS
# coverage combine
coverage report --show-missing
coverage xml