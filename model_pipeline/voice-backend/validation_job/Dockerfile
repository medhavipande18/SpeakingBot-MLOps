FROM python:3.10

WORKDIR /app

COPY model_validation.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "model_validation.py"]