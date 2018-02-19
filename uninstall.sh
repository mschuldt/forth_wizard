#!/bin/bash
set -e

FILE=/tmp/files.txt
python3 setup.py install --record $FILE
cat $FILE
cat $FILE | xargs rm -rf
rm $FILE

rm -rf /usr/local/lib/python3.5/dist-packages/forthwiz
rm -rf ~/.local/lib/python3.5/site-packages/forthwiz
