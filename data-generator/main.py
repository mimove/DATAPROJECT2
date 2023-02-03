import docker
import sys, getopt
import time
import os
import uuid
import random
import datetime

print("#############################")
print("Starting Generator execution")
print("#############################")

topcontainers = 0
elapsedtime = 0
containername=""
list_ids = []

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
    
    userid=genuserid(list_ids)
    list_ids
    cmd=f"docker run --name {userid} -e TIME_ID={elapsedtime} -e USER_ID={userid} -d {containername}:latest"
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
   try:
      opts, args = getopt.getopt(argv,"t:e:i:",["topcontainers=","elapsedtime=","imagename="])
   except getopt.GetoptError:
      print('main.py -t <topcontainers> -e <elapsedtime> -i <imagename>')
      sys.exit(2)
   for opt, arg in opts:
      if opt in ("-h", "--help"):
         print('main.py -t <topcontainers> -e <elapsedtime> -n <imagename>')
         print(" elapsedtime: int (seconds)")
         print(" topcotainers: int (top number of concurrent clients)")
         print(" image: string (image name)")
         sys.exit()
      elif opt in ("-t", "--topcontainers"):
         topcontainers = int(arg)
      elif opt in ("-e", "--elapsedtime"):
         elapsedtime = int(arg)
      elif opt in ("-i", "--image"):
         containername = arg
   print(f"Top Containers: {topcontainers}")
   print(f"Elapsed Time: {elapsedtime}")
   print(f"Container name: {containername}")

   #### MIMOVE CODE ######

   # Creating a list of limited IDs for the solar panels
   
   for i in range(topcontainers):
      list_ids.append(uuid.uuid4().hex)

if __name__ == "__main__":
   main(sys.argv[1:])



while True:
   numcon=getcontainers()
   print(f"Currently running containers: {len(containers)}")

   for i in list_ids:
      data = {}

      time_now = datetime.datetime.now() 

      data["userid"]=i

      data["power_panel"] = 0

      data["current_status"] = 0

      data["current_time"] = time_now.strftime("%d/%m/%Y, %H:%M:%S")

      print(data)




   if numcon<topcontainers:
    create=random.randint(0,topcontainers-numcon)

    print(f"Containers to be created: {create}")
    for i in range(0,create):
        ##### MIMOVE
        # Ading userid as output to avoid creating a container with the same name as another container that it's running
        [output, userid] = createcontainer()
        list_ids.remove(userid)
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
