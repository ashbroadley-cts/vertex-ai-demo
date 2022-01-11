from google.cloud import aiplatform

import os
import argparse

parser = argparse.ArgumentParser(description='')
parser.add_argument('--project', dest='project',  help='The GCP Project to run the pipeline in')
parser.add_argument('--pipeline-root', dest='pipeline_root', help='The root of the pipeline')
parser.add_argument('--service-account', dest='service_account', help='The Service Account to run the pipeline as')
parser.add_argument('--version', dest='version', help='The version of the pipeline')
parser.add_argument('--training-data', dest='training_data', help='The BQ data used for training')
parser.add_argument('--prediction-dataset', dest='prediction_dataset', help='The dataset that contains the prediction data')
parser.add_argument('--prediction-table', dest='prediction_table', help='The table containing data to predict against')
parser.add_argument('--location', dest='location', default='us-central1', help='The GCP region to run the pipeline in')
args = parser.parse_args()

project_id = args.project
pipeline_root_path = args.pipeline_root
service_account = args.service_account
version = args.version
training_data = args.training_data
prediction_dataset = args.prediction_dataset
prediction_table = args.prediction_table
location = args.location

job = aiplatform.PipelineJob(
    display_name = "automl-fraud-pipeline",
    template_path = pipeline_root_path + "/pipelines/" + version + "/automl_fraud_pipeline.json",
    parameter_values = {
        "project_id":project_id,
        "training_dataset":training_data,
        "prediction_dataset":prediction_dataset,
        "prediction_table":prediction_table
        },
    project = project_id,
    location = location,
    pipeline_root = pipeline_root_path
)

job.submit(service_account = service_account)
