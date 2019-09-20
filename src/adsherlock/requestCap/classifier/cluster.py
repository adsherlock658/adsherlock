from __future__ import division
import re
import os
import numpy as np
from scipy.cluster.vq import kmeans, vq
from tokenparser import ReadIn

pcapfile = "../tcplog/36kr.tcpdump.pcap"
parseresult = "../tcplog/result.36kr.tcpdump.pcap"

# os.system("tshark -r %s -R \"http.request || http.response\"  -t e > %s" % (pcapfile, parseresult))
os.system("tshark -r %s -Y \"http.request\"  -t e > %s" % (pcapfile, parseresult))

readresult = open(parseresult, "r")

tokensRaw = []
tokens = []

tokensRaw, tokens = ReadIn()

#dimention of vectors
d = len(tokens)

ads = []
nonads = []
for tkl in tokensRaw:
    tokenVec = [0 for i in range(d)]
    for i in range(d):
        if tokens[i] in tkl:
            tokenVec[i] = 1
    if tkl[len(tkl)-1] == 0:
        nonads.append(tokenVec)
    else:
        ads.append(tokenVec)

ads = np.array(ads)
nonads = np.array(nonads)

k = 15
codebook,distortion = kmeans(nonads, k)
code, dist = vq(nonads, codebook)

print code, len(nonads), len(code)


for c in range(k):
    print "type:", c
    for i in range(len(code)):
        if code[i] == c:
            #print nonads[i]
            tk = []
            for j in range(len(nonads[i])):
                if nonads[i][j] == 1:
                    tk.append(tokens[j])
            print tk
