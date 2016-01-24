#!/bin/bash

declare -a flist=()

for i in $(find . -type f ! -name *.sh);
do
    flist+=("${i}")
done

CLIENT=../sender.py

for i in "${flist[@]}"
do
    echo Sending.. 
    echo "$i"
    python $CLIENT -f $i
done
