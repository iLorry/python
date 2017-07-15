# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: nodes_monitor.py
#         Desc:
#       Author: Lorry
#        Email: cclorry@gmail.com
#     HomePage:
#      Version: 0.0.1
#   LastChange: 2017-07-16 01:38:23
#      History:
#=============================================================================

'''

import re, os, time, argparse
from urllib.parse import urlparse


def create_parser():
    parser = argparse.ArgumentParser(
        description='Monitor the server node.', prefix_chars='-/')

    parser.add_argument(
        '-n',
        '/n',
        '--nodes',
        dest='nodes',
        default='./config/default.nodes.txt',
        type=str,
        help='The nodes.',
        metavar='./config/domain.txt')
    parser.add_argument(
        '-u',
        '/u',
        '--url',
        dest='url',
        default=None,
        type=str,
        help='The url.',
        metavar='http://api.demo.com/status')
    parser.add_argument(
        '-l',
        '/l',
        '--log',
        dest='log',
        default='./logs/',
        type=str,
        help='The log path.',
        metavar='./logs/')
    parser.add_argument(
        '-r',
        '/r',
        '--retry',
        dest='retry',
        default=3,
        type=int,
        help='Timeout retry times.',
        metavar='3')
    parser.add_argument(
        '-t',
        '/t',
        '--timeout',
        dest='timeout',
        default=5,
        type=int,
        help='Timeout.',
        metavar='5')

    return parser.parse_args()


def run_command(cmd, retry=3):
    error = '{status:cmd_error}'
    try:
        output = (os.popen(cmd).read()).strip().replace('\n', '|')
    except:
        output = error
    if (output == '') and (retry > 1):
        retry -= 1
        run_command(cmd, retry)
    else:
        return output


def output_log(log, content):
    with open(log, 'a') as f:
        f.write(content)
    f.close


def scheme_to_port(scheme):
    return {
        'http': 80,
        'https': 443,
    }.get(scheme, 80)


def format_ip_list(config):
    f = open(config, 'r', encoding='UTF-8')
    ignore = [';', '#']
    nodes = {}

    while True:
        line = f.readline()
        if (not line) or (line[0] in ignore):
            break
        ip = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", line)
        if ip:
            ip = ip[0]

            if (ip not in nodes):
                nodes[ip] = re.findall(r"\((.*)\)", line)[0]

    return nodes


def wrong_status(string):
    codes = [
        '[None]',
        '401 Unauthorized',
        '404 Not Found',
        '503 Backend',
        '503 Service Unavailable',
        '504 Gateway Time-out',
    ]
    for code in codes:
        if (string.find(code) > -1):
            return True
    return False


def main():
    args = create_parser()

    nodes = format_ip_list(args.nodes)
    uri = urlparse(args.url)
    port = scheme_to_port(uri.scheme)

    if not os.path.exists(args.log):
        os.mkdir(r'{}'.format(args.log))

    for node in nodes:
        now = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time()))
        today = time.strftime('%Y%m%d', time.localtime(time.time()))

        cmd = 'curl --head --max-time {} --resolve {}:{}:{} "{}"'.format(
            args.timeout, uri.netloc, port, node, args.url)
        output = run_command(cmd, args.retry)

        log = '{} [{}] [{}]\n'.format(now, cmd, output)
        output_log('{}{}.{}.log'.format(args.log, uri.netloc, today), log)
        if (output == None) or (output == '') or (wrong_status(output)):
            output_log('{}{}.error.{}.log'.format(args.log, uri.netloc, today),
                       log)


if __name__ == '__main__':
    main()

# demo: __file__ --nodes="./config/demo.nodes.txt" --url="http://api.demo.com/status" --log="./logs/" --timeout=5 --retry=3

# vim: noai:ts=4:sw=4
