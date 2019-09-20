from __future__ import division
import sys
import os
import re
import numpy as np
import copy
import datetime
import json

packageName = sys.argv[1]
# requestdir = "/home/caochenhong/adviser/requestCap/emulatorlog/36kr/0708ly"
# dir = "/home/caochenhong/adviser/adviser-exp/apps/" + packageName + "/"
dir = "/home/caochenhong/adviser/requestCap/emulatorlog/" + packageName + "/"
# dir = "/home/caochenhong/adviser/adviser/exps4/exps4/" + packageName + "/"

pcapfile = dir + packageName + ".pcap"
requestdir = dir + "output"
arff = dir + packageName + ".arff"
pagefile = dir + packageName + ".page.txt"
classifierdata = dir + packageName + ".classifier.txt"
httprequestfile = dir + packageName + ".httprequest.json"
#hostip = "192.168.000.234"
hostip = "010.214.149.162"
httptype = "HTTP/1.1"
mark = re.compile('\?')
pageFilter = ["png", "gif", "jpeg", "svg", "ico", "bmp"]
appNum = 1
# timelist = []
classifierdatafile = open(classifierdata, "w")


def getHttpFileList(allfile):
    httplist = []
    port = re.compile('00080')
    for file in allfile:
        if port.search(file):
            httplist.append(file)
            # timelist.append(file.split('-')[1].split
    # list http files in time order
    httplist = [f[0] for f in sorted([(fn, fn.split('-')[1].split('.')[5]) for fn in httplist], key=lambda r:r[1])]
    return httplist


