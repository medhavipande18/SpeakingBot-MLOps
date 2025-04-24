FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/mlops-speakingchatbot.json

CMD ["python", "detect_drift.py"]
