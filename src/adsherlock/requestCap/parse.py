import dpkt
import re


pcapfile = open("./log/wireshark_06070922.pcap", "r")
#-parfile = open("./log/uri_parameters.txt", "w")
pcap = dpkt.pcap.Reader(pcapfile)
print pcap.datalink()
# print pcap.readpkts()
# print dpkt.pcap.DLT_LINUX_SLL

for raw_pkt in pcap:
    ts = raw_pkt[0]  # timestamp
    buf = raw_pkt[1]  # frame data

    if pcap.datalink() == dpkt.pcap.DLT_LINUX_SLL:
        eth = dpkt.sll.SLL(raw_pkt)
    else:
        eth = dpkt.ethernet.Ethernet(buf)

    ip = eth.data
    tcp = ip.data

    if tcp.dport == 80 and len(tcp.data) > 0:
        try:
            http = dpkt.http.Request(tcp.data)
            print "At time:", "{0:.6f}".format(ts)
            print "Header:", http.headers
            print "Method:", http.method
            print "Version:", http.version
            print "Body(for post):", http.body
            print "URI:", http.uri

            mark = re.compile('\?')
            # print mark.search(http.uri)
            if mark.search(http.uri):
                print "**************"
                URIParameters = http.uri.split("?")[1].split("&")
                for p in URIParameters:
                    name = p.split("=")[0]
                    value = p.split("=")[1]
                    #print name, value
                   #- parfile.writelines(name+" "+value+"\n")
        except dpkt.Error, e:
            print 'Error parsing packet: %s' % e
            continue

