import time
import os

timeStr = time.strftime('%Y%m%d%H', time.localtime(time.time()))
#timeStr = "2016062022"
pcapfile = "./tcplog/tcpdump."+timeStr+'.pcap'
parseresult = "./tcplog/result.tcpdump."+timeStr+".pcap"

# os.system("tshark -r %s -R \"http.request || http.response\"  -t e > %s" % (pcapfile, parseresult))
os.system("tshark -r %s -Y \"http.request\"  -t e > %s" % (pcapfile, parseresult))

pkts = []
readresult = open(parseresult, "r")

for line in readresult.readlines():
    ls = line.split()
    ts = ls[1]
    pkt = [ts, line]
    pkts.append(pkt)

for pkt in pkts:
    print pkt