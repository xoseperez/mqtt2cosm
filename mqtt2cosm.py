#! /usr/bin/python
# -*- utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

__app__ = "MQTT to COSM gateway"
__version__ = '0.1'
__author__ = "Xose Perez"
__copyright__ = "Copyright (C) Xose Perez"
__license__ = 'TBD'

import sys
import time
from datetime import datetime

from libs.Daemon import Daemon
from libs.Config import Config
from libs.Mosquitto import Mosquitto
from libs.Cosm import Cosm

class MQTT2Cosm(Daemon):

    debug = True
    mqtt = None
    cosm = None
    feeds = {}

    def log(self, message):
        if self.debug:
            timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
            sys.stdout.write("[%s] %s\n" % (timestamp, message))
            sys.stdout.flush()

    def load(self, feeds):
        self.feeds = {}
        for feed, datastreams in feeds.iteritems():
            for datastream, topic in datastreams.iteritems():
                self.feeds[topic] = {'feed': feed, 'datastream': datastream}

    def cleanup(self):
        self.mqtt.disconnect()
        self.log("[INFO] Exiting")
        sys.exit()

    def mqtt_connect(self):
        self.mqtt.on_connect = self.mqtt_on_connect
        self.mqtt.on_disconnect = self.mqtt_on_disconnect
        self.mqtt.on_message = self.mqtt_on_message
        self.mqtt.on_subscribe = self.mqtt_on_subscribe
        self.mqtt.connect()

    def mqtt_on_connect(self, obj, result_code):
        if result_code == 0:
            self.log("[INFO] Connected to local MQTT broker")
            self.mqtt.send_connected()
            for topic, feed in self.feeds.iteritems():
                self.log("[DEBUG] Subscribing to %s" % topic)
                self.mqtt.subscribe(topic, 0)
        else:
            self.stop()

    def mqtt_on_disconnect(self, obj, result_code):
        if result_code != 0:
            time.sleep(3)
            self.mqtt_connect()

    def mqtt_on_subscribe(self, obj, mid, qos_list):
        self.log("Subscription with mid %s received." % mid)

    def mqtt_on_message(self, obj, msg):
        feed = self.feeds.get(msg.topic, None)
        if feed:
            cosm.push(feed['feed'], feed['datastream'], msg.payload)
            self.log("[DEBUG] Message routed from %s to %s:%s = %s" % (msg.topic, feed['feed'], feed['datastream'], msg.payload))

    def run(self):

        self.log("[INFO] Starting " + __app__ + " v" + __version__)
        self.mqtt_connect()

        while True:
            self.mqtt.loop()

if __name__ == "__main__":

    config = Config('mqtt2cosm.yaml')

    manager = MQTT2Cosm(config.get('daemon', 'pidfile', '/tmp/mqtt2cosm.pid'))
    manager.stdout = config.get('daemon', 'stdout', '/dev/null')
    manager.stderr = config.get('daemon', 'stderr', '/dev/null')
    manager.debug = config.get('daemon', 'debug', False)

    mqtt = Mosquitto(config.get('mqtt', 'client_id'))
    mqtt.host = config.get('mqtt', 'host')
    mqtt.port = config.get('mqtt', 'port')
    mqtt.keepalive = config.get('mqtt', 'keepalive')
    mqtt.clean_session = config.get('mqtt', 'clean_session')
    mqtt.qos = config.get('mqtt', 'qos')
    mqtt.retain = config.get('mqtt', 'retain')
    mqtt.status_topic = config.get('mqtt', 'status_topic')
    manager.mqtt = mqtt

    cosm = Cosm(config.get('cosm', 'api_key'))
    cosm.timeout = config.get('cosm', 'timeout', 10)
    manager.cosm = cosm

    manager.load(config.get('cosm', 'feeds', []))

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            manager.start()
        elif 'stop' == sys.argv[1]:
            manager.stop()
        elif 'restart' == sys.argv[1]:
            manager.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)

