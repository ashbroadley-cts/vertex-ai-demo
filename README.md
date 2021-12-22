# Vertex AI Demo

This demo shows the usage of Vertex AI Pipelines for training, deploying and performing batch predictions an AutoML Tabular Classification model.

## How To Use

### Set up GCP

1. Create a new GCP Project and enable to following APIs:
    * BigQuery
    * Cloud Storage
    * Vertex AI
1. Create a new BQ Dataset, the name isn't that important, but will be used later
1. Create a new GCS Bucket, again, the name isn't important but it will be used later
1. Create a new Service Account with the following roles:
    * BigQuery Admin
    * Storage Admin
    * Vertex AI Administrator

Keep the BQ Dataset & Table name and Storage Bucket name handy for later.

### Create Prediction Data

1. In the BQ SQL Editor run the following query: 
    ```
select * except (Class) from `bigquery-public-data.ml_datasets.ulb_fraud_detection` order by V2 desc limit 100
    ```
1. Save the results to a new table in the previously created BQ Dataset

### Generate the Pipeline

1. Ensure you have this repository cloned somewhere with Python available
1. In the repository directory, run `pip install -r requirements.txt` to install the dependencies
1. Then run `python tabular-classification-pipeline.py` to generate the Vertex AI Pipeline

### Run the Pipeline

1. Open the [Vertex AI Pipelines console](https://console.cloud.google.com/vertex-ai/pipelines)
1. Click "Create Run"
1. Enter the following details:
    * File: Browse to the JSON file generated as part of the [Generate the Pipeline](#generate-the-pipeline) section
    * Leave "Pipeline name" and "Run name" as the defaults
    * Click "Advanced Options" and under "Service Account", select the SA you created as part of the [Set up GCP](#set-up-gcp) section
    * Click "Continue"
    * GCS output directory: enter the name of the Storage Bucket created earlier in the format `gs://$MY_BUCKET_NAME`
    * Under "Pipeline arameters", enter the following:
        * prediction_dataset: The name of the BQ dataset created during GCP setup
        * prediction_table:  The name of the BQ table created when during the [Create Prediction Data](#create-prediction-data) step
        * project_id: the name of the project created earlier
        * training_dataset: `bq://bigquery-public-data.ml_datasets.ulb_fraud_detection`
    * Click "Submit"

The pipeline will take a couple of hours to run the first it is submitted.

## Viewing Batch Predictions

When the pipeline has completed, the batch predictions will be saved to a table in the BQ Dataset previously created named something like `predictions_YYYY_MM_DDTHH_mm_ss_sssZ`

In the results, the predicted "Class" column `predicted_Class` contains a struct that represents the confidence for each potential "Class" classes. The higher the value (with a maximum of 1) the more confidence AutoML had that the prediction resulted in that classification.

## Performing Online Predictions

The pipeline deploys the trained model to an endpoint to be used for online predictions. To perform online predctions, follow the instructions below:

1. Go to the [Vertex AI Endpoints console](https://console.cloud.google.com/vertex-ai/endpoints)
1. Select the "automl-tabular-classification-endpoint" endpoint
1. Click "Sample Request"
1. Copy the ENDPOINT_ID & PROJECT_ID environment variables
1. Export the two previous environment variables and set `INPUT_DATA_FILE=./online-predictions.json`
1. Run the following command:

```
curl \
-X POST \
-H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
https://us-central1-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/us-central1/endpoints/${ENDPOINT_ID}:predict \
-d "@${INPUT_DATA_FILE}"
```

The response should be something akin to the following:

```
{
  "predictions": [
    {
      "scores": [
        0.04515920951962471,
        0.95484077930450439
      ],
      "classes": [
        "0",
        "1"
      ]
    },
    {
      "scores": [
        0.011245277710258961,
        0.98875468969345093
      ],
      "classes": [
        "0",
        "1"
      ]
    }
  ],
  "deployedModelId": "4284444969722183680",
  "model": "projects/671198661743/locations/us-central1/models/3880911008188858368",
  "modelDisplayName": "tabular-classification"
}
```

In the response, each object in the `predictions` array contains the confidence level for each classification in the same order as they were submitted in the [online-predictions.json file](online-predictions.json)
