from gzip import GzipFile
from binascii import unhexlify
from StringIO import StringIO

zipfile =  open("./gzipcode.temp", "r")
#hexdata = ''.join(line for line in zipfile.readlines())
dataline = []
for line in zipfile.readlines():
    line = line.strip('\n')
    dataline.append(line)

hexdata = ''.join(line for line in dataline)
print hexdata
print GzipFile(fileobj=StringIO(unhexlify(hexdata))).read()
#print unhexlify(hexdata)