#!/bin/bash
dir='/home/caochenhong/adviser/adviser-exp/apps/'
dedup='/home/caochenhong/adviser/requestCap/pattern/deduplication.py'
cd $dir
for appname in `ls`
do
    python $dedup $appname
done
