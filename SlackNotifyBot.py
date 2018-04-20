# relies on python slackclient
# install with pip install slackclient
# Should ideally be run as a daemon or service
# Reads configuration from a file, if file does not exist, runs on built in defaults


import sys
import os
import time
from slackclient import SlackClient


class Monitor():
    def loadDefaultSettings(self):
        self.watchDirectory = "."
        self.checkInterval = 5 
        self.maxAlertFrequency = 10 #greater or equal to check interval
    
    def loadSlackToken(self):
        try:
            slackFileObject = open("SlackToken.txt", "r")
        except:
            self.log.write("SlackToken.txt not found")
            sys.exit("SlackToken.txt not found, exiting")

        self.slackToken = slackFileObject.readline()

    def loadSettings(self):
        self.log.write("loadingSettings\n")
        try:
            #open file
            settingsFileObject = open("settings.cfg", "r")
            
        except:
            #file not found, load defaults
            self.log.write("Could not open settings\n")
        
        #load defaults for now, will add file parsing later
        self.loadDefaultSettings()
        self.errorTolerance = self.maxAlertFrequency / self.checkInterval
        if(self.errorTolerance <= 1):
            self.log.write("error tolorance too low: {}\n".format(self.errorTolerance))
            self.errorTolerance = 1

    #if this is the first check that returned a failure, send alert 
    #if we have just sent an alert, wait until we exceed the error tolorance to generate another alert to avoid spam
    def processError(self):
        self.alertCount += 1
        if(self.alertCount >= self.errorTolerance): 
            self.log.write("Alert count: {}, errorTolerance: {}\n".format(self.alertCount, self.errorTolerance))           
            self.alertCount = 0
            self.processError()
        elif(self.alertCount == 1):
            self.sendAlert()

    def sendAlert(self):
        self.log.write("ALERT! There are no new files!\n")
        self.log.flush()
        slackClientObject = SlackClient(self.slackToken)

        slackClientObject.api_call('chat.postMessage', 
            channel="alert_bot", 
            text="ALERT! Bose is not receiving new files! @Ransom\t {}".format(time.ctime()), 
            username='Alert Bot',
            icon_emoji=':robot_face:',
            reply_broadcast=True)


    def updateFileCount(self):
        newFileCount = sum(1 for f in os.listdir(self.watchDirectory) if os.path.isfile(os.path.join(self.watchDirectory, f)) and f[0] != '.')
        self.log.write("current file count: {} \n".format(newFileCount))

        if(self.fileCount < newFileCount):
            self.fileCount = newFileCount
        else:
            self.processError()

    def run(self):
        self.loadSettings()
        x=0
        try:
            while x < 11:
                self.log.write("looping\n")
                time.sleep(self.checkInterval)
                self.updateFileCount()
                x += 1
        except BaseException as e:
            print("watcher has exited!, {}".format(e))
            self.log.write("watcher has exited!, {}".format(e))
    
    def __init__(self):
        self.loadDefaultSettings()
        self.fileCount = 0
        self.alertCount = 0
        self.log = open("./SlackNotifyLog.txt","w")
        self.log.write("initializing\n")
        self.loadSlackToken()


if __name__ == '__main__':
    monitor = Monitor()
    monitor.run()