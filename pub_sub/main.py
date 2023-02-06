import docker
import sys, getopt
import os
import datetime

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

topcontainers = 0
elapsedtime = 0
containername=""
list_ids = []
project_id=""
topic_name=""

containers=[]

def getcontainers():
    cmd=f"docker ps | grep -c {containername}"
    stream = os.popen(cmd)
    output = stream.read()
    return int(output)

def genuserid(list_ids):
   #  print('Number of containers: {}'.format(list_ids))

    # Selecting a random id from list_ids as the new container and solar panel
    return random.choice(list_ids)

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
    
    userid=genuserid(list_ids)
    cmd=f"docker run --name {userid} -e TIME_ID={elapsedtime} -e USER_ID={userid} -e TOPIC_ID={topic_name} -e PROJECT_ID={project_id} -d {containername}:latest"
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

   #### MIMOVE CODE ######

   # Creating a list of limited IDs for the solar panels
   
   for i in range(topcontainers):
      list_ids.append(uuid.uuid4().hex)


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


if __name__ == "__main__":
    main(sys.argv[1:])
    logging.getLogger().setLevel(logging.INFO)
   #  run_generator(args.project_id, args.topic_name)


while True:
   numcon=getcontainers()
   print(f"Currently running containers: {len(containers)}")

   for i in list_ids:
      data = {}

      time_now = datetime.datetime.now() 

      data["Panel_id"]=str(i)

      data["power_panel"] = str(0)

      data["current_status"] = str(0)

      # data["current_time"] = str(time_now)

      run_generator(project_id, topic_name, data)
      #it will be generated a transaction each 2 seconds
      time.sleep(2)


   
   if int(numcon)<int(topcontainers):
      create=random.randint(0,topcontainers-numcon)

      print(f"Containers to be created: {create}")
      for i in range(0,create):
         ##### MIMOVE
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
         # 10% probabilidad de eliminar container
         deletecontainer(item)

         #### MIMOVE #####
         # Adding userid back to the list
         list_ids.append(item)
   
         
   time.sleep(1)



