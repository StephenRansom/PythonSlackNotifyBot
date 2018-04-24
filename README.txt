# PythonSlackNotifyBot
This bot monitors a directory for new contributions. 
If no new files are found within the specified time interval it raises an error
When contiguous errors pass a certain threshold an alert is sent to the specified slack channel  
  
Settings are stored in "settings.cfg"  
Your slack token should be stored on a single line in "SlackToken.txt"  
Logging information is stored in "SlackNotifyLog.txt"  

[Monitor Settings]  
  watchDirectory              
  	-directory to be monitored  
  checkInterval               
  	-Interval that the directory should be checked for new files (in seconds)  
  contiguousErrorsUntilAlert  
  	-Integer from 0 to max_int. When set to zero you will receive an alert on the first failed directory check, set to larger numbers for a larger initial tolorance to failed checks.
	-Recommended value is at least 1 to prevent receiving alerts from a slightly delayed file update  
  contiguousErrorsAfterAlert  
  	-Integer from 0 to max_int. This value allows for a delay after receiving the first error so that you aren't spammed with alerts while your process is running.  
  
Example configurations:
  #this configuration will send an alert for every single failed check once per minute in the current directory
  [Monitor Settings]
	  watchDirectory = .
	  checkInterval = 60
	  contiguousErrorsUntilAlert = 0
	  contiguousErrorsAfterAlert = 0
    
  #This is a more recommended configuration if you are expecting minutely updates.
  #It will wait until the second contiguous error to send an alert to account for time drift and slightly delayed updates
  #It will wait for 9 more contiguous errors before sending another alert, so as not to spam the slack channel needlessly
  #Effectively will send an alert every 11 minutes that it does not detect file updates in the parent directory
  [Monitor Settings]
	  watchDirectory = ..
	  checkInterval = 60
	  contiguousErrorsUntilAlert = 1
	  contiguousErrorsAfterAlert = 9
    
  EXAMPLE RUNTIME PROCESS:
  ------Initializing------
  check 0 failed
  check 1 failed: ALERT!  
  check 2 failed
  check 3 failed
  check 4 failed
  check 5 failed
  check 6 failed
  check 7 failed
  check 8 failed
  check 9 failed
  check 10 failed
  Contiguous error count reset 
  check 0 failed
  check 1 failed: ALERT!
  check 2 failed
  ----process back online, updates are recieved---
  Contiguous error count reset 
  check 0 passed
  check 0 passed
  ...
  
  
  
 Built-in Default Values: #will be used if these values are not provided in the settings.cfg file
  'watchDirectory' : '.',
  'checkInterval' : '60',
  'contiguousErrorsUntilAlert': '1',
  'contiguousErrorsAfterAlert': '9',
  'slackMessageText' : 'alert! <!channel>',
  'slackIconEmoji' : ':robot_face:',
  'slackReplyBroadcast' : 'True',
  'defaultValue' : '42',
  'slackBotUsername' : "Alert Bot"  
  
 Full Example Config:
 [Monitor Settings]
	watchDirectory = /absolutepathto/thisdirectory/
	checkInterval = 60
	contiguousErrorsUntilAlert = 1
	contiguousErrorsAfterAlert = 9
	
[Slack Settings]
	slackChannelName = alert_bot
	slackMessageText = 'ALERT! Directory is not receiving new files! <!channel>'
	slackBotUsername = Alert Bot
	slackIconEmoji = :robot_face:
	slackReplyBroadcast = True
  
  
TroubleShooting and Notes:
If you run into issues reading the config file, make sure there is a valid newline at the end of each option. 
I'd recommend manually pressing [enter] at the end of each value if in doubt. 

Only one log file is save at a time to prevent file buildup
  
  
  
  
