from google.cloud import pubsub_v1
import base64
import json
import os
import smtplib


# Creating global variables
first_time_top = True
first_time_bottom = True

# Create function send_email_alert
def send_email_alert(event, context):
    #Call global variables
    global first_time_top
    global first_time_bottom
    
    #Read and decode pub/sub message
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    message = json.loads(pubsub_message)
    power = float(message['power_panel'])

    threshold_top = 200

    #Condition to send Starting Production Email
    if power > threshold_top and first_time_top:
    
        #First_time_top becomes False to not execute condition again
        first_time_bottom = True
        first_time_top = False  
        #Print log to check if it is working in GCP functions Logs      
        print(f"Production has started. Last 30 secs power is: {power}")

        #Email credentials and text
        to = "martinezca.jorge@gmail.com"
        gmail_user = "pruebaemailsolar@gmail.com"
        gmail_password = os.environ["GMAIL_PASSWORD"]
        subject = "High value alert"
        body = "Your Photovoltaic Plant has started producing energy"

        email_text = "From: {}\nTo: {}\nSubject: {}\n\n{}".format(gmail_user, to, subject, body)

        try:
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465) #Create SSL condtion with Gmail SMTP server in 465 port
            server.ehlo()
            server.login(gmail_user, gmail_password) #Log in in SMTP server with Gmail Credentials predefined
            server.sendmail(gmail_user, to, email_text.encode('utf-8')) #Sending email
            server.close()

            #Print log to ensure that emial was sent correctly
            print("Production started. Email sent!")
        except Exception as e:
            print("Something went wrong: {}".format(e))

    
    #Condition to send Finshing Production Email
    if 3 <= power <= 100:
        if first_time_bottom and not first_time_top:

            #First_time_bottom becomes False to not execute condition again
            first_time_bottom = False

            #Print log to check if it is working in GCP functions Logs      
            print(f"Production has stopped. Last 30 secs power is: {power}")

            #Email credentials and text
            to = "martinezca.jorge@gmail.com"
            gmail_user = "pruebaemailsolar@gmail.com"
            gmail_password = os.environ["GMAIL_PASSWORD"]
            subject = "Low value alert"
            body = "Your Photovoltaic Plant has stopped producing energy"

            email_text = "From: {}\nTo: {}\nSubject: {}\n\n{}".format(gmail_user, to, subject, body)

            try:
                server = smtplib.SMTP_SSL("smtp.gmail.com", 465) #Create SSL condtion with Gmail SMTP server in 465 port
                server.ehlo()
                server.login(gmail_user, gmail_password) #Log in in SMTP server with Gmail Credentials predefined
                server.sendmail(gmail_user, to, email_text.encode('utf-8')) #Sending email
                server.close()
                #Print log to ensure that emial was sent correctly
                print("Production finished. Email sent!")
            except Exception as e:
                print("Something went wrong: {}".format(e))
