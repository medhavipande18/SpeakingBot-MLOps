import logging
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import subprocess

# Ensure logs directory exists
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logs_dir = os.path.join(root_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)
log_file_path = os.path.join(logs_dir, "pipeline.log")

# Configure logging
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Define script paths
data_acquisition_script = os.path.join(root_dir, "scripts", "data_acquisition.py")
data_preprocessing_script = os.path.join(root_dir, "scripts", "data_preprocessing.py")
upload_to_gcs_script = os.path.join(root_dir, "scripts", "upload_to_gcs.py")
dvc_pipeline_script = os.path.join(root_dir, "scripts", "dvc_pipeline.py")
test_folder = os.path.join(root_dir, "tests")


# Default arguments for Airflow tasks
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime.today() - timedelta(days=1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


dag = DAG(
    dag_id="data_pipeline",
    default_args=default_args,
    description="An Airflow DAG to orchestrate data acquisition, transformation, upload, testing, and DVC tracking",
    schedule_interval="0 * * * *",
    catchup=False,
)


def run_script(script_path):
    """Executes a Python script as a subprocess and logs its execution."""
    try:
        logging.info(f"Executing script: {script_path}")
        subprocess.run(["python", script_path], check=True)
        logging.info(f"Successfully executed: {script_path}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing {script_path}: {e}")


def run_tests():
    """Runs Pytest on the test folder and logs results."""
    try:
        logging.info("Running tests...")
        subprocess.run(["pytest", test_folder], check=True)
        logging.info("Tests completed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Tests failed: {e}")


# Define tasks
download_data = PythonOperator(
    task_id="download_data",
    python_callable=run_script,
    op_kwargs={"script_path": data_acquisition_script},
    dag=dag,
)


preprocess_data = PythonOperator(
    task_id="clean_data",
    python_callable=run_script,
    op_kwargs={"script_path": data_preprocessing_script},
    dag=dag,
)


run_tests_task = PythonOperator(
    task_id="run_tests",
    python_callable=run_tests,
    dag=dag,
)


upload_data = PythonOperator(
    task_id="upload_to_gcs",
    python_callable=run_script,
    op_kwargs={"script_path": upload_to_gcs_script},
    dag=dag,
)


dvc_pipeline = PythonOperator(
    task_id="run_dvc_pipeline",
    python_callable=run_script,
    op_kwargs={"script_path": dvc_pipeline_script},
    dag=dag,
)


# Define task dependencies
download_data >> preprocess_data >> upload_data

logging.info("Airflow DAG setup complete.")