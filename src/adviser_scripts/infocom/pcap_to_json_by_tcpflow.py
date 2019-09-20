import json
import os
from cStringIO import StringIO
from mimetools import Message
from subprocess import check_output, Popen, PIPE, call

import re

import shutil
from urlparse import urlparse, parse_qsl

"""
parse pcap file by tcp flow.
output both the request and response
"""
class RequestFingerprint(object):
    def __init__(self, **kwargs):
        self.time = kwargs['time']
        src_ip = kwargs['src_ip']
        src_port = kwargs['src_port']
        dst_ip = kwargs['dst_ip']
        dst_port = kwargs['dst_port']
        self.link = (src_ip, src_port, dst_ip, dst_port)
        self.uri = kwargs['uri']

    def __eq__(self, other):
        return (self.link == other.link) and (self.uri == other.uri)

class ResponseFingerprint(object):
    def __init__(self, **kwargs):
        self.time = kwargs['time']
        src_ip = kwargs['src_ip']
        src_port = kwargs['src_port']
        dst_ip = kwargs['dst_ip']
        dst_port = kwargs['dst_port']
        self.link = (src_ip, src_port, dst_ip, dst_port)
        self.date = kwargs['date']

    def __eq__(self, other):
        return (self.link == other.link) and (self.date == other.date)

def is_binary_file(filename):
    binary_file_suffix = ['.svg', '.ico', '.png', '.jpg', '.gif', '.m4v']
    for suffix in binary_file_suffix:
        if filename.endswith(suffix):
            return True
    return False

class HttpAction(object):
    def __init__(self, srcip, srcport, dstip, dstport, type):
        self.link = (srcip, srcport, dstip, dstport)
        self.type = type

    def upadte_request(self, request):
        self.uri = request['request_uri']
        self.finger_print = (self.link, self.uri)
        self.referer = request.get('referer')
        self.method = request['request_method']
        self.domain = request['host']
        uri_parse_result = urlparse(self.uri)
        self.path_list = [x for x in uri_parse_result.path.split('/') if x]
        qs_parse_requst = parse_qsl(uri_parse_result.query)
        self.key_list = [x[0] for x in qs_parse_requst if x]

    def update_response(self, response):
        self.date = response['date']
        self.finger_print = (self.link, self.date)
        self.location = response.get('location')
        body_file = response.get('body_file')
        if body_file:
            if not is_binary_file(body_file):
                with open(os.path.join('tcpflow_tmp', body_file), 'r') as fin:
                    self.body = fin.read()
            else:
                self.body = None
        else:
            self.body = None

        if self.body:
            r = re.compile(r'\"(http:\/\/.*?)\"')
            urls = r.findall(self.body)
            if urls:
                self.urls = urls
            else:
                self.urls = None
        else:
            self.urls = None

def clear_tmp(output_dir):
    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)

def parse_by_tcpflow(pcap_file, output_dir):
    cmd = ['tcpflow', '-r', pcap_file, '-e', 'http', '-T%A-%a-%B-%b-%t', '-o', output_dir]
    # cmd = ['tcpflow', '-r', pcap_file, '-e', 'http', '-o', output_dir]
    call(cmd)

def get_all_tcp_output_files(output_dir):
    for file_name in os.listdir(output_dir):
        yield os.path.join(output_dir, file_name)

def get_httpfile_list(output_dir):
    all_file_list = get_all_tcp_output_files(output_dir)
    http_file_list = [f for f in all_file_list if '00080' in f]
    # httplist = [f[0] for f in \
    #             sorted([(fn, fn.split('-')[1].split('.')[5]) for fn in http_file_list],
    #                    key=lambda r: r[1])]
    return http_file_list


def is_request(srcip):
    return srcip == "10.214.149.162"
    # return srcip == '192.168.0.234'

def is_http_request_header(request_text_block):
    method_list = ['GET', 'POST', 'PUT', 'DELETE']
    for method in method_list:
        if request_text_block.startswith(method):
            return True

    return False

def process_reqeust_textblock(request_text_block):
    request_line, header_alone = request_text_block.split('\r\n', 1)
    headers = Message(StringIO(header_alone))
    method, uri, http_version = request_line.split()
    request = {}
    request.update(headers.dict)
    request['request_method'] = method
    request['request_uri'] = uri
    return request

