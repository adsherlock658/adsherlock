from __future__ import division
import re
import os
import numpy as np
import copy
import math

dir = "/home/caochenhong/adviser/adviser/exps.bak/com.shoujiduoduo.ringtone/"
requestdir = dir + "output"
pagefile = dir + "com.shoujiduoduo.ringtone.page.txt"
result = dir + "com.shoujiduoduo.ringtone_result.txt.form"
patternfile = dir + "com.shoujiduoduo.ringtone_pattern.txt"
# adarff = dir + "ad.com.shoujiduoduo.ringtone.token.arff"
# nonadarff = dir + "nonad.com.shoujiduoduo.ringtone.token.arff"
hostip = "192.168.000.234"
httptype = "HTTP/1.1"
mark = re.compile('\?')


def adpage(pagefile, result):
    adpages = []
    pages = []
    results = []
    pagehand = open(pagefile, "r")
    resulthand = open(result, "r")
    for line in pagehand.readlines():
        pages.append(line)
    for line in resulthand.readlines():
        ls = line.split(',')
        truth = ls[1]
        prediction = ls[2]
        flag = truth.split(":")[1]
        results.append(flag)
    for i in range(len(pages)):
        if results[i] == '1':
            adpages.append(pages[i].strip())
    return adpages


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


def readInHttpRequests(httplist):
    requestLinks = {}
    cnt = 0
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
            #print fileName
            while True:
                ln += 1
                line = filehand.readline()
                if not line:
                    break
                if ln == 0:
                    #print line
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
                    requestLinks[link][request['seq']] = request
                    request = {}
                    ln = -1
            filehand.close()
    return requestLinks


def classify(requestLinks, adpages):
    nonads = []
    ads = []
    for link in requestLinks:
        for seq in requestLinks[link]:
            request = requestLinks[link][seq]
            host = ''
            tokens = []
            if 'Host' in request:
                host = request['Host']
            elif 'HOST' in request:
                host = request['HOST']

            pc = []
            pr = []
            if mark.search(request['uri']):
                uri = request['uri'].split("?")
                para = uri[len(uri)-1]
                for p in para.split("&"):
                    pr.append(p.split("=")[0])
            else:
                uri = [request['uri']]

            page = "http://" + host + uri[0]
            pageComponents = uri[0].split("/")
            mindex = len(pageComponents)
            for i in range(1, mindex - 1):
                pc.append(pageComponents[i])

            token = [request['method'], host] + pc + pr

            if page not in adpages:
                nonads.append(token)
            else:
                ads.append(token)
    return nonads, ads


''' generating boolean vector for k-means
def cluster(tokenset, arff):
    tokenalpha = []
    resultTokens = []
    for token in tokenset:
        for t in token:
            if t not in tokenalpha:
                tokenalpha.append(t)

    writearff = open(arff, "w")
    # dimention of vectors
    d = len(tokenalpha)
    writearff.writelines("@RELATION request\n")
    for i in range(d):
        writearff.writelines("@ATTRIBUTE " + tokenalpha[i] + " NUMERIC" + "\n")
    writearff.writelines("@ATTRIBUTE class {0, 1}\n")
    writearff.writelines("@DATA\n")

    for tkl in tokenset:
        tokenVec = [0 for i in range(d)]
        line = ""
        for i in range(d):
            if tokenalpha[i] in tkl:
                tokenVec[i] = 1
        resultTokens.append(tokenVec)
        line = ",".join([str(i) for i in tokenVec])
        writearff.writelines(line + "\n")
    writearff.close()
    return resultTokens
'''


def signature_generating(tokenset):
    n = len(tokenset)
    signature = tokenset[0]
    if n == 1:
        return signature

    for i in range(1, n):
        signature = np.intersect1d(signature, tokenset[i])
    return signature


#  output: # of false positives
def falsepositive(signature, fpset):
    #print "in falsepositive():"
    #print signature
    flpositive = 0
    for fp in fpset:
        if set(signature) <= set(fp):
            #print "++++++++++++++++++++++"
            flpositive += 1
    return flpositive

'''
def cluster(tokenset, fpset):
    threthold = 2
    n_clusters = len(tokenset)
    clusterSet = [[i] for i in range(n_clusters)]
    clusterDict = {}
    print "before:", clusterSet
    for i in range(n_clusters):
        for j in range(i+1, n_clusters):
            pair = [tokenset[i], tokenset[j]]
            signature = signature_generating(pair)
            flpositive = falsepositive(signature, fpset)
            if flpositive <= threthold:
                clusterDict[(i, j)] = flpositive
          # print i, j, ":", signature, flpositive
    # print clusterDict
    while True:
        minfp = min(clusterDict[tset] for tset in clusterDict)
        print "minfp:", minfp, len(clusterSet)
        if minfp >= threthold or len(clusterSet) == 1:
            break
        print "+++++++++++++++++="
        mergesets = []
        for tset in clusterDict.keys():
            if clusterDict[tset] == minfp:
                del clusterDict[tset]
                tset = list(tset)
                #minset = tset
                # deleteSet = [list(x) for x in list(itt.subsets(tset))]
                for t in clusterSet:
                    if set(t) < set(tset):
                        clusterSet.remove(t)
                mergesets.append(tset)
                clusterSet.append(tset)
        print "clusterSet:", clusterSet

        for tset in mergesets:
            for x in clusterSet:
                if tset == x:
                    continue
                newset = set(tset + x)
                pair = [tokenset[i] for i in newset]
                signature = signature_generating(pair)
                flpositive = falsepositive(signature, fpset)
                if flpositive <= threthold:
                    clusterDict[tuple(newset)] = flpositive

        print xxx
    print "after:", clusterSet
    print signature_generating(tokenset)
'''


