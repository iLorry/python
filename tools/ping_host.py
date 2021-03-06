# -*- coding:utf-8 -*-
'''
#=============================================================================
#     FileName: ping_host.py
#         Desc:
#       Author: Lorry
#        Email: cclorry@gmail.com
#     HomePage:
#      Version: 0.0.1
#   LastChange: 2017-07-16 16:40:50
#      History:
#=============================================================================

'''

import os
import sys
import time
import re
import requests
import socket
import platform
import argparse

__version__ = '0.0.1'
__all__ = ['main', 'get_host_ip', 'get_outer_ip']


def create_parser():
    '''
    接收参数
    '''

    parser = argparse.ArgumentParser(
        description='Ping the host.', prefix_chars='-/')

    parser.add_argument(
        '-H',
        '/H',
        '--host',
        dest='host',
        default='192.168.1.1',
        type=str,
        help='The HOST.',
        metavar='192.168.1.1')
    parser.add_argument(
        '-w',
        '/w',
        '--wait',
        dest='wait',
        default=3,
        type=int,
        help='The intervals.',
        metavar='3')
    parser.add_argument(
        '-l',
        '/l',
        '--logs-path',
        dest='logs_path',
        default='./logs/',
        type=str,
        help='The logs path.',
        metavar='./logs/')
    parser.add_argument(
        '-v',
        '/v',
        '--verbose',
        dest='verbose',
        default=0,
        action='count',
        help='Verbose mode.')
    parser.add_argument(
        '-V',
        '/V',
        '--version',
        action='version',
        version='%(prog)s ' + __version__,
        help='Show the version number and exit.')

    return parser.parse_args()


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()

    return ip


def get_outer_ip():
    url = r'http://checkip.dyndns.org'
    timeout = 3

    try:
        res = requests.get(url, timeout=timeout)
        status = res.status_code
        if status == 200:
            return re.search('\d+\.\d+\.\d+\.\d+', res.text).group(0)
    except:
        return False


def main():

    args = create_parser()
    system = platform.system().lower()

    logs_path = args.logs_path
    if logs_path[-1] != '/':
        logs_path += '/'

    if os.path.exists(logs_path) == False:
        os.makedirs(logs_path)

    pause_show_host = 10

    while True:

        # os.popen("ipconfig /flushdns")
        try:
            if system == 'linux':
                c = 'c'
            else:
                c = 'n'
            output = os.popen('ping -{0} 1 {1}'.format(c, args.host)).read()
            ip = re.search(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])',
                           output).group()
            response_time = re.search(r'=(\d+)\s*ms', output).group(1)
        except:
            ip = response_time = '---'

        now = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time()))
        info = '{0} {1} {2}ms'.format(now, ip, response_time)

        if args.verbose > 0:
            print(info)

            if args.verbose > 1:
                if pause_show_host == 1:
                    ip = get_outer_ip() if get_outer_ip() else get_host_ip()
                    print('{0} > {1}'.format(ip, args.host))
                    pause_show_host = 10
                else:
                    pause_show_host -= 1

        with open(logs_path + args.host + '.log', 'a') as f:
            f.write(info + '\n')

        time.sleep(int(args.wait))


if __name__ == '__main__':
    main()

# demo: __file__ --logs-path="./logs" --host=www.qq.com --wait=3 -v

# vim: noai:ts=4:sw=4
