import sys
import os
import time

getlog = sys.argv[1]
inevlog = open(getlog,"r")

FLAGONE = "00000001"
SLEEP = "adb shell sleep 3"
SLEEPSHORT = "adb shell sleep 1"
SLEEPLONG = "adb shell sleep 6"
repeat = 3

actions = []
click = []
cntOne = 0
secondOne = 0

while True:
    line = inevlog.readline()
    ls = line.split()
    ls = line.split()
    if not line:
        actions.append(click)
        break

    if ls[3] == FLAGONE:
        cntOne += 1

    if ls[3] != FLAGONE:
        cntOne = 0

    if cntOne == 1:
        if click != []:
            actions.append(click)
        click = []

    deviceName = ls[0].split(":")[0]
    types = int(ls[1], 16)
    codes = int(ls[2], 16)
    values = int(ls[3], 16)
    cmd = "adb shell sendevent "+deviceName+" "+str(types)+" "+str(codes)+" "+str(values)
    click.append(cmd)

for click in actions:
    ts = time.time()
    print "At time:", "{0:.6f}".format(ts)

    for cmd in click:
        print cmd
        os.system(cmd)
    os.system(SLEEP)

for i in range(repeat):
    cnt = len(actions)
    os.system(SLEEPLONG)
    for c in [cnt-2, cnt-1]:
        click = actions[c]
        print "At time:", "{0:.6f}".format(ts)
        for cmd in click:
            print cmd
            os.system(cmd)
        os.system(SLEEPSHORT)

inevlog.close()


