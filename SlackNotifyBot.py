# relies on python slackclient
# install with pip install slackclient
# Should ideally be run as a daemon or service
# Reads configuration from a file, if file does not exist, runs on built in defaults


import sys
import os
import time
from slackclient import SlackClient


class Monitor():
    def load_default_settings(self):
        self.watchDirectory = "."
        self.checkInterval = 5 
        self.maxAlertFrequency = 10 #greater or equal to check interval
        self.slackChannel="alert_bot", 
        self.slackMessageText="ALERT! Bose is not receiving new files! @Ransom\t {}".format(time.ctime()), 
        self.slackBotUsername='Alert Bot'
        self.slackIconEmoji=':robot_face:'
        self.slackReplyBroadcast=True
    
    def load_slack_token(self):
        try:
            slackFileObject = open("SlackToken.txt", "r")
        except:
            self.log.write("SlackToken.txt not found")
            sys.exit("SlackToken.txt not found, exiting")

        self.slackToken = slackFileObject.readline()

    def load_custom_settings(self):
        self.log.write("Loading Custom Settings\n")
        try:
            #open file
            settingsFileObject = open("settings.cfg", "r")
            
        except:
            #file not found, load defaults
            self.log.write("Could not open settings.cfg\n")
        
        #load defaults for now, will add file parsing later
        self.load_default_settings()
        self.errorTolerance = self.maxAlertFrequency / self.checkInterval
        if(self.errorTolerance <= 1):
            self.log.write("error tolorance too low: {}\n".format(self.errorTolerance))
            self.errorTolerance = 1

    
    def process_error(self):
        """ Will raise an alert if criteria is met
            if this is the first check that returned a failure, send alert 
            if we have just sent an alert, wait until we exceed the errorTolerance to generate another alert to avoid spam
        """
        self.alertCount += 1
        if(self.alertCount >= self.errorTolerance): 
            self.log.write("Alert count: {}, errorTolerance: {}\n".format(self.alertCount, self.errorTolerance))           
            self.alertCount = 0
            self.process_error()
        elif(self.alertCount == 1):
            self.send_alert(self.slackChannel, self.slackMessageText, self.slackBotUsername, self.slackIconEmoji, self.slackReplyBroadcast)


    
    def send_alert(self, slackChannel, slackMessageText, slackBotUsername, slackIconEmoji, slackReplyBroadcast):
        """Sends alert to Slack Channel"""
        self.log.write("ALERT! There are no new files!\n")
        self.log.flush()
        slackClientObject = SlackClient(self.slackToken)

        slackClientObject.api_call('chat.postMessage', 
            channel= slackChannel, 
            text= slackMessageText, 
            username= slackBotUsername,
            icon_emoji= slackIconEmoji,
            reply_broadcast= slackReplyBroadcast)

    
    def update_file_count(self):
        """ Checks to make sure the number of files in self.watchDirectory is increasing
            attempts to raise alert via a call to processError if file count is not increasing
        """
        newFileCount = sum(1 for f in os.listdir(self.watchDirectory) if os.path.isfile(os.path.join(self.watchDirectory, f)) and f[0] != '.')
        self.log.write("current file count: {} \n".format(newFileCount))

        if(self.fileCount < newFileCount):
            self.fileCount = newFileCount
        else:
            self.process_error()

    def run(self):
        self.load_custom_settings()
        x=0
        try:
            while x < 11:
                self.log.write("looping\n")
                time.sleep(self.checkInterval)
                self.update_file_count()
                x += 1
        except BaseException as e:
            print("watcher has exited!, {}".format(e))
            self.log.write("watcher has exited!, {}".format(e))
            self.log.flush()
    
    def __init__(self):  
        self.log = open("./SlackNotifyLog.txt","w")
        self.log.write("------Initializing------\n")              
        self.load_slack_token()
        self.load_default_settings()
        self.load_custom_settings()
        self.fileCount = 0
        self.alertCount = 0
        


class SettingsParser():
    def __init__(self):
        print("Haven't written this class yet")

if __name__ == '__main__':
    monitor = Monitor()
    monitor.run()