"""
Sample DAG using the TemplateDAGBuilder.

This DAG demonstrates how to use the TemplateDAGBuilder to create a DAG with
common patterns and configurations.
"""

from datetime import datetime, timedelta
import logging

from airflow.decorators import task
from airflow.utils.dates import days_ago

# Import the TemplateDAGBuilder
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'plugins'))
from template_dag_builder import TemplateDAGBuilder


# Define the extract function
def extract_data(**kwargs):
    """Extract data from a source."""
    logging.info("Extracting data from source")
    # In a real scenario, this would extract data from S3 or another source
    return {"extracted_data": "sample_data"}


# Define the transform function
def transform_data(**kwargs):
    """Transform the extracted data."""
    ti = kwargs['ti']
    extracted_data = ti.xcom_pull(task_ids='extract.extract_data')
    logging.info(f"Transforming data: {extracted_data}")
    # In a real scenario, this would transform the data
    return {"transformed_data": "transformed_sample_data"}


# Define the load function
def load_data(**kwargs):
    """Load the transformed data to a destination."""
    ti = kwargs['ti']
    transformed_data = ti.xcom_pull(task_ids='transform.transform_data')
    logging.info(f"Loading data: {transformed_data}")
    # In a real scenario, this would load data to PostgreSQL or S3
    return {"loaded_data": "loaded_sample_data"}


# Create the DAG using the TemplateDAGBuilder
dag_builder = TemplateDAGBuilder(
    dag_id="sample_etl_dag",
    description="A sample ETL DAG using the TemplateDAGBuilder",
    schedule_interval="@daily",
    start_date=days_ago(1),
    catchup=False,
    tags=["sample", "etl", "template"],
)

# Create an ETL pattern
dag_builder.create_extract_load_transform_pattern(
    extract_callable=extract_data,
    transform_callable=transform_data,
    load_callable=load_data,
)

# Build the DAG
dag = dag_builder.build()


# Define a parallel processing DAG
def process_chunk_1(**kwargs):
    """Process the first chunk of data."""
    logging.info("Processing chunk 1")
    return {"processed_chunk_1": "processed_data_1"}


def process_chunk_2(**kwargs):
    """Process the second chunk of data."""
    logging.info("Processing chunk 2")
    return {"processed_chunk_2": "processed_data_2"}


def process_chunk_3(**kwargs):
    """Process the third chunk of data."""
    logging.info("Processing chunk 3")
    return {"processed_chunk_3": "processed_data_3"}


# Create the parallel processing DAG
parallel_dag_builder = TemplateDAGBuilder(
    dag_id="sample_parallel_dag",
    description="A sample parallel processing DAG using the TemplateDAGBuilder",
    schedule_interval="@daily",
    start_date=days_ago(1),
    catchup=False,
    tags=["sample", "parallel", "template"],
)

# Create a parallel processing pattern
parallel_dag_builder.create_parallel_processing_pattern(
    process_callables=[
        process_chunk_1,
        process_chunk_2,
        process_chunk_3,
    ],
    process_task_ids=[
        "process_chunk_1",
        "process_chunk_2",
        "process_chunk_3",
    ],
)

# Build the parallel processing DAG
parallel_dag = parallel_dag_builder.build() 