# output: requestLinks, responseLinks, pageDict
def readInHttpRequests(httplist):
    pageDict = {}
    requestLinks = {}
    responseLinks = {}
    cnt = 0
    requestcounter = 0
    print "lenhttplist:", len(httplist)
    for fileName in httplist:
        fs = fileName.split("-")
        srcip = '.'.join(fs[0].split('.')[0:4])
        src = '.'.join(fs[0].split('.')[0:5])
        dst = '.'.join(fs[1].split('.')[0:5])
        time = fs[1].split('.')[5]
        link = (src, dst, time)
        filehand = open(requestdir + "/" + fileName, "r")

        # processing http requests
        if srcip == hostip:
            requestLinks[link] = {}
            request = {}
            ln = -1
            while True:
                ln += 1
                line = filehand.readline()
                if not line:
                    break
                if ln == 0:
                    #print line
                    line = line.strip()
                    ls = line.split()

                    if len(ls) == 0 or ls[len(ls)-1] != httptype:
                        ln = -1
                        continue
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
                    requestcounter += 1
                    requestLinks[link][request['seq']] = request
                    host = ''
                    if 'Host' in request:
                        host = request['Host']
                    elif 'HOST' in request:
                        host = request['HOST']
                    if mark.search(request['uri']):
                        uri = request['uri'].split("?")
                        para = uri[len(uri) - 1]
                        page = "http://" + host + uri[0]
                    else:
                        urisplit = request['uri'].split('.')
                        #print request
                        if urisplit[len(urisplit) - 1] not in pageFilter:
                            page = "http://" + host + request['uri']
                            para = ""
                        else:
                            continue
                    if page not in pageDict:
                        pageDict[page] = []

                    pageDict[page].append((request['seq'], time, para, src, dst))
                    request = {}
                    ln = -1
            filehand.close()

        # processing http responses
        else:
            if link not in responseLinks:
                responseLinks[link] = {}
                responseLinks[link]['headers'] = []
                responseLinks[link]['bodies'] = []
            if len(fs) > 2:
                responseLinks[link]['bodies'].append(fileName)
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
    print "Page Number:", len(pageDict)
    print "Request Number:", requestcounter
    classifierdatafile.writelines("Request Number: " + str(requestcounter) + "\n")
    classifierdatafile.writelines("Page Number: " + str(len(pageDict)) + "\n")

    return pageDict, requestLinks, responseLinks

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
        print "-".join(link)
        print "________________________________"
        for seq in requestLinks[link]:
            print "+++++++++++++++"
            request = requestLinks[link][seq]
            for x in request:
                print x, ":", request[x]
    '''


def matchRequestResponse(requestLinks, responseLinks):
    map = {}
    htmlregex = re.compile('text\/html')
    for link in requestLinks:
        src = link[0]
        dst = link[1]
        findresponse = 0
        for rlink in responseLinks:
            if rlink[0] == dst and rlink[1] == src:
                findresponse = 1
                break
        if findresponse == 0:
            continue
        seqArr = sorted([int(seq) for seq in requestLinks[link]])
        bodies = responseLinks[rlink]['bodies']
        htmlrequest = [0 for x in range(len(seqArr))]
        htmlbodies = []
        for body in bodies:
            bodyarr = body.split('.')
            if bodyarr[len(bodyarr) - 1] == 'html':
                htmlbodies.append(body)
        for i in range(len(seqArr)):
            request = (link, seqArr[i])
            response = [rlink, i]
            map[request] = response
            requestconent = requestLinks[link][seqArr[i]]
            if 'Accept' in requestconent and htmlregex.search(requestconent['Accept']):
                htmlrequest[i] = 1
        requestIndex = np.nonzero(htmlrequest)[0]

        if len(seqArr) == len(htmlbodies):
            for i in range(len(seqArr)):
                request = (link, seqArr[i])
                body = htmlbodies[i]
                map[request].append(body)
            continue

        for i in range(len(requestIndex)):
            index = requestIndex[i]
            request = (link, seqArr[index])
            if htmlbodies:
                body = htmlbodies[i]
                map[request].append(body)
            if i == len(htmlbodies) - 1:
                break
    return map


def getURL(filename):
    htmlfile = open(requestdir + "/" + filename)
    html = htmlfile.read()
    linkregex = re.compile('\"(http:\/\/.*?)\"')
    andsybol = re.compile('\\\\u0026')
    urls = re.findall(linkregex, html)
    for i in range(len(urls)):
        urls[i], number = andsybol.subn('&', urls[i])
        urls[i] = urls[i].split('?')[0]
    return urls


def getURLfromResponseHtml(pageDict, map):
    pageResponseUrlsDict = {}
    for page in pageDict:
        pageResponseUrlsDict[page] = {}

        #print page
        for pageunit in pageDict[page]:
            src = pageunit[3]
            dst = pageunit[4]
            seq = pageunit[0]
            time = pageunit[1]
            pageResponseUrlsDict[page][seq] = []
            request = ((src, dst, time), seq)
            if request not in map:
                continue
            if len(map[request]) == 3:
                htmlname = map[request][2]
                pageResponseUrlsDict[page][seq] = getURL(htmlname)
        # print page
        # print pageResponseUrlsDict[page]
    return pageResponseUrlsDict


def buildRequestTrees(requestLinks, pageDict, pageResponseUrlsDict):
    unknownReferer = {}
    linksInorder = sorted(requestLinks.keys(), key=lambda r: r[2])
    requestTrees = {}
    locations = {}

    for page in pageDict:
        requestTrees[page] = []

    for link in linksInorder:
        time = link[2]
        for seq in requestLinks[link]:
            request = requestLinks[link][seq]
            host = ''
            if 'Host' in request:
                host = request['Host']
            elif 'HOST' in request:
                host = request['HOST']
            #completepage = "http://" + request['Host'] + request['uri']
            #print 'completepage:', completepage
            if mark.search(request['uri']):
                page = "http://" + host + request['uri'].split("?")[0]
            else:
                page = "http://" + host + request['uri']

            if 'Referer' in request:
                previousPage = request['Referer'].split("?")[0]
                #print previousPage, page, pageDict[previousPage]
                minInterval = sys.maxint
                previousSeq = 0
                if previousPage not in pageDict:
                    if previousPage not in unknownReferer:
                        unknownReferer[previousPage] = []
                        unknownReferer[previousPage].append(seq)
                    continue
                for pageRequest in pageDict[previousPage]:

                    interval = int(pageRequest[1]) - int(time)
                    if interval <= minInterval:
                        minInterval = interval
                        previousSeq = pageRequest[0]
                linkOfRequests = (previousSeq, seq)
                requestTrees[previousPage].append(linkOfRequests)

            for rlink in responseLinks:
                if rlink[0] == link[1] and rlink[1] == link[0]:
                    responseHeaders = responseLinks[rlink]['headers']
                    for response in responseHeaders:
                        if 'Location' in response:
                            locseq = str(seq) + 'loc'
                            locations[int(seq)] = response['Location']
                            locationpage = response['Location'].split('?')[0]
                            if locationpage in pageDict:
                                minInterval = sys.maxint
                                for pageRequest in pageDict[locationpage]:
                                    interval = int(pageRequest[1]) - int(time)
                                    if interval <= minInterval:
                                        minInterval = interval
                                        locationSeq = pageRequest[0]
                                linkOfRequests = (seq, locationSeq)
                                if page in requestTrees:
                                    requestTrees[page].append(linkOfRequests)
                            else:
                                linkOfRequests = (seq, locseq)
                                if page in requestTrees:
                                    requestTrees[page].append(linkOfRequests)

            if page in requestTrees:
                for parentpage in pageResponseUrlsDict:
                    for pseq in pageResponseUrlsDict[parentpage]:
                        if page in pageResponseUrlsDict[parentpage][pseq]:
                            linkOfRequests = (pseq, seq)
                            requestTrees[parentpage].append(linkOfRequests)
                            break
                #print  previousPage, requestTrees[previousPage]
    completeTrees = copy.deepcopy(requestTrees)
    for page in completeTrees:
        temp = []
        visit = []
        for edge in completeTrees[page]:
            temp.append(edge[1])
        while temp:
            seq = temp.pop()
            for pu in requestTrees:
                if pu == page:
                    continue
                else:
                    for edge in requestTrees[pu]:
                        if edge[0] == seq:
                            completeTrees[page].append(edge)
                            visit.append(edge[0])
                            if edge[1] not in visit:
                                temp.append(edge[1])
    return unknownReferer, requestTrees, completeTrees, locations

'''
def featureExtractorBAK(pageDict, requestLinks):
    pageFeatureDict = {}
    for page in pageDict:
        pageFeatureDict[page] = []
        parameterDict = {}
        for pageunit in pageDict[page]:
            seq = pageunit[0]
            time = pageunit[1]
            for link in requestLinks:
                if link[2] == time:
                    if seq in requestLinks[link]:
                        src = link[0]
                        dst = link[1]
                        request = requestLinks[link][seq]
