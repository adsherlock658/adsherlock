import os
import time

timeStr = time.strftime('%Y%m%d%H',time.localtime(time.time()))
tcpdumplog = "./log/tcpdump."+timeStr+'.pcap'
androidlog = "./log/logcat."+timeStr
clicklog = "../clickdroid/log/samsungS5.getlog.form"

os.system("bash getlog.sh "+tcpdumplog+" "+androidlog+" "+clicklog)
