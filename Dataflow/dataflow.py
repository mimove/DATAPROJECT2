""" Serverless Data Processing with Dataflow
    Master Data Analytics EDEM
    Academic Year 2022-2023"""

""" Import libraries """

#Import beam libraries
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.transforms.combiners import MeanCombineFn
from apache_beam.transforms.combiners import CountCombineFn
from apache_beam.transforms.core import CombineGlobally
import apache_beam.transforms.window as window

from apache_beam.io.gcp.bigquery import parse_table_schema_from_json
from apache_beam.io.gcp import bigquery_tools

#Import Common Libraries
from datetime import datetime, timedelta
import argparse
import json
import logging
import requests


""" Helpful functions """
def ParsePubSubMessage(message):
    #Decode PubSub message in order to deal with
    pubsubmessage = message.data.decode('utf-8')
    #Convert string decoded in json format (element by element)
    row = json.loads(pubsubmessage)
    #Logging
    logging.info("Receiving message from PubSub:%s", pubsubmessage)
    #Return function
    return row




# DoFn Classes

# DoFn 01 : Add Processing Timestamp
# class AddTimestampDoFn(beam.DoFn):
#     """ Add the Data Processing Timestamp."""
#     #Add process function to deal with the data
#     def process(self, element):
#         #Add ProcessingTime field
#         element['current_time'] = str(datetime.now() + timedelta(hours=1))
#         #return function
#         yield element

#Create DoFn Class to add Window processing time and encode message to publish into PubSub

class add_processing_time(beam.DoFn):
    def process(self, element, window=beam.DoFn.WindowParam):
        window_start = window.start.to_utc_datetime() + timedelta(hours=1)
        window_end = window.end.to_utc_datetime() + timedelta(hours=1)
        output_data = {'power_panel': element, 'window_start': str(datetime.now()), 'window_end': str(datetime.now())}
        output_json = json.dumps(output_data)
        yield output_json.encode('utf-8')


class add_processing_time_bigquery(beam.DoFn):
    def process(self, element, window=beam.DoFn.WindowParam):
        window_start = window.start.to_utc_datetime() + timedelta(hours=1)
        window_end = window.end.to_utc_datetime() + timedelta(hours=1)
        output_data = {'Panel_id': str(element[0]), 'mean_power': element[1], 'window_start': str(window_start), 'window_end': str(window_end)}
        yield output_data


#Create DoFn Class to extract temperature from data
class agg_power(beam.DoFn):
    def process(self, element):
        power_panel = element['power_panel']
        yield power_panel

#Create DoFn Class to extract temperature from data
class get_panel(beam.DoFn):
    def process(self, element):
        panel_id = element['Panel_id']
        yield panel_id


""" Dataflow Process """
def run():

    """ Input Arguments"""
    parser = argparse.ArgumentParser(description=('Arguments for the Dataflow Streaming Pipeline.'))

    parser.add_argument(
                    '--project_id',
                    required=True,
                    help='GCP cloud project name')
    parser.add_argument(
                    '--input_subscription',
                    required=True,
                    help='PubSub Subscription which will be the source of data.')
    parser.add_argument(
                    '--output_topic',
                    required=True,
                    help='PubSub Topic which will be the sink for notification data.')
    parser.add_argument(
                    '--output_bigquery',
                    required=True,
                    help='Table where data will be stored in BigQuery. Format: <dataset>.<table>.')
    parser.add_argument(
                    '--output_bigquery_agg',
                    required=True,
                    help='Table where agg data will be stored in BigQuery. Format: <dataset>.<table>.')
    parser.add_argument(
                    '--bigquery_schema_path',
                    required=False,
                    default='./schema/bq_schema.json',
                    help='BigQuery Schema Path within the repository.')

                    
    args, pipeline_opts = parser.parse_known_args()

    """ BigQuery Table Schema """

    #Load schema from /schema folder
    with open('./schema/bq_schema.json') as file:
        input_schema = json.load(file)

    schema = bigquery_tools.parse_table_schema_from_json(json.dumps(input_schema))

    #Load schema from /schema folder
    with open('./schema/bq_schema_agg.json') as file:
        input_schema_agg = json.load(file)
     
    schema_agg = bigquery_tools.parse_table_schema_from_json(json.dumps(input_schema_agg))

    """ Apache Beam Pipeline """
    #Pipeline Options
    options = PipelineOptions(pipeline_opts, save_main_session=True, streaming=True, project=args.project_id)

    #Pipeline
    with beam.Pipeline(argv=pipeline_opts,options=options) as p:

        """ Part 01: Format data by masking the sensitive fields and checking if the transaction is fraudulent."""
        data = (
            p 
                | "Read From PubSub" >> beam.io.ReadFromPubSub(subscription=f"projects/{args.project_id}/subscriptions/{args.input_subscription}", with_attributes=True)
                # Parse JSON messages with Map Function
                | "Parse JSON messages" >> beam.Map(ParsePubSubMessage) 
                # | "Add Processing Time" >> beam.ParDo(AddTimestampDoFn())
        )

        """ Part 02: Writing data to BigQuery"""
        (
            data | "Write to BigQuery" >> beam.io.WriteToBigQuery(
                table = f"{args.project_id}:{args.output_bigquery}",
                schema = schema,
                create_disposition = beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                write_disposition = beam.io.BigQueryDisposition.WRITE_APPEND
            )
        )
        """ Part 03: Get mean value of powerpanel per Window and write to PubSub """
        (
            data 
                    | "Map by Panel_id" >> beam.Map(lambda x: (x['power_panel']))
                    | "WindowByMinute" >> beam.WindowInto(window.FixedWindows(30))
                    | "SumByWindow" >> beam.CombineGlobally(sum).without_defaults()
                    | "Add Window ProcessingTime" >>  beam.ParDo(add_processing_time())
                    | "WriteToPubSub" >> beam.io.WriteToPubSub(topic=f"projects/{args.project_id}/topics/{args.output_topic}", with_attributes=False)
        )  
 

        """ Part 04: Writing data_agg to BigQuery"""
        data_agg = (
            data 
                    | "BigQuery Map by Panel_id" >> beam.Map(lambda x: (x['Panel_id'], x['power_panel']))
                    | "BigQuery WindowByMinute" >> beam.WindowInto(window.FixedWindows(30))
                    | "BigQuery GroupByKey" >> beam.GroupByKey()
                    | "BigQuery MeanByWindow" >> beam.Map(lambda x: (x[0], sum(x[1])/len(x[1])))
                    | "BigQuery Window ProcessingTime" >>  beam.ParDo(add_processing_time_bigquery())

        ) 

        (
            data_agg | "Write to BigQuery agg" >> beam.io.WriteToBigQuery(
                table = f"{args.project_id}:{args.output_bigquery_agg}",
                schema = schema_agg,
                create_disposition = beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                write_disposition = beam.io.BigQueryDisposition.WRITE_APPEND
            )
        ) 
           

if __name__ == '__main__':
    #Add Logs
    logging.getLogger().setLevel(logging.INFO)
    #Run process
    run()

