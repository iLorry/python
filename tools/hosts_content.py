# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: hosts_content.py
#         Desc:
#       Author: Lorry
#        Email: cclorry@gmail.com
#     HomePage:
#      Version: 0.0.1
#   LastChange: 2017-07-01 03:44:44
#      History:
#=============================================================================

'''

import os, sys, requests, threading, argparse
import json

__version__ = '0.0.1'


def create_parser(filename):
    config = './{0}_config.json'.format(filename[0])
    target = './{0}_target.txt'.format(filename[0])

    parser = argparse.ArgumentParser(
        description='Get the host content.', prefix_chars='-/')

    parser.add_argument(
        '-c',
        '/c',
        '--config',
        dest='config',
        default=config,
        type=str,
        help='The config.',
        metavar='config.json')

    parser.add_argument(
        '-t',
        '/t',
        '--target',
        dest='target',
        default=target,
        type=str,
        help='The target.',
        metavar='target.txt')

    return parser.parse_args()


def check_host(host, url, user, password, timeout=1):
    semaphore.acquire()

    try:
        res = requests.get(url, timeout=timeout, auth=(user, password))
        status = res.status_code
        if (status == 200):
            text = res.text.strip()
        else:
            text = status
        print('[{0}] {1}'.format(text, host))
    except:
        print('[{0}] {1}'.format('err', host))

    semaphore.release()


def get_hosts(hosts_file):
    targets = []
    f = open(hosts_file, 'r', encoding='UTF-8')
    ignore = [';', '#']

    while True:
        line = f.readline().strip()
        if not line:
            break
        if line[0] not in ignore:
            targets.append(line)

    return targets


def get_filename_and_ext(filename):
    (filepath, temp_filename) = os.path.split(filename)
    (shotname, extension) = os.path.splitext(temp_filename)
    return shotname, extension


def main():
    hosts = []
    threads = []

    with open(args.config, 'r') as f:
        hosts_list = json.load(f)

    targets = get_hosts(args.target)

    for target in targets:
        if target in hosts_list:
            hosts.append(hosts_list[target])
            hosts[-1].insert(0, target)

    for host in hosts:
        t = threading.Thread(target=check_host, args=(host))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


if __name__ == '__main__':
    filename = get_filename_and_ext(__file__)
    args = create_parser(filename)

    if os.path.exists(args.config) and os.path.exists(args.target):
        concurrent = 30
        semaphore = threading.BoundedSemaphore(concurrent)
        main()
    else:
        print('Missing configuration file.')

# demo: __file__ --config="./config.json" --target="./target.txt"

# vim: noai:ts=4:sw=4
