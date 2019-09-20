import re
import time

timeStr = time.strftime('%Y%m%d%H', time.localtime(time.time()))
# timeStr = "2016062022"
androidlog = "./tcplog/logcat."+timeStr
log = open(androidlog, "r")

mEventsList = []
flag = 0
case1list = ["Time", "PointerID", "Pressure", "Size", "Source", "ToolType", "ToolMajor", "ToolMinor", "Descriptor", "Generation", "Location","Sources", "DeviceID"]


def case1(attr, edict, ls):
    edict[attr] = ls[2].lstrip()

for line in log.readlines():
    if re.search("\*MotionEvent\*", line):
        eventDict = {}
        flag = 1
        continue
    if flag == 1:
        ls = line.split(":")
        attr = ls[1].lstrip()
        # print attr
        if attr in case1list:
            case1(attr, eventDict, ls)
            if attr == 'DeviceID':
                print "********"
                flag = 0
                mEventsList.append(eventDict)
        else:
            #print line
            eventDict[attr] = line.split(":")[2].strip("\r\n")

for event in mEventsList:
    print event["Time"]
    # print event



