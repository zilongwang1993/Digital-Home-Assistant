#!/usr/bin/python
#
# Copyright 2012 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import httplib2
import sys
import time
import datetime
 
import xe #for the time comparator
from feed.date.rfc3339 import tf_from_timestamp #also for the comparator


from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run
import argparse
from oauth2client import tools
from oauth2client.client import flow_from_clientsecrets


from apscheduler.schedulers.background import BackgroundScheduler
import os, random #to play the mp3 later



# flow = OAuth2WebServerFlow(client_id, client_secret, scope)
def ringAlarm():

  songfile = random.choice(os.listdir("/Users/shuuhui/Desktop/Interstellar/disc01")) 
  print "File Selected:", songfile
  command ="afplay " + "/Users/shuuhui/Desktop/Interstellar/disc01/" +repr(songfile)+ " -t 100"
  print command
  os.system(command)

  
def checkTime():
  print "in checkTime"
  global wakeUpTime

  # epoch_time = time.time()  
  # tz_offset = - time.altzone / 3600
  # if tz_offset < 0:
  #     tz_offset_str = "-%02d00" % abs(tz_offset)
  # else:
  #     tz_offset_str = "+%02d00" % abs(tz_offset)
  # now= datetime.datetime.fromtimestamp(epoch_time).strftime("%Y-%m-%dT%H:%M:%S") 

  dt = datetime.datetime.strptime(wakeUpTime[:-6], '%Y-%m-%dT%H:%M:%S')
  now = time.localtime()
  print "wakeUpTime ",dt.hour,dt.minute
  if (dt.hour ==now.tm_hour) and (dt.minute==now.tm_min) and (dt.day ==now.tm_mday):
    print "time has come"
    ringAlarm()
  else:
    print "not yet"

  #print (wakeUpTime-now)
  #if time.strftime('%d-%m-%Y %H:%M',time.localtime(tf_from_timestamp(a_when.start_time))) == time.strftime('%d-%m-%Y %H:%M'):
  # if now> wakeUpTime:
  #   print "past due"
  # else:
  #   print "time has not come"


def main_logic():


  # Create a Storage object. This object holds the credentials that your
  # application needs to authorize access to the user's data. The name of the
  # credentials file is provided. If the file does not exist, it is
  # created. This object can only hold credentials for a single user, so
  # as-written, this script can only handle a single user.
  flow = flow_from_clientsecrets('/Users/shuuhui/Desktop/smart assistant/client_secret_401145376617-hh6vl1q96vfdre8vqb3ndeb3t5sbi8hm.apps.googleusercontent.com.json',
                               scope='https://www.googleapis.com/auth/calendar',
                               redirect_uri='http://example.com/auth_return')



  storage = Storage('credentials.dat')
  parser = argparse.ArgumentParser(parents=[tools.argparser])
  flags = parser.parse_args()
  #credentials = tools.run_flow(flow, storage, flags)
  # The get() function returns the credentials for the Storage object. If no
  # credentials were found, None is returned.
  

  # If no credentials are found or the credentials are invalid due to
  # expiration, new credentials need to be obtained from the authorization
  # server. The oauth2client.tools.run() function attempts to open an
  # authorization server page in your default web browser. The server
  # asks the user to grant your application access to the user's data.
  # If the user grants access, the run() function returns new credentials.
  # The new credentials are also stored in the supplied Storage object,
  # which updates the credentials.dat file.
  credentials =storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, storage, flags)
    storage.put(credentials)

  # Create an httplib2.Http object to handle our HTTP requests, and authorize it
  # using the credentials.authorize() function.
  http = httplib2.Http()
  http = credentials.authorize(http)

  # The apiclient.discovery.build() function returns an instance of an API service
  # object can be used to make API calls. The object is constructed with
  # methods specific to the calendar API. The arguments provided are:
  #   name of the API ('calendar')
  #   version of the API you are using ('v3')
  #   authorized httplib2.Http() object that can be used for API calls
  service = build('calendar', 'v3', http=http)

  try:

    # The Calendar API's events().list method returns paginated results, so we
    # have to execute the request in a paging loop. First, build the
    # request object. The arguments provided are:
    #   primary calendar for user
    start_date = datetime.date.today()
    end_date = datetime.date.today() + datetime.timedelta(days=1)


    #request = service.events().list(calendarId='primary')
    # Loop until all pages have been processed.
    # while request != None:
    #   # Get the next page.
    #   response = request.execute()
    #   # Accessing the response like a dict object with an 'items' key
    #   # returns a list of item objects (events).
    #   for event in response.get('items', []):
    #   #   # The event object is a dict object with a 'summary' key.
    #     event_uni=event.get('start').get('dateTime')
    #     event_start=datetime.datetime.strptime(event_uni, '%Y-%m-%dT%H:%M:%S.%fZ')
    #     if event_start >datetime.datetime.now():
    #      print event_start
    #     #print repr(event.get('summary', 'NO SUMMARY')) + '\n'

    #   request = service.events().list_next(request, response)
    # get the next 12 hours of events
    today=datetime.date.today()
    tmr =datetime.date.today() + datetime.timedelta(days=1)
    epoch_time = time.time()
    start_time = epoch_time - 3600  # 1 hour ago
    end_time = epoch_time + 12 * 3600  # 12 hours in the future
    tz_offset = - time.altzone / 3600
    if tz_offset < 0:
      tz_offset_str = "-%02d00" % abs(tz_offset)
    else:
      tz_offset_str = "+%02d00" % abs(tz_offset)
    #tz_offset_str = "+0000"
    myStart=today.strftime("%Y-%m-%dT%H:%M:%S") + tz_offset_str
    myEnd=tmr.strftime("%Y-%m-%dT%H:%M:%S") + tz_offset_str
    #print "Getting calendar events between: " + start_time + " and " + end_time

    events = service.events().list(calendarId='primary',timeMin =myStart, timeMax=myEnd, singleEvents=True).execute()
    #pprint.pprint(events)timeMin
    # for event in events['items']:
    #     print event["summary"]
    firstEvent= events['items'][0]
    print firstEvent['summary']
    firstEventTime = firstEvent['start']['dateTime']
    print firstEventTime
    global wakeUpTime

    if wakeUpTime != firstEventTime:
      wakeUpTime =firstEventTime
      print "assigned time " + wakeUpTime
    else:
      print "already assigned"
      checkTime()
      



  except AccessTokenRefreshError:
    # The AccessTokenRefreshError exception is raised if the credentials
    # have been revoked by the user or they have expired.
    credentials = tools.run_flow(flow, storage, flags)
    storage.put(credentials)
    print ('The credentials have been revoked or expired, please re-run'
           'the application to re-authorize')

wakeUpTime="-1";
#main_logic()
scheduler = BackgroundScheduler()
scheduler.add_job(main_logic,"interval",seconds=5)
try:
  scheduler.start()
except (KeyboardInterrupt, SystemExit): 
  pass

try:
        # This is here to simulate application activity (which keeps the main thread alive).
    while True: 
        time.sleep(2)
        
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()  