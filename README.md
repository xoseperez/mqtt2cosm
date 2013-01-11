# mqtt2cosm

This daemon will subscribe to an MQTT broker and push values to Cosm.com whenever a message is recevied from certain topics.

## Requirements

* python-yaml
<pre>sudo apt-get install python-yaml</pre>

* python-mosquitto
<pre>sudo apt-get install python-mosquitto</pre>

## Install

Just clone or extract the code in some folder. I'm not providing an setup.py file yet.

## Configuration

Rename or copy the mqtt2cosm.yaml.sample file to mqtt2cosm.yaml and edit it. The configuration is pretty straight forward:

### daemon

Just define the log file paths.

### mqtt

These are standard Mosquitto parameters. The status topic is the topic to post messages when the daemon starts or stops.

### cosm

Enter your cosm.com API key and a timeout value in seconds for POST and GET requests.
Define what topics to push where, the structure is as follows "feeds[feed][datastream] = topic".

## Running it

The util stays resident as a daemon. You can start it, stop it or restart it (to reload the configuration) by using:

<pre>python mqtt2cosm.py start|stop|restart</pre>



