import docker
import sys, getopt
import os
import datetime
from datetime import timedelta

#Import libraries
import json
import time
import uuid
import random
import logging
import argparse
import google.auth
from google.cloud import pubsub_v1




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




print("#############################")
print("Starting Generator execution")
print("#############################")

# Env. variables initialization

topcontainers = 0
elapsedtime = 0
containername=""
list_ids = []
project_id=""
topic_name=""
time_ini=""

containers=[]

# Function to get the actual number of solar_panels active
def getcontainers():
    cmd=f"docker ps | grep -c {containername}"
    stream = os.popen(cmd)
    output = stream.read()
    return int(output)


# Selecting a random id from list_ids as the new container and solar panel
def genuserid(list_ids):
    return random.choice(list_ids)


# Function to delete the container
def deletecontainer(container_id):
    cmd=f"docker container rm {container_id} -f "
    stream = os.popen(cmd)
    output = stream.read()
    containers.remove(container_id)
    print(f"Container Removed with id: {container_id}")


def createcontainer():
    global list_ids
    global containername
    global elapsedtime
    global topcontainers
    global containers
    global project_id
    global topic_name
    global time_ini
    
    userid=genuserid(list_ids)

    # The following command creates a container for a solar panel, and it passes info about TIME, USER, TOPIC and docker network through env. variables
    cmd=f"docker run --name {userid} -e TIME_ID={elapsedtime} -e USER_ID={userid} -e TOPIC_ID={topic_name} -e TIME_NOW='{time_ini}' -e PROJECT_ID={project_id} -d {containername}:latest"
    stream = os.popen(cmd)
    output = stream.read().replace("\n","")
    if userid not in containers:
      containers.append(userid)
    print(f"Container Created with id: {output} for user: {userid}")
    return output, userid

def main(argv):
   global containername
   global elapsedtime
   global topcontainers
   global list_ids
   global project_id
   global topic_name

   try:
      opts, args = getopt.getopt(argv,"t:e:i:p:q:",["topcontainers=","elapsedtime=","image=","project_id=","topic_name="])
   except getopt.GetoptError:
      print('main.py -t <topcontainers> -e <elapsedtime> -i <image> -p <project_id> -q <topic_name>')
      sys.exit(2)
   for opt, arg in opts:
      if opt in ("-h", "--help"):
         print('main.py -t <topcontainers> -e <elapsedtime> -i <image> -p <project_id> -q <topic_name>')
         print(" elapsedtime: int (seconds)")
         print(" topcotainers: int (top number of concurrent clients)")
         print(" image: string (image name)")
         print(" project_id: string (GCP project name)")
         print(" topic_name: string (GCP pub/sub topic name)")
         sys.exit()
      elif opt in ("-t", "--topcontainers"):
         topcontainers = int(arg)
      elif opt in ("-e", "--elapsedtime"):
         elapsedtime = int(arg)
      elif opt in ("-i", "--image"):
         containername = arg
      elif opt in ("-p", "--project_id"):
         project_id = arg
      elif opt in ("-q", "--topic_name"):
         topic_name = arg
   
   
   print(f"Top Containers: {topcontainers}")
   print(f"Elapsed Time: {elapsedtime}")
   print(f"Container name: {containername}")
   print(f"Project name: {project_id}")
   print(f"Topic name: {topic_name}")


   # Creating a list of limited IDs for the solar panels
   for i in range(topcontainers):
      list_ids.append(uuid.uuid4().hex)


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


if __name__ == "__main__":
    main(sys.argv[1:])
    logging.getLogger().setLevel(logging.INFO)


time_ini = (datetime.datetime.now()-timedelta(minutes=0)).strftime('%Y-%m-%d %H:%M:%S.%f')

while True:
   numcon=getcontainers()
   print(f"Currently running containers: {len(containers)}")

   for i in list_ids:
      data = {}

      time_now = datetime.datetime.now()-timedelta(minutes=0)

      #Each solar panel has to send status=0 once it's offline, along with its ID and timestamp

      data["Panel_id"]=str(i)

      data["power_panel"] = float(0)

      data["current_status"] = str(0)

      data["current_time"] = str(time_now)

      run_generator(project_id, topic_name, data)
      time.sleep(2)


   
   if int(numcon)<int(topcontainers):
      create=random.randint(0,topcontainers-numcon)

      print(f"Containers to be created: {create}")
      for i in range(0,create):
         # Ading userid as output to avoid creating a container with the same name as another container that it's running
         [output, userid] = createcontainer()
         list_ids.remove(userid)
      if create == 0:
         print("No containers created this time") 
   else:
      print("No more containers can be created")
   time.sleep(2)

   for item in containers:
      prob=random.randint(0, 10)
      if prob == 0:
         # 10% probability of removing container
         deletecontainer(item)

         # Adding userid back to the list
         list_ids.append(item)
   
         
   time.sleep(1)