def cluster(tokenset, fpset):
    threthold = 2
    n_clusters = len(tokenset)
    clusterSet = [[i] for i in range(n_clusters)]
    clusterDict = {}
    print "before:", clusterSet
    for i in range(n_clusters):
        for j in range(i+1, n_clusters):
            pair = [tokenset[i], tokenset[j]]
            signature = signature_generating(pair)
            flpositive = falsepositive(signature, fpset)
            if flpositive <= threthold:
                clusterDict[(i, j)] = flpositive

          # print i, j, ":", signature, flpositive
    # print clusterDict
    preiousclusterSet = copy.deepcopy(clusterSet)

    # print "clusterDict:", clusterDict

    while True:
        minfp = min(clusterDict[tset] for tset in clusterDict)
        minset = []
        #print "minfp:", minfp, len(clusterSet)
        if minfp >= threthold or len(clusterSet) == 1:
            break
        #print "+++++++++++++++++="
        for tset in clusterDict.keys():
            if clusterDict[tset] == minfp:
                #print "minset:", tset, clusterDict[tset]
                del clusterDict[tset]
                tset = list(tset)
                minset = tset
                # deleteSet = [list(x) for x in list(itt.subsets(tset))]
                for t in clusterSet:
                    #print t, tset
                    if set(t) <= set(tset):
                        clusterSet.remove(t)
                    elif set(t) > set(tset):
                        break
                if set(t) > set(tset):
                    continue
                clusterSet.append(tset)
                break

        if sorted(preiousclusterSet) == sorted(clusterSet):
            print clusterDict
            break
        preiousclusterSet = copy.deepcopy(clusterSet)

        for x in clusterSet:
            if minset == x or set(x) < set(minset):
                continue
            newset = set(minset + x)
            pair = [tokenset[i] for i in newset]
            signature = signature_generating(pair)
            flpositive = falsepositive(signature, fpset)
            if flpositive <= threthold:
                clusterDict[tuple(newset)] = flpositive
                #print minset, x, signature, flpositive
        #print "clusterSet:", clusterSet

    print "after:", clusterSet
    return clusterSet


def pattern(clusterset, tokenset, patternhand):
    for indexset in clusterset:
        tokensets = []
        for i in indexset:
            tokensets.append(tokenset[i])
        print "**************"
        print indexset
        signature = signature_generating(tokensets)
        line = ",".join(signature)
        print line
        patternhand.writelines(line+"\n")


def BayesSignature(nonads, ads):
    tokenNumDict = {}
    nonadsPoolSize = len(nonads)
    adsPoolSize = len(ads)

    for tokens in nonads:
        for t in set(tokens):
            if t not in tokenNumDict:
                tokenNumDict[t] = {}
                tokenNumDict[t]["nonads"] = 1
                tokenNumDict[t]["ads"] = 1
            tokenNumDict[t]["nonads"] += 1
    for tokens in ads:
        for t in set(tokens):
            if t not in tokenNumDict:
                tokenNumDict[t] = {}
                tokenNumDict[t]["nonads"] = 1
                tokenNumDict[t]["ads"] = 1
            tokenNumDict[t]["ads"] += 1

    tokenScoreDict = copy.deepcopy(tokenNumDict)
    for t in tokenNumDict:
        ads = tokenNumDict[t]["ads"]
        nonads = tokenNumDict[t]["nonads"]
        adscore = 0
        nonadscore = 0
        if ads != 0:
            adscore = - math.log(ads/adsPoolSize)
        if nonads != 0:
            nonadscore = - math.log(nonads/nonadsPoolSize)
        tokenScoreDict[t]['nonads'] = nonadscore
        tokenScoreDict[t]['ads'] = adscore
        # print t, tokenNumDict[t]["ads"], tokenNumDict[t]["nonads"], ads/adsPoolSize, nonads/nonadsPoolSize, adscore, nonadscore
    #print nonadsPoolSize, adsPoolSize
    return tokenScoreDict


if __name__ == "__main__":
    allfile = os.listdir(requestdir)
    adpages = adpage(pagefile, result)
    httplist = getHttpFileList(allfile)
    requestLinks = readInHttpRequests(httplist)
    nonads, ads = classify(requestLinks, adpages)
    # resultTokens = cluster(nonads, nonadarff)
   # print ads
    patternhand = open(patternfile, "w")
    nonadclusterSet = cluster(nonads, ads)
    nonadline = "============================nonads==========================="
    patternhand.writelines(nonadline + "\n")
    pattern(nonadclusterSet, nonads, patternhand)
    adline = "============================ads==========================="
    print adline
    patternhand.writelines(adline + "\n")
    adclusterSet = cluster(ads, nonads)
    pattern(adclusterSet, ads, patternhand)

    tokenScoreDict = BayesSignature(nonads, ads)
    scoreline1 =  "==========================tokenScoreDict===================="
    line2 = "token, adscore, nonadscore"
    patternhand.writelines(scoreline1 + "\n")
    patternhand.writelines(line2 + "\n")
    for token in tokenScoreDict:
        line = token + " " + ('%.10f' % tokenScoreDict[token]["ads"]) + " " + ('%.10f' % tokenScoreDict[token]["nonads"])
        patternhand.writelines(line + "\n")