provider "google" {
  version = "3.53.0"
  region  = "europe-west1"
}

module "dataflow-flex-job" {
  source  = "terraform-google-modules/secured-data-warehouse/google//modules/dataflow-flex-job"
  version = "~> 0.1"
  project_id = "deft-epigram-375817"
  name   = "dataflow-solar"
  region     = "europe-west1"
  container_spec_gcs_path = "gs://edem-serverless-bucket/data-project2-flowtemplate.json"
  staging_location        = "gs://deft-epigram-375817/stg"
  temp_location           = "gs://deft-epigram-375817/tmp"
#   subnetwork_self_link    = "<subnetwork-self-link>"
#   kms_key_name            = "<fully-qualified-kms-key-id>"
#   service_account_email   = "<dataflow-controller-service-account-email>"

  parameters = {
    input_subscription = "panels_info-sub"
    output_topic       = "panels_output"
    output_bigquery    = "solarPanelsDP2.Panel_Data"
    output_bigquery_agg = "solarPanelsDP2.Panel_Data_agg"
    temp_location      = "gs://deft-epigram-375817/tmp"
    staging_location   = "gs://deft-epigram-375817/stg"
  }
}