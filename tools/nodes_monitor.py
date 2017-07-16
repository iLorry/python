# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: nodes_monitor.py
#         Desc:
#       Author: Lorry
#        Email: cclorry@gmail.com
#     HomePage:
#      Version: 0.0.1
#   LastChange: 2017-07-16 16:03:31
#      History:
#=============================================================================

'''

import re, os, time, argparse
from urllib.parse import urlparse

__version__ = '0.0.1'
__all__ = [
    'run_command', 'output_log', 'scheme_to_port', 'get_node_list',
    'wrong_status'
]


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
    """运行命令并返回合并成一行的运行结果

    参数:
        cmd: 命令
        retry: 重试次数，应对超时的情况
    """

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


def get_node_list(nodes_file: str, ld: str='(', rd: str=')') -> dict:
    """读取 node 列表文件并提取非重复的节点 IP

    参数:
        nodes_file: 节点文件
        ld: 左定界符
        rd: 右定界符

    节点文件格式:
        127.0.0.1(localhost)
        8.8.8.8(Google)
        ; 8.8.8.8(Google DNS)
        8.8.4.4
    """
    f = open(nodes_file, 'r', encoding='UTF-8')
    ignore = [';', '#']
    nodes = {}

    while True:
        line = f.readline()
        if (not line) or (line[0] in ignore):
            break
        ip = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", line)
        if ip and (ip[0] not in nodes):
            node_name = re.findall(r"\{}(.*)\{}".format(ld, rd), line)
            if node_name:
                nodes[ip[0]] = node_name[0]
            else:
                nodes[ip[0]] = ip[0]

    return nodes


def wrong_status(string):
    """错误状态特征"""

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

    nodes = get_node_list(args.nodes)
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
