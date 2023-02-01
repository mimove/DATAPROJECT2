## Serverless_Data_Processing_GCP
# EDEM_Master_Data_Analytics

""" Data Stream Generator:
The generator will publish a new record simulating a new transaction in our site.""" 

#Import libraries
import json
import time
import uuid
import random
import logging
import argparse
import os
import numpy as np
import google.auth
from faker import Faker
from datetime import datetime
from google.cloud import pubsub_v1

fake = Faker()

#project_id = "solar-376515"
#topic_name = "projects/solar-376515/topics/Panel1"


#Input arguments
parser = argparse.ArgumentParser(description=('Aixigo Contracts Dataflow pipeline.'))
parser.add_argument(
                '--project_id',
                required=True,
                help='GCP cloud project name.')
parser.add_argument(
                '--topic_name',
                required=True,
                help='PubSub topic name.')
 
args, opts = parser.parse_known_args()

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
        logging.info("A New transaction has been registered. Id: %s", message['user_id'])

    def __exit__(self):
        self.publisher.transport.close()
        logging.info("PubSub Client closed.")
            

#Generator Code
def generateMockData():
    
    global time_now 

    data={}

    user_id = random.choice(['pF8z9GBG', 'XsEOhUOT', '89x5FhyA', 'S3yG1alL', '5pz386iG'])

    h2sec = 3600

    min2sec = 60

    # initial_time = 13*h2sec

    # final_time = 21*h2sec

    time_now = datetime.now() 

    current_minute_seconds = time_now.minute * 60 + time_now.second

    current_time_seconds = time_now.hour * 3600 + time_now.minute * 60 + time_now.second

    initial_time = time_now.minute * min2sec

    final_time = (time_now.minute + 8) * min2sec

    mean_time = (initial_time+final_time) / 2

    maxpow = 400

    power_panel = maxpow/(np.cosh((current_minute_seconds-initial_time)*(4/(mean_time-initial_time))-4)**(0.8)) 

    data["user_id"]= user_id

    data["power_panel"] = power_panel

    data["current_time"] = str(time_now)

    return data


def run_generator(project_id, topic_name):
    pubsub_class = PubSubMessages(project_id, topic_name)
    #Publish message into the queue every 5 seconds
    try:
        while True:
            message: dict = generateMockData()
            pubsub_class.publishMessages(message)
            #it will be generated a transaction each 2 seconds
            time.sleep(5)
    except Exception as err:
        logging.error("Error while inserting data into out PubSub Topic: %s", err)
    finally:
        pubsub_class.__exit__()

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    run_generator(args.project_id, args.topic_name)
