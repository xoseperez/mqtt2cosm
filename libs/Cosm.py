#! /usr/bin/python
# -*- utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import urllib2
import json

class Cosm(object):

    api_key = ''
    timeout = 10

    datapoints = []
    cosm_datapoint = "http://api.cosm.com/v2/feeds/%s/datastreams/%s/datapoints.json"
    cosm_datastream = "http://api.cosm.com/v2/feeds/%s/datastreams/%s.json"

    def __init__(self, api_key):
        self.api_key = api_key

    def _send(self, method, url, data):

        data = json.dumps(data)
        response = True

        try:
            request = urllib2.Request(url)
            request.get_method = lambda: method
            request.add_header("X-ApiKey", self.api_key)
            urllib2.urlopen(request, data, self.timeout)
        except:
            response = False

        return response

    def clear(self):
        self.datapoints = []

    def add(self, at, value):
        self.datapoints.append({'at': at, 'value': value})

    def send(self, feed, datastream):
        url = self.cosm_datapoint % (feed, datastream)
        data = {'datapoints' : self.datapoints}
        response = self._send('POST', url, data)
        return response

    def push(self, feed, datastream, value):
        url = self.cosm_datastream % (feed, datastream)
        data = {'current_value' : value}
        return self._send('PUT', url, data)

if __name__ == '__main__':
    cosm = Cosm('QFUdRPODMAkYLHx8LcuvPdECCTiSAKxwME9hb3luSVlvdz0g')
    cosm.add('2012-12-27T14:30:00+01:00', 1430)
    cosm.add('2012-12-27T15:30:00+01:00', 1530)
    print cosm.send(94914, 1)
    print cosm.push(94914, 1, 950)
