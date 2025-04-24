# Speaking Chatbot - Data Pipeline

Link to the product: https://mlops-speakingchatbot.web.app/
Video of the final deployed product: https://drive.google.com/file/d/1BUkLdaBQ8eg1vQRrCqXoJ-yqv20NZA8M/view?usp=sharing

## Overview
This project implements a robust data pipeline to process, clean, and analyze Amazon reviews for software products. The pipeline is designed for MLOps workflows, ensuring automated data acquisition, preprocessing, tracking, anomaly detection, and bias analysis. The data pipeline is orchestrated using Apache Airflow and supports scalable, reproducible workflows.

---
# Data Pipeline
## Key Features
✅ **Automated Data Acquisition**: Fetches data from Amazon Review datasets.<br>
✅ **Data Preprocessing**: Cleans and transforms raw data into structured formats.<br>
✅ **Anomaly Detection & Alerts**: Identifies missing values, outliers, and invalid formats with Slack notifications.<br>
✅ **Bias Detection**: Uses **Fairlearn** to analyze and mitigate bias across demographic subgroups.<br>
✅ **Logging & Tracking**: Tracks pipeline execution and errors using Python logging.<br>
✅ **Pipeline Orchestration**: Uses **Airflow DAGs** for automation.<br>
✅ **Data Version Control (DVC)**: Implements **DVC** to track dataset versions and ensure reproducibility.<br>
✅ **Dockerized Setup**: Fully containerized with **Docker & Docker Compose**.<br>

---
## Folder Structure
```
├── SpeakingBot-MLOps/
|   ├── config/                
│   ├── dags/                 # Airflow DAGs
|   |   ├── data_pipeline.py  
│   ├── data/                 # Data storage (local or cloud)
│   ├── docker/               
|   |   ├── Dockerfile
│   ├── scripts/              # Data processing scripts
│   │   ├── dvc_pipeline.py   # DVC integration script
│   │   ├── download_data.py  # Data acquisition script
│   │   ├── clean_data.py     # Data cleaning script
│   │   ├── run_tests.py      # Automated testing script
│   │   ├── upload_to_gcs.py  # Upload processed data to Google Cloud Storage
│   │   ├── generate_schema.py # Schema and statistics generation script
│   ├── tests/                # Unit tests
|   |   ├── test_data_acquisition.py
|   |   ├── test_data_preprocessing.py
│   ├── logs/                 # Log files
│   ├── docker-compose.yaml   # Docker setup
│   ├── requirements.txt      # Python dependencies
│   ├── README.md             # Project documentation
```

---
## Replicating the Pipeline on Another Machine
To set up and run the pipeline on a different machine, follow these steps:

### **1. Clone the Repository**
```sh
git clone https://github.com/medhavipande18/SpeakingBot-MLOps.git
cd speaking-chatbot
```

### **2. Set Up Virtual Environment**
```sh
python -m venv chatbot
# Activate on Windows
chatbot\Scripts\activate
# Activate on macOS/Linux
source chatbot/bin/activate
pip install -r requirements.txt
```

