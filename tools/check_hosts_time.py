# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: check_hosts_time.py
#         Desc:
#       Author: Lorry
#        Email: cclorry@gmail.com
#     HomePage:
#      Version: 0.0.1
#   LastChange: 2017-07-02 11:41:24
#      History:
#=============================================================================

'''

import os, time, threading, argparse
from http.client import HTTPConnection

__version__ = '0.0.1'


def create_parser(filename):
    target = './{0}_hosts.txt'.format(filename[0])

    parser = argparse.ArgumentParser(
        description='Get the hosts time.', prefix_chars='-/')

    parser.add_argument(
        '-H',
        '/H',
        '--hosts',
        dest='hosts',
        default=target,
        type=str,
        help='The hosts.',
        metavar='hosts.txt')
    parser.add_argument(
        '-z',
        '/z',
        '--timezone',
        dest='timezone',
        default=0,
        type=int,
        help='Timezone.',
        metavar='0')
    parser.add_argument(
        '-t',
        '/t',
        '--timeout',
        dest='timeout',
        default=3,
        type=int,
        help='Timeout.',
        metavar='3')

    return parser.parse_args()


def get_hosts(hosts_file):
    hosts = []
    f = open(hosts_file, 'r', encoding='UTF-8')
    ignore = [';', '#']

    while True:
        line = f.readline().strip()
        if not line:
            break
        if line[0] not in ignore:
            hosts.append(line)

    return hosts


def get_filename_and_ext(filename):
    (filepath, temp_filename) = os.path.split(filename)
    (shotname, extension) = os.path.splitext(temp_filename)
    return shotname, extension


def get_host_time(host, timezone=8, timeout=3):
    try:
        conn = HTTPConnection(host, timeout=timeout)
        conn.request('GET', '/')
        res = conn.getresponse().getheader('date')
        gmt = time.strptime(res[5:25], "%d %b %Y %H:%M:%S")
        ttime = time.localtime(time.mktime(gmt) + (timezone * 60 * 60))
        result = '[{1}-{2}-{3}T{4}:{5}:{6}] {0}'.format(
            host, ttime.tm_year,
            format(ttime.tm_mon, '02d'),
            format(ttime.tm_mday, '02d'),
            format(ttime.tm_hour, '02d'),
            format(ttime.tm_min, '02d'), format(ttime.tm_sec, '02d'))
    except:
        result = '[****-**-**T**:**:**] {0}'.format(host)
    print(result)


def main():
    threads = []

    hosts = get_hosts(args.hosts)

    for host in hosts:
        t = threading.Thread(
            target=get_host_time, args=(host, args.timezone, args.timeout))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


if __name__ == '__main__':
    filename = get_filename_and_ext(__file__)
    args = create_parser(filename)

    if os.path.exists(args.hosts):
        concurrent = 30
        semaphore = threading.BoundedSemaphore(concurrent)
        main()
    else:
        get_host_time(args.hosts, args.timezone, args.timeout)

# demo: __file__ --timezone=8 --timeout=3 --hosts="./hosts.txt"

# vim: noai:ts=4:sw=4
