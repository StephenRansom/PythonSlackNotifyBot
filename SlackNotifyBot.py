# relies on python slackclient
# install with pip install slackclient
# Should ideally be run as a daemon or service
# Reads configuration from a file, if file does not exist, runs on built in defaults


import sys
import os
from slackclient import SlackClient

  

class Monitor():
    watchDirectory = "."

    def loadSettings():
        try:
            #open file
            print("opening")
        except:
            #file not found, load defaults
            print("Could not open settings")

    print("I'm watching")

class Alerter:
    print("This is an alert")


if __name__ == '__main__':
    monitor = Monitor()