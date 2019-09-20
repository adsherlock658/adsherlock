#!/bin/bash

pids=`ps x|grep 'tcpdump'|awk '{print $1}'`
echo $pids
for p in $pids
do
    echo $p
    kill $p
done



