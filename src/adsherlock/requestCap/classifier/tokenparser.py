from __future__ import division
import re
import os
import numpy as np


pcapfile = "../tcplog/36kr.tcpdump.pcap"
parseresult = "../tcplog/result.36kr.tcpdump.pcap"
arff = "../tcplog/36kr.tcpdump.arff"

# os.system("tshark -r %s -R \"http.request || http.response\"  -t e > %s" % (pcapfile, parseresult))
os.system("tshark -r %s -Y \"http.request\"  -t e > %s" % (pcapfile, parseresult))


# Generate token list for each request and the token set from the log
# imput: pcap
# output: tokensRaw[], tokens
def ReadIn(parseresult):
    tokensRaw = []
    tokens = []
    readresult = open(parseresult, "r")
    for line in readresult.readlines():
        ls = line.split()
        dst = ls[4]
        method = ls[7]
        uri = ls[8]

        urilist = [dst, method]
        pc = []
        pr = []
        mark = re.compile('\?')
        if mark.search(uri):
            page = uri.split("?")[0]
            query = uri.split("?")[1]
            for p in query.split("&"):
                pr.append(p.split("=")[0])
        else:
            page = uri

        pageComponents = page.split("/")
        mindex = len(pageComponents)
        for i in range(1, mindex - 1):
            pc.append(pageComponents[i])
        urilist = urilist + pc + pr

        # add tag for the classifier: 0 for ad request, 1 for non-ad request
        adflag = 0
        for t in urilist:
            if t == "mads":
                adflag = 1
            if t not in tokens:
                tokens.append(t)
        urilist.append(adflag)

        tokensRaw.append(urilist)
    return tokensRaw, tokens


#Generate the arff file for weka's classifier
def arffGeneration(arff):
    writearff = open(arff, "w")
    # dimention of vectors
    d = len(tokens)
    writearff.writelines("@RELATION request\n")
    for i in range(d):
        writearff.writelines("@ATTRIBUTE " + tokens[i] + " NUMERIC" + "\n")
    writearff.writelines("@ATTRIBUTE class {0, 1}\n")
    writearff.writelines("@DATA\n")

    for tkl in tokensRaw:
        tokenVec = [0 for i in range(d)]
        line = ""
        for i in range(d):
            if tokens[i] in tkl:
                tokenVec[i] = 1
            line = line + str(tokenVec[i])+","
        line = line + str(tkl[len(tkl)-1])
        writearff.writelines(line + "\n")

if __name__ == "__name__":
    tokensRaw = []
    tokens = []
    tokensRaw, tokens = ReadIn(parseresult)
    arffGeneration(arff)

