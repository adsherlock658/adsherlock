#!/bin/bash
andtpdlog=$1
tplog=$2
presult=$3
andlog=$4
clicklog=$5

nohup adb shell tcpdump -i any -p -vv -s 0 -w $andtpdlog &

adb logcat -c
python ../clickdroid/simclick_v2.py $clicklog


pids=`ps x|grep 'tcpdump'|awk '{print $1}'`
echo $pids
echo "PID of this script is: $$"
for pid in $pids
do
    echo $pid
    if [ $pid -eq $$ ];then
        continue
    fi
    kill $pid
done

adb pull $andtpdlog $tplog

adb logcat -d *:D > $andlog


