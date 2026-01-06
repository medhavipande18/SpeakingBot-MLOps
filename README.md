# Speaking Chatbot — End-to-End MLOps System

**Live Application:** https://mlops-speakingchatbot.web.app  
**Demo Video:** https://drive.google.com/file/d/1BUkLdaBQ8eg1vQRrCqXoJ-yqv20NZA8M/view  

---

## Project Overview

This project implements a **production-style MLOps pipeline** for a **voice-enabled chatbot** designed to help **visually impaired users** explore and understand software product reviews.

The system is built as a **three-phase MLOps architecture**:

1. **Data Pipeline** — ingestion, validation, bias checks, and versioning  
2. **Model Pipeline** — RAG indexing, validation, bias evaluation, and rollback  
3. **Deployment & Monitoring Pipeline** — CI/CD, drift detection, and alerts  

The goal of this project is **reproducibility, reliability, and operational correctness**, not just model inference.

---

## High-Level Architecture

Raw Reviews
↓
[ Data Pipeline ]
↓ (Versioned & Validated Data)
[ Model / RAG Pipeline ]
↓ (Validated FAISS Index)
[ Deployment Pipeline ]
↓
End Users (Voice + Web)

---

## Repository Structure
├── .github/workflows # CI/CD pipelines
├── data_pipeline # Airflow-based data pipeline
├── model_pipeline # RAG + FAISS model pipeline
├── deployment_pipeline # Cloud Run + Firebase deployment
├── frontend # React voice-enabled UI
├── docker-compose.yml # Local orchestration
├── README.md

---

# Phase 1 — Data Pipeline (Airflow + DVC)

## Objective
Create a **reproducible, validated, bias-aware dataset** that can safely feed downstream ML and RAG systems.

## Key Capabilities
- Automated data acquisition
- Data cleaning and feature engineering
- Schema validation and statistics generation
- Anomaly detection with alerts
- Bias detection using data slicing
- Dataset versioning with DVC
- Fully orchestrated via Airflow DAGs

## Pipeline Stages

### 1. Data Acquisition
- Downloads raw software review and metadata datasets
- External dependencies explicitly versioned

### 2. Data Preprocessing
- Cleans missing values and invalid records
- Generates derived features (e.g., sentiment, price category)
- Produces structured `.jsonl` outputs

### 3. Schema & Statistics Generation
- Automatically generates schema and summary statistics
- Validates schema consistency across runs

### 4. Anomaly Detection
- Detects missing values, outliers, and invalid formats
- Sends Slack alerts on violations

### 5. Bias Detection (Data-Level)
- Uses Fairlearn to slice data across attributes
- Logs and alerts on distribution imbalance

### 6. Data Versioning
- Uses DVC to track dataset versions
- Ensures reproducibility across machines

### 7. Testing & Logging
- Unit tests for preprocessing logic
- Centralized logging via Python and Airflow logs

---

# Phase 2 — Model Pipeline (RAG + FAISS)

## Objective
Build a **validated Retrieval-Augmented Generation system** with safety checks before deployment.

## Key Capabilities
- Embedding generation and FAISS indexing
- RAG-based question answering
- Model validation and regression checks
- Bias detection on model outputs
- Automated rollback on degradation
- CI/CD-driven execution

## Pipeline Stages

### 1. Data Loading
- Loads versioned, validated outputs from the data pipeline
- Ensures schema compatibility

### 2. Embedding & FAISS Indexing
- Uses SentenceTransformers to embed product metadata
- Builds and persists FAISS index
- Index artifacts stored in Google Cloud Storage

### 3. RAG Query System
- Retrieves top-k relevant chunks via FAISS
- Injects retrieved context into LLM prompts
- Supports conversational follow-ups

### 4. Model Validation
- Compares generated answers against reference answers
- Uses semantic similarity scoring
- Fails pipeline if quality drops below threshold

### 5. Bias Detection (Model-Level)
- Slice-based evaluation across product attributes
- Alerts on disproportionate performance

### 6. Rollback Mechanism
- Automatically restores previous FAISS index
- Prevents degraded models from reaching production

### 7. CI/CD Automation
- GitHub Actions trigger index rebuilds, validation checks, and deployment steps

---

# Phase 3 — Deployment & Monitoring

## Objective
Deploy the system with **automated CI/CD, monitoring, and drift detection**.

## Deployment Stack
- **Backend:** Flask + FAISS on Google Cloud Run
- **Frontend:** React + Voice UI on Firebase Hosting
- **Artifacts:** FAISS index stored in Google Cloud Storage

## Pipeline Stages

### 1. Backend Deployment
- Dockerized Flask application
- Deployed via GitHub Actions to Cloud Run

### 2. Frontend Deployment
- React app deployed to Firebase Hosting
- Automatically triggered after backend success

### 3. Monitoring & Logging
- Cloud Logging for runtime metrics
- GitHub Actions logs for CI/CD visibility

### 4. Drift Detection
- Uses Evidently AI to monitor input distribution shifts
- Triggers alerts when drift exceeds threshold

### 5. Notifications
- Slack alerts for drift detection, validation failures, and deployment status

---

# Running the Project Locally

## Prerequisites
- Python 3.9+
- Docker & Docker Compose
- Node.js
- Google Cloud account (for deployment)

## Setup

```bash
git clone https://github.com/medhavipande18/SpeakingBot-MLOps.git
cd SpeakingBot-MLOps
docker-compose build
docker-compose up -d
```

Access Airflow at http://localhost:8080

Default credentials:
Username: admin
Password: admin123

Build FAISS Index:
```
cd model_pipeline/voice-backend
python build-faiss-index.py
```

Run Backend
```
flask run
```

Run Frontend
```
cd model_pipeline/src
npm install
npm run dev
```

## Why This Project Matters
This project demonstrates:
- End-to-end MLOps design
- Separation of data, model, and deployment concerns
- CI/CD, monitoring, and rollback mechanisms
- Responsible ML practices with bias detection
- Cloud-native, production-oriented architecture

## Future Improvements:
- MLflow or Weights & Biases for experiment tracking
- Canary deployments for FAISS index updates
- Evaluation dashboards and metrics visualization
- Cost-aware retraining triggers
