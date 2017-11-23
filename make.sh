#!/bin/bash

gcc example.c -g -O3 -o example

rm -rf build

#python3 setup.py build
python3 setup.py install
