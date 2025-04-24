FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/mlops-speakingchatbot.json

CMD ["python", "detect_drift.py"]