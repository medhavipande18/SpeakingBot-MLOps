# ===== Dockerfile for Flask Backend =====
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all backend code into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Expose port for Cloud Run
EXPOSE 8080

# Run the Flask app
CMD ["python", "app.py"]