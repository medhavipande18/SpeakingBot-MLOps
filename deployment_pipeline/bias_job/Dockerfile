FROM python:3.10

WORKDIR /app

COPY bias_detection.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "bias_detection.py"]