import re
htmlfile = open("/home/caochenhong/adviser/requestCap/emulatorlog/36kr/0708ly/203.208.043.122.00080-192.168.000.234.55307.1467964202-HTTPBODY-001.html")
html = htmlfile.read()

print type(html)

linkregex = re.compile('\"(http:\/\/.*?)\"')

for link in re.findall(linkregex,html):
    print link