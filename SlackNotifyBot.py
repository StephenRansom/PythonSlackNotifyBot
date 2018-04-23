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
        
    def load_settings(self):
        config = configparser.ConfigParser()
        config['DEFAULT'] = {
            'watchDirectory' : '.',
            'checkInterval' : '5',
            'contiguousErrorsUntilAlert': '1',
            'contiguousErrorsAfterAlert': '10',
            'slackMessageText' : 'alert! <!channel>',
            'slackIconEmoji' : ':robot_face:',
            'slackReplyBroadcast' : 'True',
            'defaultValue' : '42',
            'slackBotUsername' : "Alert Bot"            
        }
        try:
            #open file
            config.read("settings.cfg")
            self.log.write("Successfully opened settings file\n")
        except BaseException as e:
            #file not found, load defaults
            self.exit("Could not open settings.cfg\n{}".format(e))

        try:
            self.watchDirectory = config.get("Monitor Settings", "watchDirectory")
            self.checkInterval = config.getint("Monitor Settings", "checkInterval") 
            self.contiguousErrorsUntilAlert = config.getint("Monitor Settings", "contiguousErrorsUntilAlert")
            self.contiguousErrorsAfterAlert = config.getint("Monitor Settings", "contiguousErrorsAfterAlert")
            self.slackChannelName = config.get("Slack Settings", "slackChannelName")  
            self.slackMessageText = config.get("Slack Settings", "slackMessageText") + " {}".format(time.ctime()) 
            self.slackBotUsername = config.get("Slack Settings", "slackBotUsername")
            self.slackIconEmoji= config.get("Slack Settings", "slackIconEmoji")
            self.slackReplyBroadcast= config.getboolean("Slack Settings", "slackReplyBroadcast")          
        except configparser.NoOptionError as e:
            self.exit("encountered Exception {}".format(e))

    def exit(self, message):
        self.log.write(message + '\nExiting {}'.format(time.ctime()))
        self.log.flush()
        sys.exit(message + '\nExiting')


    def initialize_slack_client(self):
        try:
            slackFileObject = open("SlackToken.txt", "r")
        except:
            self.exit("SlackToken.txt not found")
            

        try:     
            self.slackClientObject = SlackClient(slackFileObject.readline())
        except:
            self.exit("Could not load slack client from provided slack token in SlackToken.txt!")
            

    
    def process_error(self):
        """ Will raise an alert if criteria is met
            if this is the first check that returned a failure, send alert 
            if we have just sent an alert, wait until we exceed the errorTolerance to generate another alert to avoid spam
        """
        print("Error count: {}".format(self.contiguousErrorCount))
        if(self.contiguousErrorCount == self.contiguousErrorsUntilAlert): 
            self.send_alert(self.slackChannelName, self.slackMessageText, self.slackBotUsername, self.slackIconEmoji, self.slackReplyBroadcast)
            print("Alert!")
        elif(self.contiguousErrorCount >= self.contiguousErrorsUntilAlert + self.contiguousErrorsAfterAlert):
            self.contiguousErrorCount = -1
            print("resetting error count")
     
        self.contiguousErrorCount += 1

    
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
            self.contiguousErrorCount = 0
        else:
            self.process_error()

    def run(self):
        
        try:
            while True:
                time.sleep(self.checkInterval)
                self.update_file_count()
        except BaseException as e:
            self.exit("Encountered exception {}".format(e))
            
    
    def __init__(self):  
        self.log = open("./SlackNotifyLog.txt","w")
        self.log.write("------Initializing------\n")
        self.load_settings()
        self.initialize_slack_client()
        self.fileCount = 0
        self.contiguousErrorCount = 0
      

if __name__ == '__main__':
    monitor = Monitor()
    monitor.run()