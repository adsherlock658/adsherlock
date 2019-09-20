import subprocess
import re

import sys


def parse_apk(apk):
    activity_regex = re.compile(r"name='(.*?)'\s+label")
    package_regex = re.compile(r"name='(.*?)'\s+versionCode")

    activity = ''
    package = ''
    badging = subprocess.check_output(['aapt', 'dump', 'badging', apk])
    for line in badging.splitlines():
        if line.startswith('launchable-activity'):
            if not activity:
                t = activity_regex.search(line)
                if t:
                    activity = t.group(1)

        if line.startswith('package'):
            if not package:
                t = package_regex.search(line)
                if t:
                    package = t.group(1)

    return package, activity

def get_sn_list():
    output = subprocess.check_output(['adb', 'devices'])
    device_pattern = re.compile(r'[\w\d]+\t+device')
    matches = device_pattern.findall(output)
    return [x.split('\t')[0] for x in matches]

def prompt_confirm(prompt):
    print('\t%s' % prompt)
    while True:
        input = raw_input('Press ENTER/y to accept or n to reject: ',)
        if input == '' or input == 'y':
            return True
        elif input == 'n':
            return False

def has_install(sn, package):
    package_list = subprocess.check_output(['adb', '-s', sn, 'shell', 'pm', 'list', 'packages'])
    if package not in package_list:
        return False
    else:
        return True

def log(message):
    print('[STAGE] %s' % message)

def install(sn, apk):
    try:
        subprocess.check_output(['adb', '-s', sn, 'install', apk])
    except Exception:
        log('Fail to install apk %s' % apk)
        sys.exit(1)

def uninstall(sn, package):
    try:
        subprocess.check_output(['adb', '-s', sn, 'uninstall', package])
    except Exception:
        log('Fail to uninstall apk %s' % package)
        sys.exit(1)

def start_app(sn, package, activity):
    subprocess.check_output(['adb', '-s', sn, 'shell', 'am', 'start', '-n', '%s/%s' % (package, activity)])

def get_touchscreen_device(sn):
    data = {
        '03a7632a093f4a5d': '/dev/input/event1',
    }
    if sn not in data:
        return
    return data[sn]

def test1():
    apk = '/home/luoy/infocom16/com.yoka.hotman-4.0.9-55.apk'
    package, activity = parse_apk(apk)
    print(package, activity)

def test2():
    prompt_confirm('aaaaaaaaaaaaaaaaaaa')

def test3():
    print get_sn_list()

def test4():
    sn = get_sn_list()[0]
    apk = '/home/luoy/infocom16/com.yoka.hotman-4.0.9-55.apk'
    package, activity = parse_apk(apk)
    print(has_install(sn, package))

if __name__ == '__main__':
    test4()
