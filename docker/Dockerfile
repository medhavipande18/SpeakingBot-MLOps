# Use official Airflow image as base
FROM apache/airflow:latest

# Set the working directory inside the container
WORKDIR /opt/airflow

# Copy project files into the container
COPY dags/ dags/
COPY scripts/ scripts/
COPY tests/ tests/
COPY requirements.txt requirements.txt
COPY config/ config/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables for Airflow
ENV AIRFLOW_HOME=/opt/airflow

# Initialize Airflow database
RUN airflow db init

# Start Airflow webserver and scheduler
CMD airflow scheduler & airflow webserver -p 8080