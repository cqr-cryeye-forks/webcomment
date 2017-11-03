#!/usr/bin/env python3

import argparse
from argparse import RawTextHelpFormatter

import urllib.request
import urllib.parse
import re
import sys

parser = argparse.ArgumentParser(

    epilog='./webcomment.py -m url -t http://www.blog.btbw.pl \n'
           './webcomment.py -m url -t http://www.blog.btbw.pl -f example/btbw_filter.txt \n'
           './webcomment.py -m url -t http://www.blog.btbw.pl -f example/btbw_filter.txt -o /tmp/output.txt \n'
           './webcomment.py -m urls -t example/btbw_20.txt -f example/btbw_filter.txt -o /tmp/output.txt \n'
           ' ',

    formatter_class=RawTextHelpFormatter
)

garbage = []


def get_content(_url):
    req = urllib.request.Request(_url, method='GET')

    try:
        response = urllib.request.urlopen(req)
        return response.read().decode('utf8')
    except urllib.error.URLError:
        print("Error: " + _url)
        return ""


def get_html_comments(_html):
    p = re.compile('<!--(.+?)-->')
    return p.findall(_html)


def is_valid(_content):
    return (_content.strip() in garbage) == False


def main():
    parser.add_argument("-m", "--mode", help="Mode (url or urls)")
    parser.add_argument("-t", "--target", help="Target url or file (where each url is in new line)")
    parser.add_argument("-f", "--filter", help="File with filters (where you can list comments that should be omitted)")
    parser.add_argument("-o", "--output", help="Output file", default="/tmp/output.txt")
    parser.add_argument_group("xxx")

    args = parser.parse_args()

    print("Mode {}".format(args.mode))
    print("Target {}".format(args.target))
    print("Filter {}".format(args.filter))
    print("Output {}".format(args.output))

    action_type = args.mode
    targets = args.target
    filters = args.filter
    output = args.output

    log = open(output, 'w')

    if action_type == "urls":
        if filters is not None:
            collect_garbage(filters)
        process_targets(targets, log)

    if action_type == "url":
        if filters is not None:
            collect_garbage(filters)
        process_target(targets, log)


def collect_garbage(filters):
    try:
        with open(filters) as filterFile:
            for one_filter in filterFile:
                garbage.append(one_filter.strip())
    except Exception:
        print('Incorrect filter path: ' + filters)
        print('-----------------------------------')


def process_targets(targets, log):
    try:
        with open(targets) as urlFile:
            for urlLine in urlFile:
                process_target(urlLine.strip(), log)
    except Exception:
        print('Incorrect target path: ' + targets)
        print('-----------------------------------')


def process_target(url, log):
    try:
        log.write("---------- " + url + " ----------\n")
        content = get_content(url)
        comments = get_html_comments(content.strip().replace('\n', ''))
        for idx, comment in enumerate(comments):
            if is_valid(comment):
                log.write(comment.strip() + "\n")
        log.write("\n\n")
        print("- " + url)
    except Exception as error:
        print(error)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
