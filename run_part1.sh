#!/bin/sh

for i in ./tweets/*
do
    echo Running ttwt on $i
    output=./twts/`basename $i`.twt
    if [ -f $output ]
    then
        rm $output
    fi
    python ./ttwt.py $i $output &>/dev/null
    echo Done
done
