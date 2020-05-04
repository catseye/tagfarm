#!/bin/sh

PYTHONPATH=src python2 src/tagfarm/tests.py || exit 1
PYTHONPATH=src python3 src/tagfarm/tests.py || exit 1
