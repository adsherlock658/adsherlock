import sys
import os

inevlog = open("./inputevent.log","r")
cmdlist = []

for line in inevlog.readlines():
    ls = line.split()
    if ls == []:
        continue
    if ls[0] == 'sleep':
        cmd = "adb shell "+ls[0]+" "+ls[1]

        cmdlist.append(cmd)
        continue
    names = ls[0].split(":")[0]
    types = int(ls[1],16)
    codes = int(ls[2],16)
    values = int(ls[3],16)

    cmd = "adb shell sendevent "+names+" "+str(types)+" "+str(codes)+" "+str(values)
    cmdlist.append(cmd)

for cmd in cmdlist:
    print cmd
    os.system(cmd)

inevlog.close()


