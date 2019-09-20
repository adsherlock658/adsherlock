#!/bin/bash

rawlog=$1
output=$1".form"

begin=`awk '/^\/dev\/input\/event/{print NR}' $rawlog | head -n 1`
end=`awk '/^\/dev\/input\/event/{print NR}' $rawlog | tail -n 1`

begin=$(($begin-1))
end=$(($end+1))

echo $begin
echo $end

awk -vt1=$begin -vt2=$end 'NR>t1 && NR<t2 {print $0}' $rawlog > $output


