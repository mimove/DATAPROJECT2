import json
import os
import time
import numpy as np
import datetime


user_id=os.getenv('USER_ID')
topic_id=os.getenv('TOPIC_ID')
time_lapse=int(os.getenv('TIME_ID'))
time_ini = datetime.datetime.strptime(os.getenv('TIME_NOW'), '%Y-%m-%d %H:%M:%S.%f')

# user_id='12345'
# topic_id='topic_test'
# time_lapse=2



def generatedata(maxpow):

    global time_ini

    data={}



    h2sec = 3600

    min2sec = 60


    ######################
    #INTERVAL OF N HOURS

    delta_hour = 4
    
    #######################
    # INTERVAL OF N MINUTES FOR TESTING PURPOUSES
    #######################

    delta_min = 0

    initial_time = time_ini.hour * h2sec + time_ini.minute * min2sec

    final_time = (time_ini.hour + delta_hour) * h2sec + (time_ini.minute + delta_min) * min2sec

    mean_time = (initial_time + final_time) / 2
    #######################

    time_now= datetime.datetime.now()-timedelta(minutes=0)

   #  current_minute_seconds = time_now.minute * 60 + time_now.second

    current_time_seconds = time_now.hour * h2sec + time_now.minute * min2sec + time_now.second

    # power_panel = maxpow/(np.cosh((current_minute_seconds-initial_time)*(4/(mean_time-initial_time))-4)**(0.8))*random.uniform(0.98, 1)

    power_panel = maxpow/(np.cosh((current_time_seconds-initial_time)*((delta_hour)*0.5/(mean_time-initial_time))-(delta_hour)*0.5)**((delta_hour)/2))

    data["Panel_id"]=user_id

    data["power_panel"] = power_panel

    data["current_status"] = 1

    data["current_time"] = time_now.strftime("%d/%m/%Y, %H:%M:%S")

    return json.dumps(data)

def senddata():

    # Coloca el código para enviar los datos a tu sistema de mensajería
    # Utiliza la variable topic id para especificar el topico destino
    
    print(generatedata())



while True:
    senddata()
    time.sleep(time_lapse)
