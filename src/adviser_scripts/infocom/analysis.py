import json

def get_true_positive(requests):
    count = 0
    for request in requests:
        if request['is_ad'] and request['result']:
            count += 1
    return count

def get_true_negative(requests):
    count = 0
    for request in requests:
        if (not request['is_ad']) and (not request['result']):
            count += 1
    return count

def get_false_positive(requests):
    count = 0
    for request in requests:
        if (not request['is_ad']) and (request['result']):
            count += 1
    return count

def get_false_negative(requests):
    count = 0
    for request in requests:
        if (request['is_ad']) and (not request['result']):
            count += 1
    return count

def get_score_determine(requests):
    count = 0
    for request in requests:
        if (not request['determined']):
            count += 1
    return count

def get_score_true_positive(requests):
    count = 0
    for request in requests:
        if (not request['determined']) and request['is_ad'] and request['result']:
            count += 1
    return count

def get_score_true_negative(requests):
    count = 0
    for request in requests:
        if (not request['determined']) and (not request['is_ad']) and (not request['result']):
            count += 1
    return count

def get_score_false_positive(requests):
    count = 0
    for request in requests:
        if (not request['determined']) and (not request['is_ad']) and (request['result']):
            count += 1
    return count

def get_score_false_negative(requests):
    count = 0
    for request in requests:
        if (not request['determined']) and (request['is_ad']) and (not request['result']):
            count += 1
    return count

def get_process_time(requests):
    timeset = []
    for request in requests:
        timeset.append(request["parsed_time"])
    return timeset

def show_process_time():
    filename = 'result.json'
    outputname = 'processtime.json'
    with open(filename, 'r') as fin:
        result = json.load(fp=fin)
    requests = result['action_list']
    count = result['count']
    ptime = {}
    ptime['ptime'] = get_process_time(requests)
    ptime['count'] = count
    with open(outputname, "w") as json_file:
        json.dump(ptime, json_file)

def show_basic_result():
    filename = 'result.json'
    outputname = 'output.json'
    with open(filename, 'r') as fin:
        result = json.load(fp=fin)
    requests = result['requests']

    output = {}
    output['tp'] = get_true_positive(requests)
    output['tn'] = get_true_negative(requests)
    output['fp'] = get_false_positive(requests)
    output['fn'] = get_false_negative(requests)

    output['stp'] = get_score_true_positive(requests)
    output['stn'] = get_score_true_negative(requests)
    output['sfp'] = get_score_false_positive(requests)
    output['sfn'] = get_score_false_negative(requests)

    with open(outputname, "w") as json_file:
        json.dump(output, json_file, sort_keys=True, indent=2)

    print("Totoal Result Count: %d" % result['requestcount'])
    print("Totoal used time %s ms" % ((result['parseend'] - result['parsestart']) / 1000000.0))

    print("True positive: %d, True negative: %d" % (get_true_positive(requests), get_true_negative(requests)))
    print("False positive: %d, False negative: %d" % (get_false_positive(requests), get_false_negative(requests)))

    print("Score determined: %d" % (get_score_determine(requests)))
    print("Score True positive: %d, Score True negative: %d" % (get_score_true_positive(requests), get_score_true_negative(requests)))
    print("Score False positive: %d, Score False negative: %d" % (get_score_false_positive(requests), get_score_false_negative(requests)))


if __name__ == '__main__':
    # show_basic_result()
    show_process_time()
