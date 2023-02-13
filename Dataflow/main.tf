provider "google" {
  version = "3.53.0"
  region  = "europe-west1"
}

resource "google_dataflow_flex_template_job" "big_data_job" {
    provider                = google-beta
    name                    = "dataflow-flextemplates-job"
    container_spec_gcs_path = "gs://edem-serverless-bucket/data-project2-flowtemplate.json"
    project = "deft-epigram-375817"
    region = "europe-west1"


  parameters = {
    input_subscription = "panels_info-sub"
    output_topic       = "panels_output"
    output_bigquery    = "solarPanelsDP2.Panel_Data"
    output_bigquery_agg = "solarPanelsDP2.Panel_Data_agg"
    temp_location      = "gs://deft-epigram-375817/tmp"
    staging_location   = "gs://deft-epigram-375817/stg"
  }
}