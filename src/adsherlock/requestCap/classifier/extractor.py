from __future__ import division
import re
import os
import numpy as np

pcapfile = "../tcplog/36kr.tcpdump.pcap"
parseresult = "../tcplog/result.36kr.tcpdump.pcap"

# os.system("tshark -r %s -R \"http.request || http.response\"  -t e > %s" % (pcapfile, parseresult))
os.system("tshark -r %s -Y \"http.request\"  -t e > %s" % (pcapfile, parseresult))

getList = []
postList = []
Flows = []

readresult = open(parseresult, "r")


def readIn():
    for line in readresult.readlines():
        ls = line.split()
        method = ls[7]
        uri = ls[8]

        if method == 'GET':
            getList.append(uri)
        elif method == 'POST':
            postList.append(uri)


# parse a uri, and return two string set, pc[] and pr[]
def uriParse(uri):
    mark = re.compile('\?')
    pc = []
    pr = []
    if mark.search(uri):
        page = uri.split("?")[0]
        query = uri.split("?")[1]
        URIParameters = query.split("&")
        for p in URIParameters:
            kvpair = p.split("=")
            pr.append(kvpair[0])
    else:
        page = uri
    pageComponets = page.split("/")
    mindex = len(pageComponets)
    for i in range(1,mindex-1):
        pc.append('/'+pageComponets[i])
    return pc, pr


# compute the request similarity matrix: distance[n][n]
def requestSimilarityMx(requestlist):
    n = len(requestlist)
    distance = [[0 for col in range(n)] for row in range(n)]
    for i in range(n):
        urii = requestlist[i]
        (pci, pri) = uriParse(urii)
        for j in range(i+1, n):
            urij = requestlist[j]
            (pcj, prj) = uriParse(urij)


            if (pci == [] and pcj == []) and (pri == [] and prj == []):
                #print "pc =[]", urii, urij
                distance[i][j] = 0
                distance[j][i] = 0
                continue
            #print pci, pcj, pri, prj
            pculen = len(np.union1d(pci, pcj))
            prulen = len(np.union1d(pri, prj))
            pcilen = len(np.intersect1d(pci, pcj))
            prilen = len(np.intersect1d(pri, prj))

            if pculen == 0:
                pcsim = 1
            else:
                pcsim = 1 - pcilen/pculen
            if prulen == 0:
                prsim = 0
            else:
                prsim = 1 - prilen/prulen

            dis = (pcsim + prsim)/2
            distance[i][j] = dis
            distance[j][i] = dis
            if i == 36 and j == 37:
                print "36", urii
                print "37", urij
                print pci,pri
                print pcj,prj
                print "distance:",pcsim,prsim,distance[36][37]
    return distance


# divide flows according to distance matrix, return flow sets: Flows[]
def flowSets(distance):
    #distance = np.array(distance)
    #indx = np.nonzero(distance<0.5)
    #print indx
    #for i in range(len(indx[0])):
    #    print distance[indx[0][i]][indx[1][i]]
    indexes = []
    n = len(distance)
    visit = [0 for i in range(n)]
    merge = [0 for i in range(n)]

    for i in range(n):
        index = [i]
        for j in range(i+1, n):
            if distance[i][j] < 0.5:
                index.append(j)
        indexes.append(index)

    for i in range(n):
        if visit[i] == 1:
            continue
        else:
            merge[i] = 1
            for j in range(n):
                if visit[j] == 1:
                    continue
                if len(np.intersect1d(indexes[i], indexes[j])) > 0:
                    visit[j] = 1
                    indexes[i] = np.union1d(indexes[i], indexes[j])
    print visit
    print merge
    flowset = []
    for i in range(n):
        if merge[i] == 1:
            #print i, indexes[i]
            flowset.append(indexes[i])
    return flowset

def patternExtract(flowset):
    for set in flowset:
        print "set:",set
        for i in set:
            print getList[i]


if __name__=="__main__":
    readIn()
    distance = requestSimilarityMx(getList)
    # print distance
    flowset = flowSets(distance)
    patternExtract(flowset)