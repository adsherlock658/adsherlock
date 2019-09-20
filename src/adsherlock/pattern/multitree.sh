#!/bin/bash
dir='/home/caochenhong/adviser/adviser-exp/apps/'

cd $dir
for appname in `ls`
do
    cd $dir
    cd $appname
    python -m infocom.tree
    python -m infocom.analysis
done
