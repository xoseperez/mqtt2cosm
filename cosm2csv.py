#! /usr/bin/python
# -*- utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import re
import datetime

from libs.Cosm import Cosm
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Cosm.com to CSV')
    parser.add_argument("-k", dest="api_key",  help="cosm.com API key", required=True)
    parser.add_argument("-f", dest="feed",  help="coms.com feed", required=True, type=int)
    parser.add_argument("-d", dest="datastream",  help="datastream in the feed", required=True)
    parser.add_argument("-s", dest="start",  help="start datetime (YYYY-MM-DD [HH:MM:SS])", required=True)
    parser.add_argument("-e", dest="end",  help="end datetime (YYYY-MM-DD [HH:MM:SS])", required=True)
    parser.add_argument("--format", dest="format",  help="output timestamp format")
    options = parser.parse_args()

    cosm = Cosm(options.api_key)

    start = datetime.datetime(*[int(x) for x in re.findall(r'\d+', options.start)])
    end = datetime.datetime(*[int(x) for x in re.findall(r'\d+', options.end)])

    print "timestamp,value"
    for ts, value in cosm.get(options.feed, options.datastream, start, end):
        if options.format:
            ts = datetime.datetime(*[int(x) for x in re.findall(r'\d+', ts)])
            ts = ts.strftime(options.format)
        print "%s,%s"  % (ts, value)

