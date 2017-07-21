# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: nodes_monitor2.py
#         Desc:
#       Author: Lorry
#        Email: cclorry@gmail.com
#     HomePage:
#      Version: 0.0.2
#   LastChange: 2017-07-22 02:03:03
#      History:
#=============================================================================

'''

import os
import random
import re
import time
import requests
import threading
import argparse
from urllib.parse import urlparse

__version__ = '0.0.2'
__all__ = [
    'create_user_agent', 'get_headers', 'output_log', 'get_node_list',
    'check_node'
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


def create_user_agent(kind='rand'):
    mark = [
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.2)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)',
        'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:47.0) Gecko/20100101 Firefox/47.0',
    ]

    user_agent = {
        'tester': 'tester',
        'rand': random.sample(mark, 1),
    }.get(kind, kind)

    return user_agent


def get_headers(url, ip, timeout=5, retry=3, client='rand'):
    """获取目标响应头

    参数:
        url: 目标地址，包含 http(s)://
        ip: host ip
        client: 客户端标识，随机或自定义
    """

    u = urlparse(url)
    t = '{scheme}://{ip}{path}'.format(scheme=u.scheme, path=u.path, ip=ip)
    user_agent = create_user_agent(client)[0]

    requests.adapters.DEFAULT_RETRIES = retry
    try:
        r = requests.head(
            t,
            headers={'host': u.netloc,
                     'User-Agent': user_agent},
            timeout=timeout,
            verify=False)
        return r.status_code, r.headers, (r.elapsed.microseconds / 1000000)
    except:
        return 0, "{status: 'error'}", 0


def output_log(log, content):
    with open(log, 'a') as f:
        f.write(content)
    f.close


def get_nodes_list(nodes_file: str, ld: str='(', rd: str=')') -> dict:
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


def check_node(url, node, timeout, log_dir, domain, retry=3):
    """检测单节点信息并输出日志"""

    now = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time()))
    today = time.strftime('%Y%m%d', time.localtime(time.time()))

    code, headers, elapsed = get_headers(url, node, timeout, retry)

    log = '{time} {node} {url} {code} {elapsed} [{output}]\n'.format(
        time=now,
        node=node,
        url=url,
        code=code,
        elapsed=elapsed,
        output=headers)
    output_log('{log_dir}{domain}.{date}.log'.format(
        log_dir=log_dir, domain=domain, date=today), log)

    if code != 200:
        output_log('{log_dir}{domain}.{date}.{code}.log'.format(
            log_dir=log_dir, domain=domain, date=today, code=code), log)


def main():
    args = create_parser()
    nodes = get_nodes_list(args.nodes)
    uri = urlparse(args.url)

    concurrent = 30
    semaphore = threading.BoundedSemaphore(concurrent)
    threads = []

    if not os.path.exists(args.log):
        os.mkdir(r'{}'.format(args.log))

    for node in nodes:
        t = threading.Thread(
            target=check_node,
            args=(args.url, node, args.timeout, args.log, uri.netloc,
                  args.retry))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


if __name__ == '__main__':
    main()

# demo: __file__ --nodes="./config/demo.nodes.txt" --url="http://api.demo.com/status" --log="./logs/" --timeout=5 --retry=3

# vim: noai:ts=4:sw=4
