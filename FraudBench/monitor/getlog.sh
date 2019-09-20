#!/bin/bash
tplog=$1
andlog=$2
clicklog=$3

nohup tcpdump -i eth0 'host 10.214.149.162 and port http' -w $tplog &

python ../clickdroid/simclick_v2.py $clicklog

pids=`ps x|grep 'tcpdump'|awk '{print $1}'`
echo $pids
for pid in $pids
do
    echo $pid
    kill $pid
done

adb logcat -d *:D > $andlog


