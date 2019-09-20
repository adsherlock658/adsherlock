import json
import sys
from subprocess import Popen, PIPE, check_output
from urlparse import urlparse, parse_qsl

def check_is_ad(uri):
    if 'dz.zb' in uri:
        return True, 'mobads'
    if 'gdt_mview' in uri:
        return True, 'gdt'
    if ('/m/ad?' in uri) or ('m/imp?' in uri):
        return True, 'mopub'
    if 'getAd?' in uri:
        return True, 'millennialmedia'
    if '/mads/gma' in uri:
        return True, 'admob'

    return False, None

class HttpRequest(object):
    def __init__(self, method, domain, path_list, key_list, is_ad, ad_type):
        self.method = method
        self.domain = domain
        self.path_list = path_list
        self.key_list = key_list
        self.is_ad = is_ad
        if is_ad:
            self.ad_type = ad_type

    def to_json(self):
        return json.dumps(self.__dict__)

def pcap_line_to_request(line):
    domain, method, uri = line.split()
    uri_parse_result = urlparse(uri)
    path_list = [x for x in uri_parse_result.path.split('/') if x]
    qs_parse_requst = parse_qsl(uri_parse_result.query)
    key_list = [x[0] for x in qs_parse_requst if x]
    is_ad, ad_type = check_is_ad(uri)

    return HttpRequest(method, domain, path_list, key_list, is_ad, ad_type)

def pcap_to_httprequest(filename):
    cmd = ['tshark', '-r', filename, '-Y', 'http.request', '-Tfields', '-e', 'http.host', '-e', 'http.request.method', '-e', 'http.request.uri']
    p = Popen(cmd, stdout=PIPE)
    requests = []
    for line in iter(p.stdout.readline, ''):
        line = line.strip()
        req = pcap_line_to_request(line)
        if req:
            requests.append(req)
        else:
            print("Fatal error: %s" % line)
            sys.exit(1)
    return requests

def httprequest_to_json(httprequest_list, filename):
    request_list = []
    for request in httprequest_list:
        request_list.append(request.__dict__)
    with open(filename, 'w') as fout:
        json.dump(fp=fout, obj=request_list)

def test_HttpRequest():
    method = 'GET'
    domain = 'www.baidu.com'
    path_list = ['a', 'b']
    key_list = ['loc', 'time']
    request = HttpRequest(method, domain, path_list, key_list)
    print(request.to_json())

def test_pcap_to_httprequest():
    filename = '/home/luoy/infocom16/adviser/exps/com.funshion.video.mobile/com.funshion.video.mobile.pcap'
    pcap_to_httprequest(filename)

def test_httprequest_to_json():
    method = 'GET'
    domain = 'www.baidu.com'
    path_list = ['a', 'b']
    key_list = ['loc', 'time']
    r1 = HttpRequest(method, domain, path_list, key_list)
    domain = 'www.baidu2.com'
    r2 = HttpRequest(method, domain, path_list, key_list)
    path_list = ['a', 'c', 'd']
    r3 = HttpRequest(method, domain, path_list, key_list)
    r_list = [r1, r2, r3]
    httprequest_to_json(r_list, 'txt.json')

def main():
    ifname = '/home/luoy/infocom16/adviser/exps/com.shoujiduoduo.ringtone/com.shoujiduoduo.ringtone.pcap'
    ofname = 'request.json'
    requests = pcap_to_httprequest(ifname)
    httprequest_to_json(requests, ofname)

if __name__ == '__main__':
    main()
