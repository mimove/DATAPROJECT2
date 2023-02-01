import json
import os
import time
import numpy as np
import datetime


# user_id=os.getenv('USER_ID')
# topic_id=os.getenv('TOPIC_ID')
# time_lapse=int(os.getenv('TIME_ID'))


user_id='12345'
topic_id='topic_test'
time_lapse=2


time_now = datetime.datetime.now() 



def generatedata():

    global time_now 

    data={}

    h2sec = 3600

    min2sec = 60

    # initial_time = 13*h2sec

    # final_time = 21*h2sec

    time_now = datetime.datetime.now() 

    current_minute_seconds = time_now.minute * 60 + time_now.second

    current_time_seconds = time_now.hour * 3600 + time_now.minute * 60 + time_now.second

    initial_time = time_now.minute * min2sec

    final_time = (time_now.minute + 8) * min2sec

    mean_time = (initial_time+final_time) / 2

    maxpow = 400

    power_panel = maxpow/(np.cosh((current_minute_seconds-initial_time)*(4/(mean_time-initial_time))-4)**(0.8)) 

    data["userid"]=user_id

    data["power_panel"] = power_panel

    data["current_time"] = time_now

    return json.dumps(data)

def senddata():

    # Coloca el código para enviar los datos a tu sistema de mensajería
    # Utiliza la variable topic id para especificar el topico destino
    print(generatedata())



while True:
    senddata()
    time.sleep(time_lapse)
