import base64, json, sys, os
from google.cloud import bigquery
import logging


def pubsub_to_bigquery(event, context):
    #Add logs
    logging.getLogger().setLevel(logging.INFO)
    
    #Dealing with environment variables
    project_id = os.environ['PROJECT_ID']
    table = os.environ['BIGQUERY_TABLE_ID']

    #Read message from Pubsub (decode from Base64)
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')

    #Load json
    message = json.loads(pubsub_message)

    bq_client = bigquery.Client (project = project_id)

    bq_client.insert_rows_json(table, [message])

    # if message['power_panel'] != 0:
    #     insert.rows_json
    
    if message['power_panel'] != 0:
        logging.info ("Panel working")
    else:
        logging.info("Panel not working correctly")
    
    bq_client.close()
