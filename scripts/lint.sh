#!/usr/bin/env bash
set -e

SRCS="hooks"
TEST_SRCS="tests"

[ -d $SRCS ] || (echo "Run this script from project root"; exit 1)

set -x

black $SRCS $TEST_SRCS
isort $SRCS $TEST_SRCS
mypy $SRCS $TEST_SRCS
flake8 $SRCS $TEST_SRCS