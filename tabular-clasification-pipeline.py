import kfp
from kfp.v2 import dsl
from google.cloud import aiplatform
from google_cloud_pipeline_components import aiplatform as gcc_aip

# Define the workflow of the pipeline.
@dsl.pipeline(
    name="automl-tabular-classification")

def pipeline(
        project_id: str,
        training_dataset: str,
        prediction_dataset: str,
        prediction_table: str,
    ):
    # The first step of your workflow is a dataset generator.
    # This step takes a Google Cloud pipeline component, providing the necessary
    # input arguments, and uses the python variable `ds_op` to define its
    # output. Note that here the `ds_op` only stores the definition of the
    # output but not the actual returned object from the execution. The value
    # of the object is not accessible at the dsl.pipeline level, and can only be
    # retrieved by providing it as the input to a downstream component.
    ds_op = gcc_aip.TabularDatasetCreateOp(
        project=project_id,
        display_name="tabular-classification-dataset",
        bq_source=training_dataset
    )

    # The second step is a model training component. It takes the dataset
    # outputted from the first step, supplies it as an input argument to the
    # component (see `dataset=ds_op.outputs["dataset"]`), and will put its
    # outputs into `training_job_run_op`.
    training_job_run_op = gcc_aip.AutoMLTabularTrainingJobRunOp(
        project=project_id,
        display_name="tabular-classification-training",
        optimization_prediction_type="classification",
        dataset=ds_op.outputs["dataset"],
        target_column="Class",
        optimization_objective="maximize-au-prc",
        model_display_name="tabular-classification",
        training_fraction_split=0.8,
        validation_fraction_split=0.1,
        test_fraction_split=0.1,
        budget_milli_node_hours=1000,
    )

    # The following two steps are only needed for online predictions
    # The third and fourth step are for deploying the model.
    create_endpoint_op = gcc_aip.EndpointCreateOp(
        project=project_id,
        display_name = "automl-tabular-classification-endpoint",
    )

    model_deploy_op = gcc_aip.ModelDeployOp(
        model=training_job_run_op.outputs["model"],
        endpoint=create_endpoint_op.outputs['endpoint'],
        dedicated_resources_machine_type='n1-standard-4',
        dedicated_resources_min_replica_count=1,
        dedicated_resources_max_replica_count=1,
        traffic_split={"0":100},
    )

    ## We can also do a model batch predition as part of the pipeline
    batch_predict = gcc_aip.ModelBatchPredictOp(
        project=project_id,
        job_display_name=f"tabular-classification-predictions",
        model=training_job_run_op.outputs["model"],
        bigquery_source_input_uri=f'bq://{project_id}.{prediction_dataset}.{prediction_table}',
        bigquery_destination_output_uri=f'bq://{project_id}.{prediction_dataset}',
        instances_format = "bigquery",
        predictions_format = "bigquery"
    )

# Compile the pipeline into JSON
from kfp.v2 import compiler
compiler.Compiler().compile(pipeline_func=pipeline,
        package_path='automl_tabular_classification_pipeline.json')