### **3. Set Up Docker**
Ensure Docker is installed and running. Then, execute:
```sh
docker-compose build
docker-compose up -d
```
This will set up Airflow and other required services. Once done, visit **[localhost:8080](http://localhost:8080/)** to access Airflow.

### **4. Initialize Airflow**
Run the following commands to create an Airflow admin user and start the scheduler:
```sh
docker exec -it airflow_container airflow users create --username admin \
    --password admin123 --firstname Admin --lastname User --role Admin \
    --email admin@example.com

# Start Airflow scheduler
docker exec -it airflow_container airflow scheduler
```
Login using:
- **Username:** `admin`
- **Password:** `admin123`

### **5. Verify Pipeline Execution**
Monitor logs and execution:
```sh
tail -f logs/pipeline.log
```
Or check the status in the Airflow UI at **[localhost:8080](http://localhost:8080/)**.

---
## Data Pipeline Components

### **1. Data Acquisition**
- **download_data.py**: Fetches Amazon review datasets and metadata.
- Extracts and saves files locally.

### **2. Data Preprocessing**
- **clean_data.py**: Cleans data, removes missing values, and formats columns.
- Generates new features (e.g., **price_category, review_sentiment**).

### **3. Anomaly Detection & Alerts**
- Detects missing values and outliers.
- Sends Slack notifications for detected anomalies.

### **4. Bias Detection & Mitigation**
- Uses **Fairlearn** to analyze bias across groups (e.g., **reviewer gender, location**).
- If bias is found, alerts are logged and sent via Slack.

### **5. Orchestration with Airflow**
- Uses **Airflow DAGs** to automate data processing.
- Ensures logging and monitoring for pipeline tasks.

### **6. Data Version Control (DVC)**
- **dvc_pipeline.py** in the **scripts/** folder ensures **dataset versioning**.
- Tracks data lineage and ensures reproducibility.
- Works seamlessly with the pipeline to fetch and store dataset versions.

### **7. Schema & Statistics Generation**
- **generate_schema.py**: Automates schema and statistics generation.
- Uses **DAG-based approach** to ensure schema validation over time.

### **8. Automated Testing in Docker**
- **run_tests.py** executes automated tests within the **Dockerized pipeline**.
- Tests are executed as part of the **Airflow DAG**.
- Logs and results can be monitored in the **Airflow UI** or through **Docker logs**.

### **9. Pipeline Flow Optimization**
- Uses **Airflow’s Gantt chart** to identify bottlenecks in execution.
- **Observation:** The `download_data` task was the longest-running step.
- **Optimization:** Modified `download_data.py` to **download reviews and metadata in parallel**, reducing runtime.

---
## Evaluation Criteria
1. Proper Documentation
Fulfilled by: README.md
The entire pipeline is well-documented, including setup instructions, workflow descriptions, dependencies, and execution steps. The structured folder organization is also detailed in the README.

2. Modular Syntax and Code
Fulfilled by: Function-wise implementation in all scripts
The pipeline follows a modular coding approach, where each task (data acquisition, preprocessing, bias detection, etc.) is encapsulated into independent functions, ensuring reusability and easy updates.

3. Pipeline Orchestration (Airflow DAGs)
Fulfilled by: data_pipeline DAG in Airflow
The entire pipeline is orchestrated using Airflow DAGs, ensuring a structured task execution flow. Error handling is implemented using try-except blocks to catch failures and log errors efficiently.

4. Tracking and Logging
Fulfilled by: Python logging, Slack alerts
Python’s logging module tracks task execution and errors. Additionally, Slack alerts are triggered whenever an anomaly is detected, ensuring quick notifications for failures.

5. Data Version Control (DVC)
Fulfilled by: dvc_pipeline.py
The processed data is versioned using DVC before being uploaded to Google Cloud Storage (GCS). The pipeline fetches the latest version ID for tracking, and rollback is possible in case of failures.

6. Pipeline Flow Optimization
Fulfilled by: Airflow Gantt Chart analysis, download_data.py
Airflow’s Gantt chart was analyzed to identify bottlenecks. The download_data task was found to be the heaviest, so the process was optimized by parallelizing reviews and metadata downloads.

7. Schema and Statistics Generation
Fulfilled by: generate_schema.py
The pipeline automates schema generation by analyzing review and metadata files. Using DAGs and pandas, it extracts column names, data types, and statistical summaries for validation.

8. Anomalies Detection and Alert Generation
Fulfilled by: Logging mechanism, Slack alerts
The pipeline tracks missing values and outliers in datasets. Whenever an anomaly is detected, an alert is automatically sent to Slack, ensuring real-time notifications.

9. Bias Detection and Mitigation
Fulfilled by: bias_analysis.py, bias_mitigation.py
Bias is analyzed through data slicing, measuring variations in ratings across demographic subgroups. The threshold-based approach ensures meaningful disparities are detected while minimizing false positives.

10. Test Modules
Fulfilled by: test_data_acquisition.py, test_data_preprocessing.py
Unit tests have been implemented to validate data acquisition and preprocessing. These tests help catch issues early and ensure data consistency.

11. Reproducibility
Fulfilled by: README.md, Dockerized pipeline
The README provides clear steps to replicate the pipeline on any machine. The entire setup, including dependencies, is containerized using Docker, making it easy to deploy.

12. Error Handling and Logging
Fulfilled by: Logging mechanisms in all scripts
Comprehensive logging is implemented across all scripts. Errors are logged with sufficient details, ensuring quick debugging and issue resolution.
