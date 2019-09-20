import json
import sys

class HttpRequest(object):
    def __init__(self, method, domain, path_list, key_list):
        self.method = method
        self.domain = domain
        self.path_list = path_list
        self.key_list = key_list

class TokenScore(object):
    def __init__(self, token, advalue, nonadvalue):
        self.token = token
        self.adscore = advalue
        self.nonadscore = nonadvalue

def parse_pattern_lines(lines):
    pattern_lines = []
    for line in lines:
        tokens = [x.strip() for x in line.split(",") if x]
        pattern_lines.append(tokens)
    return pattern_lines

def parse_socre_lines(lines):
    score_list = []
    for line in lines:
        tokens = [x for x in line.split() if x]
        if len(tokens) != 3:
            continue
        token, advalue, nonadvalue = tokens
        tokenscore = TokenScore(token, advalue, nonadvalue)
        score_list.append(tokenscore)

    return score_list

def parse_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    nonad_index = -1
    ad_index = -1
    score_index = -1

    for index, line in enumerate(lines):
        if line.find('==nonads==') != -1:
            nonad_index = index
        elif line.find('==ads==') != -1:
            ad_index = index
        elif line.find('==tokenScoreDict==') != -1:
            score_index = index

    nonad_lines = lines[nonad_index+1: ad_index]
    ad_lines = lines[ad_index+1: score_index]
    score_lines = lines[score_index+2:] # because of a stupid prompt line

    nonad_pattern = parse_pattern_lines(nonad_lines)
    ad_pattern = parse_pattern_lines(ad_lines)
    score_list = parse_socre_lines(score_lines)

    pattern = {"adtoken": ad_pattern, "nonadtoken": nonad_pattern}

    score_dict_to_file('score.json', score_list)
    pattern_to_file('pattern.json', pattern)

def score_dict_to_file(filename, score_list):
    with open(filename, 'w') as fout:
        score_dict_list = []
        for score in score_list:
            score_dict_list.append(score.__dict__)
        json.dump(fp=fout, obj=score_dict_list)

def pattern_to_file(filename, pattern):
    with open(filename, 'w') as fout:
        json.dump(fp=fout, obj=pattern)

def test_parse_file():
    filename = '/home/luoy/infocom16/com.shoujiduoduo.ringtone_pattern.txt'
    parse_file(filename)

if __name__ == '__main__':
    test_parse_file()
