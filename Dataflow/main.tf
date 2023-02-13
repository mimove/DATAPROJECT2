provider "google" {
  version = "3.28.0"
  region  = "europe-west1"
}

module "dataflow_job" {
  source = "terraform-google-modules/dataflow/google"

  project_id = "deft-epigram-375817"
  job_name   = "dataflow-solar"
  region     = "europe-west1"

  # Define the Flex template properties
  template_bucket = "edem-serverless-bucket"
  template_object = "data-project2-flowtemplate.json"
  sdk_language = "PYTHON"
  image = "gcr.io/deft-epigram-375817/dataflow/data-project2:latest"

  # Define the job parameters
  parameters = {
    input_subscription = "panels_info-sub"
    output_topic       = "panels_output"
    output_bigquery    = "solarPanelsDP2.Panel_Data"
    output_bigquery_agg = "solarPanelsDP2.Panel_Data_agg"
    temp_location      = "gs://deft-epigram-375817/tmp"
    staging_location   = "gs://deft-epigram-375817/stg"
  }
}
