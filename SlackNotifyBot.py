# relies on python slackclient
# install with pip install slackclient
# Should ideally be run as a daemon or service
# Reads configuration from a file, if file does not exist, runs on built in defaults


import sys
import os
import time
import configparser
from slackclient import SlackClient


class Monitor():
    def load_default_settings(self):
        '''Default Settings are used in the case that another value is not provided in settings.cfg'''
        self.config['DEFAULT'] = {
            'watchDirectory' : '.',
            'checkInterval' : '5',
            'maxAlertFrequency' : '10',
            'slackMessageText' : 'alert! <!channel>',
            'slackIconEmoji' : ':robot_face:',
            'slackReplyBroadcast' : 'True',
            'defaultValue' : '42'
        }

        self.watchDirectory = "."
        self.checkInterval = 5 
        self.maxAlertFrequency = 10 #greater or equal to check interval
        self.slackChannelName="alert_bot", 
        self.slackMessageText="ALERT! Directory is not receiving new files! <!channel> {}".format(time.ctime()), 
        self.slackBotUsername='Alert Bot'
        self.slackIconEmoji=':robot_face:'
        self.slackReplyBroadcast= "true"
        self.errorTolerance = self.maxAlertFrequency / self.checkInterval
    
    def load_settings(self):
        self.config = configparser.ConfigParser()
        self.load_default_settings()
        try:
            #open file
            self.config.read("settings.cfg")
            self.log.write("Successfully opened settings file\n")
        except BaseException as e:
            #file not found, load defaults
            self.log.write("Could not open settings.cfg\n{}".format(e))


        print("Test Default Value:")
        print(self.config.get('Slack Settings','defaultValue'))
        self.log.flush()

    def exit(self, message):
        self.log.write(message + '\nExiting')
        self.log.flush()
        sys.exit(message + '\nExiting')


    def initialize_slack_client(self):
        try:
            slackFileObject = open("SlackTodken.txt", "r")
        except:
            self.exit("SlackToken.txt not found")
            

        try:     
            self.slackClientObject = SlackClient(slackFileObject.readline())
        except:
            self.exit("Could not load slack client from provided slack token in SlackToken.txt!")
            

    def load_custom_settings(self):
        """ Attempts to load custom settings from file
            If a valid setting is read for an attribute, the default setting will be overwritten
            Otherwise the default is kept
            Lines from settings.cfg that are preceeded with a '#' are ignored as comments
        """

    
        self.errorTolerance = self.maxAlertFrequency / self.checkInterval
        if(self.errorTolerance <= 1):
            self.log.write("error tolerance too low: {}\n".format(self.errorTolerance))
            self.errorTolerance = 1

    
    def process_error(self):
        """ Will raise an alert if criteria is met
            if this is the first check that returned a failure, send alert 
            if we have just sent an alert, wait until we exceed the errorTolerance to generate another alert to avoid spam
        """
        self.alertCount += 1
        if(self.alertCount >= self.errorTolerance): 
            self.log.write("Alert count: {}, errorTolerance: {}\n".format(self.alertCount, self.errorTolerance))    
            self.log.flush()       
            self.alertCount = 0
            self.process_error()
        elif(self.alertCount == 1):
            self.send_alert(self.slackChannelName, self.slackMessageText, self.slackBotUsername, self.slackIconEmoji, self.slackReplyBroadcast)


    
    def send_alert(self, slackChannelName, slackMessageText, slackBotUsername, slackIconEmoji, slackReplyBroadcast):
        """Sends alert to Slack Channel"""
        self.log.write("ALERT! There are no new files!\n")
        self.log.flush()
        

        self.slackClientObject.api_call('chat.postMessage', 
            channel = slackChannelName, 
            text = slackMessageText, 
            username = slackBotUsername,
            icon_emoji = slackIconEmoji,
            link_names=1)

    
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
        
        x=0
        try:
            while x < 2:
                self.log.write("looping\n")
                time.sleep(self.checkInterval)
                self.update_file_count()
                x += 1
        except BaseException as e:
            self.exit("Encountered exception {}".format(e))
            
    
    def __init__(self):  
        self.log = open("./SlackNotifyLog.txt","w")
        self.log.write("------Initializing------\n")
        self.load_settings()
        self.initialize_slack_client()
        self.fileCount = 0
        self.alertCount = 0
      

if __name__ == '__main__':
    monitor = Monitor()
    monitor.run()