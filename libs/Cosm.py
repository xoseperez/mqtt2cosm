#! /usr/bin/python
# -*- utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import urllib2
import json
import datetime

class Cosm(object):

    api_key = ''
    timeout = 10

    datapoints = []
    base_url = "http://api.cosm.com/v2/feeds/%s/datastreams/%s"

    def __init__(self, api_key):
        self.api_key = api_key

    def _send(self, method, url, data = None):

        output = True

        try:
            request = urllib2.Request(url)
            request.get_method = lambda: method
            request.add_header("X-ApiKey", self.api_key)
            response = urllib2.urlopen(request, data, self.timeout)
            output = response.read()
            response.close()
        except:
            output = False

        return output

    def clear(self):
        self.datapoints = []

    def add(self, at, value):
        self.datapoints.append({'at': at, 'value': value})

    def send(self, feed, datastream):
        url = self.base_url % (feed, datastream) + "/datapoints.json"
        data = json.dumps({'datapoints' : self.datapoints})
        response = self._send('POST', url, data)
        return response

    def get(self, feed, datastream, start, end, step=360):

        ts_start = start
        step = datetime.timedelta(minutes=step)
        url = self.base_url % (feed, datastream)
        counter = 1

        while ts_start < end:
            ts_end = min(ts_start + step, end)
            data = "limit=1000&interval=0&start=%s&end=%s" % (ts_start.isoformat(), ts_end.isoformat())
            response = self._send('GET', url + "?c=" + str(counter), data)
            response = json.loads(response)
            if 'datapoints' in response:
                for datapoint in  response['datapoints']:
                    yield [datapoint['at'], datapoint['value']]
            ts_start = ts_end
            counter = counter + 1


    def push(self, feed, datastream, value):
        url = self.base_url % (feed, datastream) + ".json"
        data = json.dumps({'current_value' : value})
        return self._send('PUT', url, data)
