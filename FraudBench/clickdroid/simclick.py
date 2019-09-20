import sys
import os

inevlog = open("./inputevent.log","r")
outevsh = open("./outev.sh","w")
cmdlist = []

for line in inevlog.readlines():
    ls = line.split()
    if ls == []:
        continue
    names = ls[0]
    types = int(ls[1],16)
    codes = int(ls[2],16)
    values = int(ls[3],16)

    cmd = "sendevent "+names+" "+str(types)+" "+str(codes)+" "+str(values)
    cmdlist.append(cmd)

for cmd in cmdlist:
    print cmd
    outevsh.writelines(cmd+'\n')

inevlog.close()
outevsh.close()


