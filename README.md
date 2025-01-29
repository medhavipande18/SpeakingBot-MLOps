# SpeakingBot-MLOps
e-Commerce RAG-Based Shopping Assistant / Speaking Chatbot 

This project focuses on developing an AI-powered eCommerce chatbot with speech-to-text and text-to-speech capabilities, making online shopping accessible for visually impaired users. The chatbot utilizes a Retrieval-Augmented Generation (RAG) approach, combining product metadata and customer reviews to generate informative responses.

The system is designed to be scalable, efficient, and cloud-deployable, leveraging Airflow for workflow automation, MLflow for model tracking, Docker & Kubernetes for deployment, and Google Cloud Platform (GCP) for hosting. The chatbot retrieves product details, processes user queries via voice commands, and delivers responses in an intuitive, interactive manner.

This repository contains the data pipeline, model training scripts, API services, and deployment configurations for the chatbot. Future updates will include real-time monitoring, automated model retraining, and enhanced response generation. 🚀

# Folder Structure Overview
project-root/
├── README.md                 # Comprehensive project documentation, setup guide, and usage instructions
├── data/                     # Directory for dataset storage and management
│   ├── raw/                  # Unprocessed datasets directly obtained from sources
│   └── processed/            # Cleaned and preprocessed datasets ready for model training
├── notebooks/                # Jupyter notebooks for data analysis and experimentation
├── src/                      # Core source code for the chatbot system
│   ├── backend/              # Backend API for handling chatbot interactions
│   │   ├── endpoints/        # API endpoint handlers 
│   │   ├── utils/            # Helper functions and utility scripts
│   ├── embeddings/           # Embedding generation and vectorization scripts
│   │   ├── models/           # Pre-trained models for generating embeddings
│   ├── monitoring/           # Performance monitoring and logging tools
│   ├── training/             # Model training scripts and fine-tuning strategies
├── models/                   # Directory to store trained models and checkpoints
├── tests/                    # Unit tests and integration tests for various components
├── docker/                   # Docker configurations for containerization
├── airflow/                  # Airflow DAGs for task automation
│   ├── dags/                 # DAGs managing data preprocessing, model training, and updates
│   ├── tasks/                # Individual task scripts for ingestion, embedding, and retraining
├── cloud/                    # Cloud deployment and configuration files
│   ├── gcp_config/           # Google Cloud Platform (GCP) configuration files
│   ├── kubernetes/           # Kubernetes configurations for deployment
│   ├── terraform/            # Infrastructure-as-Code (IaC) files for provisioning cloud resources
├── monitoring/               # Logging and monitoring configurations
│   ├── grafana/              # Pre-configured Grafana dashboards for performance tracking
├── ci_cd/                    # CI/CD automation scripts
│   ├── github-actions/       # GitHub Actions workflows for automated testing and deployment
│   ├── jenkins/              # Jenkins pipeline configuration (if applicable)
├── requirements.txt          # List of Python dependencies for the project
├── .gitignore                # Files and directories to be ignored in version control
├── LICENSE                   # License for the project
└── CONTRIBUTING.md           # Guidelines for contributing to the repository

