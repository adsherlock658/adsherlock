import os
import time

timeStr = time.strftime('%Y%m%d%H', time.localtime(time.time()))
androidtpdlog = "/sdcard/tcpdump."+timeStr+'.pcap'
tcpdumplog = "./tcplog/tcpdump."+timeStr+'.pcap'
parseresult = "./tcplog/result.tcpdump."+timeStr+".pcap"

androidlog = "./tcplog/logcat."+timeStr
# clicklog = "../clickdroid/log/samsungS5.062111.form"
clicklog = "../clickdroid/log/nexus4.getlog.form"
os.system("bash -x getlog.sh "+androidtpdlog+" "+tcpdumplog+" "+parseresult+" "+androidlog+" "+clicklog)
