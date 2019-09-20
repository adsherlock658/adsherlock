from __future__ import division
import re
import os
import sys
import numpy as np
import copy
import math
from numpy import random
import json

packageName = sys.argv[1]
dir = "/home/caochenhong/adviser/adviser-exp/apps-bak/" + packageName + "/"
desdir = "/home/caochenhong/adviser/adviser-exp/apps/" + packageName + "/"
requestdir = dir + "output"
pagefile = dir + packageName + ".page.txt"
# patternfile = dir + packageName + ".pattern.txt"

# adarff = dir + "ad.com.shoujiduoduo.ringtone.token.arff"
# nonadarff = dir + "nonad.com.shoujiduoduo.ringtone.token.arff"
hostip = "192.168.000.234"
httptype = "HTTP/1.1"
mark = re.compile('\?')

def adpage(pagefile):
    adpages = []
    pagehand = open(pagefile, "r")
    # ad request patterns for groudtruth
    adsregex = re.compile('\/mads\/gma|dz\.zb|gdt_mview|\/m\/ad|\/m\/imp$|\/getAd')

    for page in pagehand.readlines():
        if adsregex.search(page):
            adpages.append(page.split()[0])
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
        # print "link:", link
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
            for i in range(1, mindex):
                pc.append(pageComponents[i])

            token = [request['method'], host] + pc + pr
            # print "page:", page
            if page not in adpages:
                nonads.append(token)
            else:
                ads.append(token)
    return nonads, ads

def noise(ads, nonads, fraction):
    noiseNum = int((fraction/(1-fraction))*(len(ads)))
    nonadsize = len(nonads)
    noiseset = []
    for n in range(noiseNum):
        index = random.random_integers(0, nonadsize-1)
        noiseset.append(nonads[index])
    return noiseset




#  output: # of false positives
def falsepositive(signature, fpset):
    flpositive = 0
    for fp in fpset:
        if set(signature) <= set(fp):
            #print "++++++++++++++++++++++"
            flpositive += 1
    # print "FALSEPOSITVIES:", signature, flpositive
    return flpositive

def BayesSignature(nonads, ads):
    tokenNumDict = {}
    nonadsPoolSize = len(nonads)
    adsPoolSize = len(ads)
    # print "adsize:", adsPoolSize
    # print "nonadssize:", nonadsPoolSize
    for tokens in nonads:
        for t in set(tokens):
            if t not in tokenNumDict:
                tokenNumDict[t] = {}
                tokenNumDict[t]["nonads"] = 0
                tokenNumDict[t]["ads"] = 0
            tokenNumDict[t]["nonads"] += 1
    for tokens in ads:
        for t in set(tokens):
            if t not in tokenNumDict:
                tokenNumDict[t] = {}
                tokenNumDict[t]["nonads"] = 0
                tokenNumDict[t]["ads"] = 0
            tokenNumDict[t]["ads"] += 1

    tokenScoreDict = copy.deepcopy(tokenNumDict)
    for t in tokenNumDict:
        ads = tokenNumDict[t]["ads"]
        nonads = tokenNumDict[t]["nonads"]
        # print t, ads, nonads
        adscore = 0
        nonadscore = 0
        if ads != 0:
            # print ads/adsPoolSize, math.log(ads/adsPoolSize)
            adscore = math.log(ads/adsPoolSize) + 10
        if nonads != 0:
            nonadscore = math.log(nonads/nonadsPoolSize) + 10
        tokenScoreDict[t]['nonads'] = nonadscore
        tokenScoreDict[t]['ads'] = adscore
        # print t, tokenNumDict[t]["ads"], tokenNumDict[t]["nonads"], ads/adsPoolSize, nonads/nonadsPoolSize, adscore, nonadscore
    #print nonadsPoolSize, adsPoolSize
    return tokenScoreDict


if __name__ == "__main__":
    threshold = 2
    allfile = os.listdir(requestdir)
    adpages = adpage(pagefile)
    fraction = 0.3

    # print "adpage:", adpages
    httplist = getHttpFileList(allfile)
    requestLinks = readInHttpRequests(httplist)
    nonads, ads = classify(requestLinks, adpages)

    fractionset = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    for fraction in fractionset:
        print "fraction:", fraction
        scorefile = desdir + "output_score_" + str(fraction) + ".json"
        scoreresult = {}
        noiseset = noise(ads, nonads, fraction)
        noiseads = ads + noiseset
        # print noiseads
        tokenScoreDict = BayesSignature(nonads, noiseads)
        scoreline1 =  "==========================tokenScoreDict===================="
        line2 = "token, adscore, nonadscore"
        #patternhand.writelines(scoreline1 + "\n")
        #patternhand.writelines(line2 + "\n")
        tp = 0
        tn = 0
        fp = 0
        fn = 0
        for nonad in nonads:
            adscore = 0
            nonadscore = 0
            for t in nonad:
                adscore += tokenScoreDict[t]['ads']
                nonadscore += tokenScoreDict[t]['nonads']
            if adscore > nonadscore:
                fp += 1
            else:
                tn += 1

        for ad in noiseads:
            adscore = 0
            nonadscore = 0

            for t in ad:
                adscore += tokenScoreDict[t]['ads']
                nonadscore += tokenScoreDict[t]['nonads']
            if (adscore > nonadscore) and (ad in ads):
                tp += 1
            elif (adscore > nonadscore) and (ad not in ads):
                fp += 1
            elif (adscore < nonadscore)and (ad in ads):
                fn += 1
            elif (adscore < nonadscore)and (ad not in ads):
                tn += 1

        scoreresult['stp'] = tp
        scoreresult['stn'] = tn
        scoreresult['sfp'] = fp
        scoreresult['sfn'] = fn
        with open(scorefile, "w") as json_file:
            json.dump(scoreresult, json_file, sort_keys=True, indent=2)
        print "ads size:", len(ads)
        print "noiseads size:", len(noiseads)
        print "nonadsize:", len(nonads)
        print "tp  fp tn fn", tp, fp, tn, fn
        print "FPR:", fp/(fp+tn)
        for token in tokenScoreDict:
            line = token + " " + ('%.10f' % tokenScoreDict[token]["ads"]) + " " + ('%.10f' % tokenScoreDict[token]["nonads"])
        #patternhand.writelines(line + "\n")