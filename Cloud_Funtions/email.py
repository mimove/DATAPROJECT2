from google.cloud import pubsub_v1
import base64
import json
import os
import smtplib



first_time = True

def send_email_alert(event, context):
    global first_time
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    message = json.loads(pubsub_message)

    printeado = 50

    threshold = 50
    mean_power = json.loads(message['mean_power'])

    if mean_power > threshold:
        if first_time:
            # print('Creating alert: value {} is greater than threshold {}'.format(mean_power, threshold))
            first_time = False
            printeado = False

            to = "martinezca.jorge@gmail.com"
            gmail_user = "pruebaemailsolar@gmail.com"
            gmail_password = os.environ["GMAIL_PASSWORD"]
            subject = "High value alert"
            body = "Su instalación fotovoltaica ha comenzado a producir energía"

            email_text = "From: {}\nTo: {}\nSubject: {}\n\n{}".format(gmail_user, to, subject, body)

            try:
                server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
                server.ehlo()
                server.login(gmail_user, gmail_password)
                server.sendmail(gmail_user, to, email_text.encode('utf-8'))
                server.close()
                print("Email sent!")
            except Exception as e:
                print("Something went wrong: {}".format(e))

    # Cuando esté la primera condición completada. Añadir condición en la que cuando la mean power esté entre 5 y 10 por ejemplo se envíe otro correo. 
    # Ponemos 5 porque puede ser que se haya apagado una placa. Así no tenemos eso en cuenta