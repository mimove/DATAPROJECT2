import json
import os
import time
import numpy as np
import datetime
from datetime import timedelta

#Import libraries
import uuid
import random
import logging
import argparse
import google.auth
from google.cloud import pubsub_v1



user_id=os.getenv('USER_ID')
topic_name=os.getenv('TOPIC_ID')
project_id=os.getenv('PROJECT_ID')
time_lapse=int(os.getenv('TIME_ID'))
time_ini = datetime.datetime.strptime(os.getenv('TIME_NOW'), '%Y-%m-%d %H:%M:%S.%f')


## Variables for testing purpouses
# user_id='12345'
# time_lapse=1
# project_id = 'deft-epigram-375817'
# topic_name= 'panels_info'
# time_ini = datetime.datetime.now()


# Getting GCP credentials from JSON. This file is not uploaded to GitHub. Each user
# must create its own file from Service Account
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]='./run.json'
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id


class PubSubMessages:
    """ Publish Messages in our PubSub Topic """

    def __init__(self, project_id, topic_name):
        self.publisher = pubsub_v1.PublisherClient()
        self.project_id = project_id
        self.topic_name = topic_name

    def publishMessages(self, message):
        json_str = json.dumps(message)
        topic_path = self.publisher.topic_path(self.project_id, self.topic_name)
        publish_future = self.publisher.publish(topic_path, json_str.encode("utf-8"))
        logging.info("A New transaction has been registered. Id: %s", message['Panel_id'])

    def __exit__(self):
        self.publisher.transport.close()
        logging.info("PubSub Client closed.")




def run_generator(project_id, topic_name, data):
   pubsub_class = PubSubMessages(project_id, topic_name) 
   #Publish message into the queue 
   try:
      message: dict = data
      # Sending data to PubSub.
      pubsub_class.publishMessages(message)
      time.sleep(1)

   except Exception as err:
      logging.error("Error while inserting data into out PubSub Topic: %s", err)
   finally:
      pubsub_class.__exit__()


def generatedata(maxpow):

    global time_ini

    # Conversion from hours to seconds and minutes to seconds
    data={}

    h2sec = 3600

    min2sec = 60


    ######################
    #INTERVAL OF N HOURS

    delta_hour = 6
    
    #######################
    # INTERVAL OF N MINUTES FOR TESTING PURPOUSES
    #######################

    delta_min = 0

    #Defining initial time from the variables comming from data-generator/main.py
    initial_time = time_ini.hour * h2sec + time_ini.minute * min2sec

    final_time = (time_ini.hour + delta_hour) * h2sec + (time_ini.minute + delta_min) * min2sec

    mean_time = (initial_time + final_time) / 2
    #######################

    time_now= datetime.datetime.now()-timedelta(minutes=0)+timedelta(hours=1)


    current_time_seconds = time_now.hour * h2sec + time_now.minute * min2sec + time_now.second

    # Equation to calculate the instantaneous power, based on the sech(x), which has a similar shape to that of the normal distribution
    power_panel = maxpow/(np.cosh((current_time_seconds-initial_time)*((delta_hour)*0.5/(mean_time-initial_time))-(delta_hour)*0.5)**(1))

    #Defining information of each solar panel: ID, power, status=1(active) and timestamp
    data["Panel_id"]=str(user_id)

    data["power_panel"] = float(power_panel)

    data["current_status"] = str(1)

    print(power_panel)

    data["current_time"] = str(time_now)

    return data


def senddata(maxpow):
    global time_now
    global time_ini


    data = generatedata(maxpow)

    print(data)

    # Using run_generator function 
    run_generator(project_id, topic_name, data)



maxpow = 400 * random.uniform(0.8, 1.2) # Max. power of each solar panel. It can be from -20% to +20% of 400W


while True:
    senddata(maxpow)
    logging.getLogger().setLevel(logging.INFO)
    time.sleep(time_lapse)
