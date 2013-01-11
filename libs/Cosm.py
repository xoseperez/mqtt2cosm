#! /usr/bin/python
# -*- coding: utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

#   Copyright (C) 2013 by Xose Pérez
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Xose Pérez"
__contact__ = "xose.perez@gmail.com"
__copyright__ = "Copyright (C) 2013 Xose Pérez"
__license__ = 'GPL v3'

import urllib2
import json
import datetime

class Cosm(object):

    api_key = ''
    timeout = 10

    datapoints = []
    base_url = "http://api.cosm.com/v2/feeds/%s/datastreams/%s"

    def __init__(self, api_key):
        """
        Constructor, provide API Key
        """
        self.api_key = api_key

    def _send(self, method, url, data = None):
        """
        Private method that performs the HTTP request
        """

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
        """
        Reset the stored datapoints
        """
        self.datapoints = []

    def add(self, at, value):
        """
        Add a datapoint with a given timestamp and value
        """
        self.datapoints.append({'at': at, 'value': value})

    def send(self, feed, datastream):
        """
        Send all stored datapoints.
        Usage example:
            cosm = Cosm('APIKEY')
            cosm.add('2012-12-27T12:00:00+01:00', 190)
            cosm.add('2012-12-27T13:00:00+01:00', 150)
            cosm.add('2012-12-27T14:00:00+01:00', 270)
            cosm.send(94234, 1)
        """
        url = self.base_url % (feed, datastream) + "/datapoints.json"
        data = json.dumps({'datapoints' : self.datapoints})
        response = self._send('POST', url, data)
        return response

    def get(self, feed, datastream, start, end, step=360):
        """
        Gets all datapoints (interval 0) from a feed between two dates
        """

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
        """
        Pushes a single value with current timestamp to the given feed/datastream
        """
        url = self.base_url % (feed, datastream) + ".json"
        data = json.dumps({'current_value' : value})
        return self._send('PUT', url, data)