def process_request_file(http_file):
    request_list = [x for x in http_file.read().split('\r\n\r\n') if x]
    request_dict_list = []
    for request in request_list:
        try:
            if not is_http_request_header(request):
                continue
            request_obj = process_reqeust_textblock(request)
            request_dict_list.append(request_obj)
        except:
            print 'request file in error: ', http_file.name
            raise

    return request_dict_list

def extract_response_text_block(data):
    r = re.compile(r'(HTTP/1.1.*\r\n(?:\w.*\r\n)*\r\n)')
    return r.findall(data)

def process_response_textblock(response_text_block):
    response_line, header_alone = response_text_block.split('\r\n', 1)
    version, code = response_line.split()[0:2]
    headers = Message(StringIO(header_alone))
    response = {}
    response.update(headers.dict)
    response['code'] = code
    return response

def process_response_file(http_file):
    # print(http_file.name)
    data = http_file.read()
    response_list = extract_response_text_block(data)
    response_dict_list = []
    for response in response_list:
        try:
            response_obj = process_response_textblock(response)
            # print(response_obj['date'], response_obj['code'])
            response_dict_list.append(response_obj)
        except:
            print 'response file in error: ', http_file.name
            raise

    return response_dict_list

def merge_reponse_responseBody_dict(link_responseList_dict, link_responseBoydList_dict):
    for link, response_list in link_responseList_dict.items():
        if link not in link_responseBoydList_dict:
            print('No response body file for the response')
        else:
            responseBody_list = link_responseBoydList_dict[link]
            for responseBody in responseBody_list:
                responseId = int(responseBody.split('-')[-1].split('.')[0])
                try:
                    response = response_list[responseId-1]
                    response['body_file'] = responseBody
                except:
                    print len(response_list)
                    print responseId

def get_normal_ip(ip):
    tokens = ip.split('.')
    tokens = [str(int(token)) for token in tokens]
    return '.'.join(tokens)

def parse_http_file_list(http_file_list):
    link_requestList_dict = {}
    link_responseList_dict = {}
    link_responseBodyList_dict = {}
    for http_file in http_file_list:
        filename = os.path.basename(http_file)
        fs = filename.split("-")
        srcip, srcport, dstip, dstport, tcp_flow_time = fs[0:5]
        srcip = get_normal_ip(srcip)
        srcport = str(int(srcport))
        dstip = get_normal_ip(dstip)
        dstport = str(int(dstport))
        link = (srcip, srcport, dstip, dstport)

        with open(http_file, 'r') as fin:
            if is_request(srcip):
                if len(fs) != 5:
                    raise RuntimeError("Found an unexpected reqeust file")
                if link in link_requestList_dict:
                    raise RuntimeError("Unexpected a same link")
                request_list = process_request_file(fin)
                link_requestList_dict[link] = request_list
            else:
                if len(fs) == 7:
                    if link not in link_responseBodyList_dict:
                        link_responseBodyList_dict[link] = []
                    link_responseBodyList_dict[link].append(filename)
                elif len(fs) == 5:
                    response_list = process_response_file(fin)
                    link_responseList_dict[link] = response_list
                else:
                    raise RuntimeError("Found an unexpected response file")

    merge_reponse_responseBody_dict(link_responseList_dict, link_responseBodyList_dict)

    return link_requestList_dict, link_responseList_dict

def get_request_and_response_list(link_requestList_dict, link_responseList_dict):
    request_all_list = []
    for link, request_list in link_requestList_dict.items():
        for request in request_list:
            request['link'] = request
        request_all_list.extend(request_list)
    response_all_list = []
    for link, response_list in link_responseList_dict.items():
        for response in response_list:
            response['link'] = response
        response_all_list.extend(response_list)

    return request_all_list, response_all_list

def get_request_by_tshark(pcap_file):
    request_list = []
    cmd = ['tshark', '-r', pcap_file, '-Y', 'http.request', '-T', 'fields',
           '-e', 'frame.time_relative', '-e', 'ip.src', '-e', 'tcp.srcport',
           '-e', 'ip.dst', '-e', 'tcp.dstport', '-e', 'http.request.uri']
    p = Popen(cmd, stdout=PIPE)
    for line in iter(p.stdout.readline, ''):
        time, srcip, srcport, dstip, dstport, uri = line.split()
        request = RequestFingerprint(time=time, src_ip=srcip, src_port=srcport, dst_ip=dstip, dst_port=dstport, uri=uri)
        request_list.append(request)

    return request_list

