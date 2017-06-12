# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: copy_files_to_share.py
#         Desc:
#       Author: Lorry
#        Email: cclorry@gmail.com
#     HomePage:
#      Version: 0.0.1
#   LastChange: 2017-06-12 23:55:11
#      History:
#=============================================================================

'''

import os, glob, time, shutil
import argparse

__version__ = '0.0.1'
__all__ = ['screen_files', 'backup_files', 'remove_files', 'main']


def create_parser():
    '''
    接收参数
    '''

    parser = argparse.ArgumentParser(
        description='Copy files to share.', prefix_chars='-/')

    parser.add_argument(
        '-s',
        '/s',
        '--source',
        dest='source',
        default='./source',
        type=str,
        help='The source.',
        metavar='./source')
    parser.add_argument(
        '-t',
        '/t',
        '--target',
        dest='target',
        default='./target',
        type=str,
        help='The target.',
        metavar='./target')
    parser.add_argument(
        '-d',
        '/d',
        '--diff',
        dest='diff',
        default=86400,
        type=int,
        help='The time diff.',
        metavar='86400')
    parser.add_argument(
        '-l',
        '/l',
        '--logs-file',
        dest='logs_file',
        default=None,
        type=str,
        help='The logs file.',
        metavar='./logs/file.log')
    parser.add_argument(
        '-r',
        '/r',
        '--remove',
        dest='remove',
        action='store_true',
        default=False,
        help='Delete expired files')
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


def screen_files(source, time_diff, mode=True):
    files = []
    ticks = round(time.time())
    for parent, paths, filenames in os.walk(source):
        for filename in filenames:
            full_path = os.path.join(parent, filename)
            meta = os.stat(full_path)
            if ((ticks - meta.st_mtime) < time_diff) == mode:
                files.append({
                    'name': full_path,
                    'size': meta.st_size,
                    'mtime': meta.st_mtime
                })
    return files


def backup_files(files, source, target, user, password, log, verbose=0):
    for f in files:
        target_file = f['name'].replace(source, target)
        target_path = os.path.dirname(target_file)
        if os.path.exists(target_path) == False:
            os.makedirs(target_path)

        output = os.popen('net use {0} /user:{1} "{2}"'.format(
            target, user, password)).read()

        shutil.copyfile(f['name'], target_file)

        now = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time()))
        info = '{0} [C] {1} {2}'.format(now, f['name'], target_file)

        if verbose > 0:
            print(info)

        if log:
            with open(log, 'a') as f:
                f.write(info + '\n')


def remove_files(files, log, verbose=0):
    for f in files:
        if os.path.exists(f['name']) == True:
            os.remove(f['name'])

            now = time.strftime('%Y-%m-%dT%H:%M:%S',
                                time.localtime(time.time()))
            info = '{0} [D] {1}'.format(now, f['name'])

            if verbose > 0:
                print(info)

            if log:
                with open(log, 'a') as f:
                    f.write(info + '\n')


def main():
    args = create_parser()
    target = '\\\\192.168.1.1\\share\\' + args.target
    user = 'user'
    password = 'password'
    files = screen_files(args.source, args.diff)
    backup_files(files, args.source, target, user, password, args.logs_file,
                 args.verbose)
    if args.remove == True:
        files = screen_files(target, args.diff, False)
        remove_files(files, args.logs_file, args.verbose)


if __name__ == '__main__':
    main()

# demo: __name__ --logs-file=./logs/file.log --source=./source --target=./target -r -v

# vim: noai:ts=4:sw=4
