import os
import sys

packageName = sys.argv[1]
dir = "/home/caochenhong/adviser/adviser-exp/apps/" + packageName + "/"
#desdir = "/home/caochenhong/adviser/adviser-exp/apps/" + packageName + "/"
# dir = "/home/caochenhong/adviser/adviser/exps4/exps4/" + packageName + "/"
# dir = "/home/caochenhong/adviser/requestCap/emulatorlog/" + packageName + "/"

requestdir = dir + "output"
# pagefile = dir + packageName + ".page.txt"
patternfile = dir + packageName + "_pattern.txt"
newpatternfile = dir + packageName + "_pattern.txt"

rf = open(patternfile, "r")
lineSet = [line.strip() for line in rf.readlines()]
# print lineSet
nonadsDelimiter = "============================nonads==========================="
adsDelimiter = "============================ads==========================="
tokenDelimiter = "==========================tokenScoreDict===================="

scoreindex = lineSet.index(tokenDelimiter)
adindex = lineSet.index(adsDelimiter)
# print adindex, lineSet[adindex]
# print scoreindex, lineSet[scoreindex]
nonads = lineSet[1:adindex]
ads = lineSet[adindex+1:scoreindex]
scores = lineSet[scoreindex+1:len(lineSet)]
nonads = list(set(nonads))
ads = list(set(ads))
# print ads
rf.close()
wf = open(newpatternfile, "w")
wf.writelines(nonadsDelimiter + "\n")
for pattern in nonads:
    ps = pattern.split()
    line = ""
    try:
        line = " ".join([unicode(p) for p in ps])
        wf.writelines(line + "\n")
    except UnicodeDecodeError:
        pass

wf.writelines(adsDelimiter + "\n")
for pattern in ads:
    wf.writelines(pattern + "\n")
wf.writelines(tokenDelimiter + "\n")
for score in scores:
    sp = score.split()
    # print "sp0: ", sp[0]
    try:
        line = unicode(sp[0]) + " " + " ".join(sp[1:len(sp)])
        # print line
        wf.writelines(line + "\n")
    except UnicodeDecodeError:
        pass

wf.close()