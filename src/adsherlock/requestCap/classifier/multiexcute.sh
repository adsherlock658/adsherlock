#!/bin/bash
dir='/home/caochenhong/adviser/adviser/exps4/exps4/'
py='/home/caochenhong/adviser/requestCap/classifier/requestree.py'

cd $dir
for appname in `ls`
do
    cd $dir
    python $py $appname 
done