def get_response_by_tshark(pcap_file):
    response_list = []
    cmd = ['tshark', '-r', pcap_file, '-Y', 'http.response', '-T', 'fields',
           '-e', 'frame.time_relative', '-e', 'ip.src', '-e', 'tcp.srcport',
           '-e', 'ip.dst', '-e', 'tcp.dstport', '-e', 'http.date']
    p = Popen(cmd, stdout=PIPE)
    for line in iter(p.stdout.readline, ''):
        tokens = line.split()
        time, srcip, srcport, dstip, dstport = tokens[0:5]
        date = ' '.join(tokens[5:])
        response = ResponseFingerprint(time=time, src_ip=srcip, src_port=srcport, dst_ip=dstip, dst_port=dstport, date=date)
        response_list.append(response)

    return response_list

def get_seq_finder(request_fingerprint_list, response_fingerprint_list):
    time_obj_dict = {}
    time_list = []
    for request_fingerprint in request_fingerprint_list:
        time = float(request_fingerprint.time)
        if time in time_obj_dict:
            raise RuntimeError("Same time for two http event")
        time_obj_dict[time] = request_fingerprint
        time_list.append(time)

    for response_fingerprint in response_fingerprint_list:
        time =  float(response_fingerprint.time)
        if time in time_obj_dict:
            raise RuntimeError("Same time for two http event")
        time_obj_dict[time] = response_fingerprint
        time_list.append(time)

    time_list.sort()

    fingerprint_seq_dict = {}
    for index, time in enumerate(time_list):
        obj = time_obj_dict.get(time)
        if isinstance(obj, RequestFingerprint):
            finger_print = (obj.link, obj.uri)
        elif isinstance(obj, ResponseFingerprint):
            finger_print = (obj.link, obj.date)
        else:
            raise RuntimeError("No type detected")
        fingerprint_seq_dict[finger_print] = index

    def seq_finder(http_action):
        if http_action.finger_print not in fingerprint_seq_dict:
            print('Could not found seq for %s' % http_action.date)
            return -1
        return fingerprint_seq_dict[http_action.finger_print]

    return seq_finder

def linearize_all_httpactions(link_requestList_dict, link_responseList_dict, seq_finder):
    httpaction_list = []
    for link, requestList in link_requestList_dict.items():
        for request in requestList:
            httpaction = HttpAction(link[0], link[1], link[2], link[3], 'request')
            httpaction.upadte_request(request)
            seq = seq_finder(httpaction)
            if seq == -1:
                continue
            httpaction.seq = seq
            httpaction_list.append(httpaction)

    for link, responseList in link_responseList_dict.items():
        for response in responseList:
            httpaction = HttpAction(link[0], link[1], link[2], link[3], 'response')
            httpaction.update_response(response)
            seq = seq_finder(httpaction)
            if seq == -1:
                continue
            httpaction.seq = seq
            httpaction_list.append(httpaction)

    return httpaction_list

