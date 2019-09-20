from subprocess import check_output, Popen, PIPE
import os

from infocom.pattern_to_json import parse_file
from infocom.pcap_to_json_by_tcpflow import pcap_to_actions
from infocom.util import has_install, install, get_sn_list, uninstall, start_app


def get_dirname():
    return os.path.basename(os.getcwd())

def get_filenames(package_name):
    pcap_filename = package_name + '.pcap'
    pattern_filename = package_name + '_pattern.txt'

    return pcap_filename, pattern_filename

def install_apk(sn):
    cla_apk = os.path.join(os.path.dirname(__file__), 'lib', 'tree.apk')
    print(cla_apk)
    package_name = 'org.emnets.adviser.httpclassifier'
    if not has_install(sn, package_name):
        install(sn, cla_apk)
    else:
        uninstall(sn, package_name)
        install(sn, cla_apk)

def wait_until_done(sn):
    cmd_init = ['adb', '-s', sn, 'logcat', '-c']
    check_output(cmd_init)
    cmd = ['adb', '-s', sn, 'logcat', '-s', 'ADVISER-Act']
    p = Popen(cmd, stdout=PIPE)
    for line in iter(p.stdout.readline, ''):
        print(line.strip())
        if line.find('execute done') != -1:
            break
    p.kill()

def delete_files(sn):
    cmd1 = ['adb', '-s', sn, 'shell', 'rm', '/sdcard/actions.json']
    cmd2 = ['adb', '-s', sn, 'shell', 'rm', '/sdcard/pattern.json']
    cmd3 = ['adb', '-s', sn, 'shell', 'rm', '/sdcard/score.json']
    cmd4 = ['adb', '-s', sn, 'shell', 'rm', '/sdcard/result.json']
    check_output(cmd1)
    check_output(cmd2)
    check_output(cmd3)
    check_output(cmd4)

def retrive_result(sn):
    check_output(['adb', '-s', sn, 'pull', '/sdcard/result.json', '.'])

def generate_jsonfiles(pcap_file, pattern_file):
    ifname = pcap_file
    ofname = 'actions.json'
    pcap_to_actions(ifname, ofname)
    parse_file(pattern_file)

def push_files(sn):
    cmd1 = ['adb', '-s', sn, 'push', 'actions.json', '/sdcard/actions.json']
    cmd2 = ['adb', '-s', sn, 'push', 'pattern.json', '/sdcard/pattern.json']
    cmd3 = ['adb', '-s', sn, 'push', 'score.json', '/sdcard/score.json']
    check_output(cmd1)
    check_output(cmd2)
    check_output(cmd3)

def start(sn):
    start_app(sn=sn, package='org.emnets.adviser.httpclassifier', activity='org.emnets.adviser.httpclassifier.MainActivity')

def main():
    sn = get_sn_list()[0]

    dirname = get_dirname()

    pcap_file, pattern_file = get_filenames(dirname)

    generate_jsonfiles(pcap_file, pattern_file)

    delete_files(sn)

    push_files(sn)

    install_apk(sn)

    start(sn)

    wait_until_done(sn)

    retrive_result(sn)

if __name__ == '__main__':
    main()
