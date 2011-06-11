#! /bin/bash

dir=${0%/*}
if [ -d "$dir" ]; then
  cd "$dir"
fi

python2.6 ./musicquizzer.py
