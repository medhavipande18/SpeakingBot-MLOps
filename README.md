https://github.com/Shardul-Khandekar/speaking-chatbot.git

python -m venv chatbot
chatbot\Scripts\activate
pip install -r requirements.txt

Prerequisite - Docker installed

Run the below commands in the project root directory
docker-compose build
docker-compose up -d
Visit - http://localhost:8080/

### Admin Accecss
docker exec -it airflow_container airflow users create --username admin --password admin123 --firstname Admin --lastname User --role Admin --email admin@example.com

Login with the username - admin and passowrd - admin123

docker exec -it airflow_container airflow scheduler

<p>Check status of the pipeline in the airflow UI at localhost:8080</p>