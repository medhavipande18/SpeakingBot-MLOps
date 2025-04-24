# Speaking Chatbot - MLOps Pipeline

**Live Website**: [https://mlops-speakingchatbot.web.app](https://mlops-speakingchatbot.web.app)  
**Demo Video**: [Watch the demo](https://drive.google.com/file/d/1BUkLdaBQ8eg1vQRrCqXoJ-yqv20NZA8M/view?usp=sharing)

## Overview

This project implements an end-to-end MLOps pipeline for a **speaking chatbot** built to assist **visually impaired users** in navigating software product reviews. It integrates data preprocessing, anomaly and bias detection, vector-based semantic search (RAG), and full-stack deployment using **Airflow**, **FAISS**, **Flask**, **React**, **Docker**, **Firebase**, and **Google Cloud Run**.

---

## Folder Structure

---
## Folder Structure
```.
├── .github
│   └── workflows
│       ├── build_index.yml
│       ├── deploy_pipeline.yml
│       ├── model_pipeline.yml
│       └── monitoring_pipeline.yml
│
├── data_pipeline
│   ├── .dvc
│   ├── chatbot
│   ├── dags
│   ├── docker
│   ├── logs
│   ├── scripts
│   └── tests
│
├── deployment_pipeline
│   ├── .dockerignore
│   ├── .firebaserc
│   ├── Dockerfile
│   ├── config.py
│   ├── detect_drift.py
│   ├── firebase.json
│   ├── list_gcs_files.py
│   ├── notifications.py
│   └── requirements.txt
│
├── model_pipeline
│   ├── public
│   ├── src
│   │   ├── assets
│   │   │   ├── App.css
│   │   │   ├── App.jsx
│   │   │   ├── index.css
│   │   │   └── main.jsx
│   │
│   ├── voice-backend
│   │   ├── tests
│   │   │   └── test_app.py
│   │   ├── Procfile
│   │   ├── app.py
│   │   ├── app.yaml
│   │   ├── bias_detection.py
│   │   ├── build-faiss-index.py
│   │   ├── faiss_index.index
│   │   ├── gcs_helper.py
│   │   ├── index_metadata.json
│   │   ├── model_validation.py
│   │   ├── rag_helper.py
│   │   └── requirements.txt
│
├── .firebaserc
├── .gitignore
├── README.md
├── eslint.config.js
├── firebase.json
├── index.html
├── package-lock.json
├── package.json
├── vite.config.js
└── README.md
```
---


---

## Replicating the Project on Any Machine

### Step 1: Clone the Repository

```bash
git clone https://github.com/medhavipande18/SpeakingBot-MLOps.git
cd SpeakingBot-MLOps
``` 

### Step 2: Set Up a Virtual Environment
```bash
python -m venv chatbot
# Windows
chatbot\Scripts\activate
# macOS/Linux
source chatbot/bin/activate
pip install -r requirements.txt
```

### Step 3: Set Up Docker and Airflow (Data Pipeline)
Ensure Docker is installed. Then run:
```bash
docker-compose build
docker-compose up -d
```
Access Airflow at: http://localhost:8080

Initialize Airflow:
```bash
docker exec -it airflow_container airflow users create --username admin \
  --password admin123 --firstname Admin --lastname User --role Admin \
  --email admin@example.com
docker exec -it airflow_container airflow scheduler
```

### Step 4: Build FAISS Index
```bash
cd model_pipeline/voice-backend
python build-faiss-index.py
```
Ensure meta_software.json is available GCS.

### Step 5: Run Model Validation and Bias Detection
```bash
python model_validation.py
python bias_detection.py
```

### Step 6: Run Backend Locally
```bash
cd model_pipeline/voice-backend
flask run
```
### Step 7: Run Frontend Locally
```bash
cd model_pipeline/src
npm install
npm run dev
```
Visit http://localhost:5173

Step 8: Cloud Deployment (CI/CD)
Ensure:
Firebase project is set up and linked
GitHub secrets: GCP_PROJECT_ID, GCP_CREDENTIALS, SERVICE_NAME, REGION

Push to main → triggers deploy_pipeline.yml to deploy both frontend and backend
Use build_index.yml manually if needed
Use model_pipeline.yml for automatic backend + frontend deployment

---
### Replicating the Data Pipeline on Another Machine
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
## 1. Data Pipeline Summary
- **Automated Data Acquisition**: Fetches data from Amazon Review datasets.<br>
- **Data Preprocessing**: Cleans and transforms raw data into structured formats.<br>
- **Anomaly Detection & Alerts**: Identifies missing values, outliers, and invalid formats with Slack notifications.<br>
- **Bias Detection**: Uses **Fairlearn** to analyze and mitigate bias across demographic subgroups.<br>
- **Logging & Tracking**: Tracks pipeline execution and errors using Python logging.<br>
- **Pipeline Orchestration**: Uses **Airflow DAGs** for automation.<br>
- **Data Version Control (DVC)**: Implements **DVC** to track dataset versions and ensure reproducibility.<br>
- **Dockerized Setup**: Fully containerized with **Docker & Docker Compose**.<br>

## 1. Data Pipeline Components

**1. Data Acquisition**
- **download_data.py**: Fetches Amazon review datasets and metadata.
- Extracts and saves files locally.

**2. Data Preprocessing**
- **clean_data.py**: Cleans data, removes missing values, and formats columns.
- Generates new features (e.g., **price_category, review_sentiment**).

**3. Anomaly Detection & Alerts**
- Detects missing values and outliers.
- Sends Slack notifications for detected anomalies.

**4. Bias Detection & Mitigation**
- Uses **Fairlearn** to analyze bias across groups (e.g., **reviewer gender, location**).
- If bias is found, alerts are logged and sent via Slack.

**5. Orchestration with Airflow**
- Uses **Airflow DAGs** to automate data processing.
- Ensures logging and monitoring for pipeline tasks.

**6. Data Version Control (DVC)**
- **dvc_pipeline.py** in the **scripts/** folder ensures **dataset versioning**.
- Tracks data lineage and ensures reproducibility.
- Works seamlessly with the pipeline to fetch and store dataset versions.

**7. Schema & Statistics Generation**
- **generate_schema.py**: Automates schema and statistics generation.
- Uses **DAG-based approach** to ensure schema validation over time.

**8. Automated Testing in Docker**
- **run_tests.py** executes automated tests within the **Dockerized pipeline**.
- Tests are executed as part of the **Airflow DAG**.
- Logs and results can be monitored in the **Airflow UI** or through **Docker logs**.

**9. Pipeline Flow Optimization**
- Uses **Airflow’s Gantt chart** to identify bottlenecks in execution.
- **Observation:** The `download_data` task was the longest-running step.
- **Optimization:** Modified `download_data.py` to **download reviews and metadata in parallel**, reducing runtime.
---

## 2. Model Pipeline Summary
- **Data Loading**: Loads software product review and metadata processed by the data pipeline. Supports integration with DVC-managed versions.<br>
- **FAISS Indexing**: Converts cleaned metadata into embeddings using SentenceTransformers and builds a FAISS index for semantic similarity search.<br>
- **RAG Architecture**: 8Implements Retrieval-Augmented Generation where the top-k matched chunks from FAISS are used as context for query response.<br>
- **Model Validation**: Validates RAG responses via semantic similarity against expected answers and monitors accuracy over time.<br>
- **Bias Detection**: Applies slice-based evaluation using Fairlearn, checking semantic bias across dimensions like rating or category.<br>
- **CI/CD Automation**: Uses GitHub Actions to trigger model indexing, validation, and deployment workflows.<br>
- **Dockerized Backend**: Flask backend containerized for reproducibility and Cloud Run deployment.<br>


## Model Pipeline Components

**1. Data Loading and Preprocessing**: 
Loads review and metadata from the data pipeline’s cleaned output. Converts product metadata into embeddings using SentenceTransformers. Uses .jsonl format for processed metadata.

**2. FAISS Index Generation**: 
build-faiss-index.py encodes metadata to vectors. Builds and saves FAISS index locally or pushes to GCS. Index is used for fast top-k retrieval.

**3. RAG Query System**: 
Retrieves context using FAISS before responding. Generates natural language answers using LLMs like OpenAI GPT/Gemini. Contextual memory enables follow-up question handling.

**4. Model Validation**: 
model_validation.py compares RAG responses with ground-truth answers. Uses cosine similarity and semantic scoring to evaluate quality. Logs validation results for every run.

**5. Bias Detection**: 
bias_detection.py performs slicing analysis using Fairlearn. Evaluates fairness across product categories, review length, etc. Slack alerts are triggered if significant disparity is found.

**6. CI/CD Integration**:
- model_pipeline.yml automates:
  > Index rebuilding
  > Backend deployment to Cloud Run
  > Frontend deployment to Firebase
- build_index.yml supports manual reindexing.

**7. Experiment Tracking & Reporting**: Intermediate outputs like FAISS index and validation scores are stored in versioned paths. Future extension includes MLflow or WandB for full experiment logs.

**8. Dockerized Setup**: Backend fully containerized with Flask + FAISS logic. Supports testing, local execution, and cloud deployment.
---

## 3. Deployment Pipeline Summary
- **Cloud Deployment:** Backend deployed to Google Cloud Run, frontend to Firebase Hosting.<br>
- **CI/CD Pipeline:** Uses GitHub Actions to trigger deployment automatically on main branch changes.<br>
- **Artifact Management:** FAISS index stored in GCS, model versioning built into pipeline stages.<br>
- **Monitoring Setup:** Integration with Cloud Logging to monitor backend and model outputs.<br>
- **Drift Detection:** Uses Evidently AI to detect input feature distribution shifts and trigger retraining if thresholds are exceeded.<br>
- **Slack Alerts:** Sends failure or validation alerts on drift or deployment status.<br>
- **Reproducible Environment:** Docker-based scripts and .yml files allow replication on any GCP account with linked Firebase.<br>


## Deployment Pipeline Components

### **1. Backend Deployment**
Flask backend deployed via Cloud Run using Docker.
Triggered from model_pipeline.yml or deploy_pipeline.yml.
Authenticated using GCP service account stored in GitHub secrets.

### **2. Frontend Hosting**
React app deployed to Firebase Hosting.
Auto-triggered on commit or on backend deployment success.

### **3. CI/CD Automation**
deploy_pipeline.yml handles:
- Backend build and deploy to Cloud Run
- Frontend deploy to Firebase
- Includes rollback on failure via GCP console controls.

### **4. Monitoring & Drift Detection**
Uses Evidently AI to compare recent inputs vs. training distributions.
Triggers retraining script if cosine distance > threshold.
Notifies Slack channel on drift detection or validation failures.

### **5. Deployment Scripts**
Dockerfile for backend
.firebaserc and firebase.json for frontend
Configurable .env for sensitive keys and project values

### **6. Rollback & Notifications**
Deployment logs visible in Cloud Run Console and GitHub Actions.
Rollback possible from Cloud Run UI if newer build fails.
Slack notifications include:
Drift alerts, Deployment failures, Successful redeploys
---

