import multiprocessing
import os

from subprocess import check_output, Popen, PIPE

import thread

import subprocess

import sys

from util import get_sn_list, log, parse_apk, has_install, install, uninstall, prompt_confirm, get_touchscreen_device, \
    start_app


def find_target_device(sn):
    sn_list = get_sn_list()
    if not sn:
        if len(sn_list) > 1:
            print('Multiple device found, please specify the device with -s')
            return
        if len(sn_list) == 0:
            print('No device found')
            return
        return sn_list[0]
    else:
        if sn not in sn_list:
            print('The specify device not plugged in')
            return
        return sn

def install_pc(sn):
    pc_apk = os.path.join(os.path.dirname(__file__), 'lib', 'packetcapture.apk')
    pc_package, pc_activity = parse_apk(pc_apk)
    if not has_install(sn, pc_package):
        install(sn, pc_apk)

    return pc_package, pc_activity

def install_app(sn, apk):
    package, activity = parse_apk(apk)
    if not has_install(sn, package):
        install(sn, apk)
    else:
        uninstall(sn, package)
        install(sn, apk)

    return package, activity

def delete_capture_files(sn, pc_package):
    path = '/sdcard/Android/data/%s/files/*' % pc_package
    check_output(['adb', '-s', sn, 'shell', 'rm', path])

def retrive_capture_file(sn, pc_package, name):
    name = '%s_capture.pcap' % name
    path = '/sdcard/Android/data/%s/files/' % pc_package
    file_name = check_output(['adb', '-s', sn, 'shell', 'ls', path]).strip()
    path = path + file_name
    check_output(['adb', '-s', sn, 'pull', path, name])

def store_uevent(sn, package):
    file_name = package + '_evdev.txt'
    event_dev = get_touchscreen_device(sn)
    with open(file_name, 'w') as fout:
        p = Popen(['adb', '-s', sn, 'shell', 'getevent', '-lt', event_dev], stdout=PIPE)
        for line in iter(p.stdout.readline, ''):
            fout.write(line.strip() + '\n')

def tcpdump(package):
    subprocess.check_output(['sudo', 'tcpdump', '-i', 'ppp0', '-w', package + '.pcap'])

def main(apk, sn=''):
    """
    Step 1: parse the apk file and get the package name
    Step 2: install
    :return:
    """
    if not os.path.isfile(apk):
        print('No such apk file')
        return

    # check for plugged devices
    target_sn = find_target_device(sn)
    if not target_sn:
        return
    log('Target device: %s' % target_sn)

    # check target apk and install it
    app_package, app_activity = install_app(target_sn, apk)
    log('Target apk has been installed')

    # prompt and get ready for record
    if not prompt_confirm('Ready for record?'):
        return

    # start app
    start_app(target_sn, app_package, app_activity)
    log('Start app')

    # start uevent logger
    thread.start_new_thread(store_uevent, (target_sn, app_package))
    log('Start uevent logger')

    # start tcpdump
    thread.start_new_thread(tcpdump, (app_package,))

    # now we start repaly recorder
    try:
        subprocess.call(['python', '-m', 'preplay.examples.DroidRecorder', app_package + '_record.txt'])
    except KeyboardInterrupt:
        uninstall(target_sn, app_package)

def test1():
    sn = get_sn_list()[0]
    pc_package = 'jp.co.taosoftware.android.packetcapturepro'
    delete_capture_files(sn, pc_package)

def test2():
    sn = get_sn_list()[0]
    pc_package = 'jp.co.taosoftware.android.packetcapturepro'
    name = 'hello'
    retrive_capture_file(sn, pc_package, name)

def test3():
    sn = get_sn_list()[0]
    package = 'asdf'
    thread.start_new_thread(store_uevent, (sn, package))
    while True:
        pass

def test4():
    apk = '/home/luoy/infocom16/com.yoka.hotman-4.0.9-55.apk'
    main(apk)

def test5():
    apk = '/home/luoy/infocom16/exps/net.zedge.android/net.zedge.android.apk'
    package, activity = parse_apk(apk)
    tcpdump(package)

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 1:
        main(apk=args[0])
    if len(args) == 3:
        main(apk=args[2], sn=args[1])
