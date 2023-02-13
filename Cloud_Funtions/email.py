from google.cloud import pubsub_v1
import base64
import json
import os
import smtplib



first_time_top = True
first_time_bottom = True

def send_email_alert(event, context):
    global first_time_top
    global first_time_bottom
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    message = json.loads(pubsub_message)
    power = float(message['power_panel'])

    threshold_top = 200

    if power > threshold_top:
        if first_time_top:
            first_time_top = False
            print(f"Comienza la producción. La potencia es {power}")

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
                print("Production started. Email sent!")
            except Exception as e:
                print("Something went wrong: {}".format(e))

    if 5 <= power <= 10:
        if first_time_bottom and not first_time_top:
            first_time_bottom = False

            print(f"Acaba la producción. La potencia es {power}")


            to = "martinezca.jorge@gmail.com"
            gmail_user = "pruebaemailsolar@gmail.com"
            gmail_password = os.environ["GMAIL_PASSWORD"]
            subject = "Low value alert"
            body = "Su instalación fotovoltaica ha dejado de producir energía"

            email_text = "From: {}\nTo: {}\nSubject: {}\n\n{}".format(gmail_user, to, subject, body)

            try:
                server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
                server.ehlo()
                server.login(gmail_user, gmail_password)
                server.sendmail(gmail_user, to, email_text.encode('utf-8'))
                server.close()
                print("Production finished. Email sent!")
            except Exception as e:
                print("Something went wrong: {}".format(e))


        