#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
#=============================================================================
#     FileName: port_scan.py
#         Desc:
#       Author: Lorry
#        Email: cclorry@gmail.com
#     HomePage:
#      Version: 0.0.1
#   LastChange: 2017-05-17 15:30:59
#      History:
#=============================================================================

'''

from socket import *
import threading
import argparse

__version__ = '0.0.1'
__all__ = ['port_scanner', 'main']

lock = threading.Lock()
threads = []

def port_scanner(host: str, port: int, verbose: int =0) -> print:
    '''
    扫描端口并直接在屏幕打印状态
    '''

    try:
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((host, port))
        lock.acquire()
        if verbose < 1:
            print('%s:%d' % (host, port))
        else:
            print('[OPEN] %s:%d' % (host, port))
        lock.release()
        s.close()
    except:
        if verbose < 1:
            pass
        else:
            print('[CLOSE] %s:%d' % (host, port))

def create_parser():
    '''
    接收参数
    '''

    parser = argparse.ArgumentParser(description='Scan the hosts\'s port.', prefix_chars='-/')

    parser.add_argument('-H', '/H', '--hosts', dest='hosts', default='192.168.1.', type=str, help='The IP segment.', metavar='192.168.1.')
    parser.add_argument('-b', '/b', '--begin', dest='begin', default=1, type=int, help='The begin of the IP segment.', metavar='1')
    parser.add_argument('-e', '/e', '--end', dest='end', default=None, type=int, help='The end of the IP segment.', metavar='254')
    parser.add_argument('-p', '/p', '--ports', dest='ports', default='80,443', type=str, help='Target ports.', metavar='80,443')
    parser.add_argument('-t', '/t', '--timeout', dest='timeout', default=1, type=int, help='Timeout.', metavar='1')
    parser.add_argument('-v', '/v', '--verbose', dest='verbose', default=0, action='count', help='Verbose mode.')
    parser.add_argument('-V', '/V', '--version', action='version', version='%(prog)s ' + __version__, help='Show the version number and exit.')

    return parser.parse_args()

def main():
    '''
    并发请求
    '''

    args = create_parser()
    ports = args.ports.split(',')

    if (args.end == None) or (args.end < args.begin):
        args.end = args.begin

    setdefaulttimeout(args.timeout)

    while args.begin <= args.end:

        for port in ports:
            host = '{0}{1}'.format(args.hosts, args.begin)
            t = threading.Thread(target=port_scanner, args=(host, int(port), args.verbose))
            t.start()

        for t in threads:
            t.join()

        args.begin += 1

if __name__ == '__main__':
    main()

# demo: __name__ --hosts=192.168.1. --begin=1 --end=255 --ports=80,443 -v

# vim: noai:ts=4:sw=4