def show_data(link_requestList_dict, link_responseList_dict, request_all_list, response_all_list, request_fingerprint_list,
              response_fingerprint_list):
    total_request_by_tcpflow = len(request_all_list)
    total_response_by_tcpflow = len(response_all_list)
    total_request_by_tshark = len(request_fingerprint_list)
    total_response_by_tshark = len(response_fingerprint_list)

    print("request count by tcpflow: %d\nresponse count by tcpflow: %d\nrequest count by tshark: %d\n"
          "response count by tshark: %d" % (total_request_by_tcpflow, total_response_by_tcpflow,
                                              total_request_by_tshark, total_response_by_tshark))

    for link, request_list in link_requestList_dict.items():
        print("request count by tcpflow of %s: %d" % (link, len(request_list)))

    for link, response_list in link_responseList_dict.items():
        print("response count by tcpflow of %s: %d" % (link, len(response_list)))

    link_requestfingerprintList_dict = {}
    for request_fingerprint in request_fingerprint_list:
        link = request_fingerprint.link
        if link not in link_requestfingerprintList_dict:
            link_requestfingerprintList_dict[link] = [request_fingerprint]
        else:
            link_requestfingerprintList_dict[link].append(request_fingerprint)

    link_responsefingerprintList_dict = {}
    for response_fingerprint in response_fingerprint_list:
        link = response_fingerprint.link
        if link not in link_responsefingerprintList_dict:
            link_responsefingerprintList_dict[link] = [response_fingerprint]
        else:
            link_responsefingerprintList_dict[link].append(response_fingerprint)

    for link, request_fingerprint_list in link_requestfingerprintList_dict.items():
        print("request count by tshark of %s: %d" % (link, len(request_fingerprint_list)))

    for link, response_fingerprint_list in link_responsefingerprintList_dict.items():
        print("response count by tshark of %s: %d" % (link, len(response_fingerprint_list)))

    # link = ('203.208.40.45', '80', '192.168.0.234', '56568')
    # response_list = link_responseList_dict[link]
    # response_fingerprint_list = link_responsefingerprintList_dict[link]
    # response_date_list = [response['date'] for response in response_list]
    # sorted(response_date_list)
    # response_fingerprint_date_list = [response.date for response in response_fingerprint_list]
    # sorted(response_fingerprint_date_list)
    # for date in response_date_list:
    #     print(date)
    #
    # print('---')
    # for date in response_fingerprint_date_list:
    #     print(date)
    # print('---')
    #
    # for date in response_date_list:
    #     if date not in response_fingerprint_date_list:
    #         print(date)

def httpaction_to_dict(o):
    if o.type == 'request':
        return dict(type=o.type, srcip=o.link[0], srcport=int(o.link[1]),
                    dstip=o.link[2], dstport=int(o.link[3]), seq=o.seq, uri=o.uri,
                    referer=o.referer, method=o.method, domain=o.domain, path_list=o.path_list, key_list=o.key_list)
    else:
        return dict(type=o.type, srcip=o.link[0], srcport=int(o.link[1]),
                    dstip=o.link[2], dstport=int(o.link[3]), seq=o.seq, date=o.date,
                    location=o.location, urls=o.urls)

def httpactions_to_file(httpaction_list, outputfile):
    httpaction_json_list = []
    for httpaction in httpaction_list:
        httpaction_json_list.append(httpaction_to_dict(httpaction))
    httpaction_json_list.sort(key=lambda httpaction: httpaction['seq'])
    import json
    with open(outputfile, 'w') as fout:
        json.dump(httpaction_json_list, fp=fout, indent=4)

def test():
    dirname = os.path.basename(os.getcwd())
    pcap_file = dirname + '.pcap'
    output_dir = 'tcpflow_tmp'
    clear_tmp(output_dir)
    parse_by_tcpflow(pcap_file, output_dir)
    http_list = get_httpfile_list(output_dir)
    link_requestList_dict, link_responseList_dict = parse_http_file_list(http_list)
    request_list, response_list = get_request_and_response_list(link_requestList_dict, link_responseList_dict)
    request_fingerprint_list = get_request_by_tshark(pcap_file)
    response_fingerprint_list = get_response_by_tshark(pcap_file)
    show_data(link_requestList_dict, link_responseList_dict, request_list, response_list, request_fingerprint_list, response_fingerprint_list)
    seq_finder = get_seq_finder(request_fingerprint_list, response_fingerprint_list)
    httpaction_list = linearize_all_httpactions(link_requestList_dict, link_responseList_dict, seq_finder)
    httpactions_to_file(httpaction_list, 'actions.json')

def pcap_to_actions(pcapfile, outputfile):
    output_dir = 'tcpflow_tmp'
    clear_tmp(output_dir)
    parse_by_tcpflow(pcapfile, output_dir)
    http_list = get_httpfile_list(output_dir)
    link_requestList_dict, link_responseList_dict = parse_http_file_list(http_list)
    request_list, response_list = get_request_and_response_list(link_requestList_dict, link_responseList_dict)
    request_fingerprint_list = get_request_by_tshark(pcapfile)
    response_fingerprint_list = get_response_by_tshark(pcapfile)
    show_data(link_requestList_dict, link_responseList_dict, request_list, response_list, request_fingerprint_list, response_fingerprint_list)
    seq_finder = get_seq_finder(request_fingerprint_list, response_fingerprint_list)
    httpaction_list = linearize_all_httpactions(link_requestList_dict, link_responseList_dict, seq_finder)
    httpactions_to_file(httpaction_list, outputfile)

if __name__ == '__main__':
    test()
