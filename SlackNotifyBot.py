# relies on python slackclient
# install with pip install slackclient
# Should ideally be run as a daemon or service
# Reads configuration from a file, if file does not exist, runs on built in defaults


import sys
import os
from slackclient import SlackClient

  

class Monitor():
    def loadDefaultSettings(self):
        self.watchDirectory = "."
        self.checkInterval = 5

    def loadSettings(self):
        print("loadingSettings")
        try:
            #open file
            settingsFileObject = open("settings.cfg", "r")
            print(settingsFileObject)
        except OSError:
            #file not found, load defaults
            print("Could not open settings")
        
        #load defaults for now, will add file parsing later
        self.loadDefaultSettings()
        print(self.watchDirectory)
        print(self.checkInterval)

    print("I'm watching")

class Alerter:
    print("This is an alert")


if __name__ == '__main__':
    monitor = Monitor()
    monitor.loadSettings()