'''


def featureExtractor(pageDict, requestTrees, completeTrees, locations):
    pageFeatureDict = {}
    pagecounter = 0
    adpagecounter = 0
    adrequest = 0
    for page in pageDict:
        pagecounter += 1
        pageFeatureDict[page] = []
        pageparnum = []
        parameterDict = {}
        enumThretholds = [0.5, 0.7]
        diversityThretholds = [10, 40]
        entropythr = 2000
        numeric = 10
        alnumenic = 62
        enumparas = 0
        likelyenum = 0
        nonenum = 0
        lowdiv = 0
        midumdiv = 0
        highdiv = 0
        lowentropy = 0
        highentropy = 0
        avgnum = 0
        totalnum = 0
        maxpvalue = 0
        avgpvalue = 0
        # print page

        # extract path features
        # pathC = page.split('/')
        # lastpc = pathC[len(pathC)-1]


        for pageunit in pageDict[page]:
            para = pageunit[2].split('&')
            pageparnum.append(len(para))
            for pkv in para:
                key = pkv.split('=')[0]
                if key not in parameterDict:
                    parameterDict[key] = []
                if len(pkv.split('=')) <= 1:
                    parameterDict[key].append('NULL')
                else:
                    parameterDict[key].append(pkv.split('=')[1])

        # extract parameter features
        avgsum = 0
        for parameter in parameterDict:
            para = parameterDict[parameter]
            distinctRatio = len(set(para))/len(para)
            disOverApps = len(set(para))/appNum

            if distinctRatio < enumThretholds[0]:
                nonenum += 1
            elif enumThretholds[0] <= distinctRatio <= enumThretholds[1]:
                likelyenum += 1
            else:
                enumparas += 1

            if disOverApps < diversityThretholds[0]:
                highdiv += 1
            elif diversityThretholds[0] <= disOverApps < diversityThretholds[1]:
                midumdiv += 1
            else:
                lowdiv += 1

            lengths = [len(value) for value in para]
            # print lengths
            avg = np.mean(lengths)
            max = np.max(lengths)
            avgsum += avg  # new*************
            if max > maxpvalue:
                maxpvalue = max

            if all([value.isdigit() for value in para]):
                entropy = avg*numeric
            else:
                entropy = avg*alnumenic
            if entropy > entropythr:
                highentropy += 1
            else:
                lowentropy += 1
        avgnum = np.mean(pageparnum)
        totalnum = len(parameterDict)
        avg = avgsum/totalnum
        # print "parameterDict:", parameterDict
        # print "totalnum:", totalnum
        #print "enumparas, likelyenum, nonenum, lowdiv, midumdiv, highdiv,highe,lowe,avg,total", enumparas, likelyenum, nonenum,lowdiv, midumdiv, highdiv,highentropy, lowentropy,avgnum,totalnum
        avghight = 0
        redirectNodes = 0
        tree = completeTrees[page]
        paths = [[s[0], s[1]] for s in requestTrees[page]]
        if paths:
            nodes = list(set(np.concatenate(paths)))
            for node in nodes:
                if node in locations:
                    redirectNodes += 1
            redirectNodesRatio = redirectNodes / len(nodes)
            for edge in tree:
                for path in paths:
                    if edge[0] == path[len(path) - 1]:
                        path.append(edge[1])
            treehights = {}
            #print paths
            for path in paths:
                if path[0] not in treehights:
                    treehights[path[0]] = 0
                if len(path) > treehights[path[0]]:
                    treehights[path[0]] = len(path)
            lengths = [treehights[root] for root in treehights]
            avghight = np.mean(lengths)
        else:
            redirectNodesRatio = 0
            avhight = 0
            #print "avghight", avghight, redirectNodesRatio
        pageFeatureDict[page] = [maxpvalue, avg, enumparas, likelyenum, nonenum, lowdiv, midumdiv, highdiv, highentropy, lowentropy, avgnum,totalnum,avghight, redirectNodesRatio]

        # ad request patterns for groudtruth
        adsregex = re.compile('\/mads\/gma|dz\.zb|gdt_mview|\/m\/ad|\/m\/imp|\/getAd')
        if adsregex.search(page):
            pageFeatureDict[page].append(1)
            adpagecounter += 1
            adrequest += len(pageDict[page])
        else:
            pageFeatureDict[page].append(0)
        # print pageFeatureDict[page]
    print "adrequest:", adrequest
    print "pageCounter:", pagecounter, "adpageCounter:", adpagecounter
    classifierdatafile.writelines("PageCounter: " + str(pagecounter) + "\n")
    classifierdatafile.writelines("AdpageCounter: " + str(adpagecounter) + "\n")
    return pageFeatureDict


#Generate the arff file for weka's classifier
def arffGeneration(pagefile, arff, pageFeatureDict, pageDict):
    writearff = open(arff, "w")
    writepagefile = open(pagefile, "w")
    # dimention of vectors
    features = ['maxpvalue', 'avgpvalue','enumparas', 'likelyenum', 'nonenum', 'lowdiv', 'midumdiv', 'highdiv', 'highentropy', 'lowentropy', 'avgnum', 'totalnum', 'avghight', 'redirectNodesRatio']
    writearff.writelines("@RELATION request\n")
    for feature in features:
        writearff.writelines("@ATTRIBUTE " + feature + " NUMERIC" + "\n")
    writearff.writelines("@ATTRIBUTE class {0, 1}\n")
    writearff.writelines("@DATA\n")
    for page in pageFeatureDict:
        line = ','.join([str(val) for val in pageFeatureDict[page]])
        #print line
        # print page
        # print line
        requestcnt = len(pageDict[page])
        writearff.writelines(line + "\n")
        writepagefile.writelines(page + " " + str(requestcnt) + "\n")
    writearff.close()
    writepagefile.close()


def httpRequestJson(requestLinks):
    file = open(httprequestfile, "w")
    for link in requestLinks:
        for seq in requestLinks[link]:
            try:
                request = json.dumps(requestLinks[link][seq], sort_keys=True, indent=2)
                file.write(request)
            except UnicodeDecodeError:
                pass

if __name__ == "__main__":
    cmdclear = "rm -r " + requestdir
    cmd = "tcpflow -r " + pcapfile + " -e http -T%A.%a-%B.%b%V%v%C%c.%t -o " + requestdir
    os.system(cmdclear)
    os.system(cmd)
    allfile = os.listdir(requestdir)
    httplist = getHttpFileList(allfile)
    pageDict, requestLinks, responseLinks = readInHttpRequests(httplist)

    httpRequestJson(requestLinks)
    map = matchRequestResponse(requestLinks, responseLinks)
    #print map
    pageResponseUrlsDict = getURLfromResponseHtml(pageDict, map)

    time1 = datetime.datetime.now()
    unknownReferer, requestTrees, completeTrees, locations = buildRequestTrees(requestLinks, pageDict,pageResponseUrlsDict)
    # print unknownReferer
    # print "Locations:", locations
    # print "============================requestrees============================"
    # print requestTrees
    pageFeatureDict = featureExtractor(pageDict, requestTrees, completeTrees, locations)
    arffGeneration(pagefile, arff, pageFeatureDict, pageDict)
    time2 = datetime.datetime.now()
    interval = int((time2-time1).total_seconds()*1000)
    print "Time of classifier:", interval
    classifierdatafile.writelines("Time of classifier: " + str(interval) + "\n")
    classifierdatafile.close()

#for  in requestLinks