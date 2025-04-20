# Use an official Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend app code into the container
COPY . .

# Cloud Run expects the app to listen on 0.0.0.0 and port 8080
EXPOSE 8080

# Set environment variable (Flask will read this port)
ENV PORT 8080

# Run the Flask app
CMD ["python", "app.py"]