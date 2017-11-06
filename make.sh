#!/bin/bash

gcc wiz_test.c -g -O3 -o test

rm -rf build

#python3 setup.py build
python3 setup.py install
