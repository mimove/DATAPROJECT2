import json
import os
import time
import numpy as np
import datetime

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

# user_id='12345'
# time_lapse=1
# project_id = 'deft-epigram-375817'
# topic_name= 'panels_info'

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
      pubsub_class.publishMessages(message)
      time.sleep(1)

   except Exception as err:
      logging.error("Error while inserting data into out PubSub Topic: %s", err)
   finally:
      pubsub_class.__exit__()


def generatedata(maxpow):

    global time_now 

    data={}

    h2sec = 3600

    min2sec = 60


    #######################
    # INTERVAL OF 8 HOURS

    # initial_time = 13*h2sec

    # final_time = 21*h2sec
    #######################

    #######################
    # INTERVAL OF 8 MINUTES FOR TESTING PURPOUSES
    #######################

    # time_now = datetime.datetime.now() 

    initial_time = time_now.minute * min2sec

    final_time = (time_now.minute + 8) * min2sec

    mean_time = (initial_time+final_time) / 2
    #######################


    current_minute_seconds = time_now.minute * 60 + time_now.second

    current_time_seconds = time_now.hour * 3600 + time_now.minute * 60 + time_now.second


    power_panel = (maxpow/(np.cosh((current_minute_seconds-initial_time)*(4/(mean_time-initial_time))-4)**(0.8)))*random.uniform(0.98, 1)

    data["Panel_id"]=str(user_id)

    data["power_panel"] = str(power_panel)

    data["current_status"] = str(1)

    data["current_time"] = time_now.strftime("%d/%m/%Y, %H:%M:%S")
    # data["current_time"] = str(time_now)

    return data


def senddata(maxpow):
    global time_now
    # Coloca el código para enviar los datos a tu sistema de mensajería
    # Utiliza la variable topic id para especificar el topico destino

    data = generatedata(maxpow)

    print(data)

    run_generator(project_id, topic_name, data)




time_now = (datetime.datetime.now() +  datetime.timedelta(hours=1))

maxpow = 400 * random.uniform(0.9, 1)

while True:
    senddata(maxpow)
    logging.getLogger().setLevel(logging.INFO)
    time.sleep(time_lapse)
