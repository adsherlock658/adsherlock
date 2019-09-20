import sys
import os
import re

requestdir = "/home/caochenhong/adviser/requestCap/emulatorlog/36kr/output"

port = re.compile('00080')
allfile = os.listdir(requestdir)
hostip = "010.000.003.015"
httptype = "HTTP/1.1"
httplist = []
pageDict = {}
requestLinks = {}
responseLinks = {}
cnt = 0
mark = re.compile('\?')
pageFilter = ["png", "gif", "jpeg", "svg", "ico", "bmp"]
# timelist = []

for file in allfile:
    if port.search(file):
        httplist.append(file)
        # timelist.append(file.split('-')[1].split('.')[5])

for file in httplist:
    fs = file.split("-")
    srcip = '.'.join(fs[0].split('.')[0:4])
    src = '.'.join(fs[0].split('.')[0:5])
    dst = '.'.join(fs[1].split('.')[0:5])
    time = fs[1].split('.')[5]
    link = (src, dst, time)
    filehand = open(requestdir + "/" + file, "r")

    #print src, dst,time
    #print file
    #if srcip != hostip:
        #continue
    #request
    if srcip == hostip:
        requestLinks[link] = []
        request = {}
        ln = -1
        while True:
            ln += 1
            line = filehand.readline()
            if not line:
                break
            if ln == 0:
                ls = line.split()
                request['method'] = ls[0]
                request['uri'] = ls[1]
                request['seq'] = cnt
                cnt += 1
                #print line
                #print ls
            else:
                ls = line.split(":")
                request[ls[0]] = ":".join(ls[1:len(ls)]).strip()
                #print ls
            if not line.strip():
                requestLinks[link].append(request)
                if mark.search(request['uri']):
                    page = "http://" + request['Host'] + request['uri'].split("?")[0]
                else:
                    urisplit = request['uri'].split('.')
                    if urisplit[len(urisplit) - 1] not in pageFilter:
                        page = "http://" + request['Host'] + request['uri']
                if page not in pageDict:
                    pageDict[page] = []
                pageDict[page].append((request['seq'], time))
                request = {}
                ln = -1

        filehand.close()
    #response
    else:
        if link not in responseLinks:
            responseLinks[link] = {}
            responseLinks[link]['headers'] = []
            responseLinks[link]['bodies'] = []
        if len(fs) > 2:
            responseLinks[link]['bodies'].append(file)
        else:
            empline = 0
            ln = -1
            flag = 0
           # response = {}
            while True:
                line = filehand.readline()
                ls = line.split()
                #print line
                if not line:
                    break
                #print ls
                if not line.strip():
                    if flag == 1:
                        responseLinks[link]['headers'].append(response)
                        flag = 0
                    else:
                        continue
                elif ls[0] == httptype:
                    response = {}
                    response['code'] = ls[1]
                    response['status'] = ls[2]
                    flag = 1
                elif flag == 1:
                    ls = line.split(":")
                    response[ls[0]] = ":".join(ls[1:len(ls)]).strip()
            filehand.close()

'''
for link in responseLinks:
    print link
    print "_________________________________"
    for header in responseLinks[link]['headers']:
        print "+++++++++++++++"
        for x in header:
            print x, ":", header[x]
    print responseLinks[link]['bodies']
'''

'''
for link in requestLinks:
    for request in requestLinks[link]:
        print "+++++++++++++++"
        for y in x:
            print y, ":", x[y]
'''

#print pageDict

linksInorder = sorted(requestLinks.keys(), key=lambda r: r[2])

requestTrees = {}
for page in pageDict:
    requestTrees[page] = []

for link in linksInorder:
    time = link[2]
    for request in requestLinks[link]:
        seq = request['seq']
        if mark.search(request['uri']):
            page = "http://" + request['Host'] + request['uri'].split("?")[0]
        else:
            page = "http://" + request['Host'] + request['uri']
        if 'Referer' in request:
            previousPage = request['Referer']
            #print request['Referer'], page
            minInterval = sys.maxint
            previousSeq = 0
            for pageRequest in pageDict[previousPage]:

                interval = int(pageRequest[1]) - int(time)
                if interval <= minInterval:
                    minInterval = interval
                    previousSeq = pageRequest[0]
            linkOfRequests = (previousSeq, seq)
            requestTrees[previousPage].append(linkOfRequests)
print requestTrees


#for  in requestLinks