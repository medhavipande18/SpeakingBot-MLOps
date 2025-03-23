# notifications.py
import json
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")

def send_slack_message(message):
    if not SLACK_WEBHOOK:
        print("Slack webhook not set in .env.")
        return
    payload = {"text": message}
    requests.post(SLACK_WEBHOOK, json=payload)
    print("Slack message sent.")

def notify_from_result(result_path: str):
    if not os.path.exists(result_path):
        print(f"File not found: {result_path}")
        return

    with open(result_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    task = "Bias Check" if "bias_pass" in data else "Model Validation"
    status_key = "bias_pass" if "bias_pass" in data else "validation_pass"
    status = data.get(status_key, False)

    if status:
        send_slack_message(f"{task} passed successfully.")
    else:
        send_slack_message(f"{task} failed. Rollback may be required.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python notifications.py <result_json_path>")
    else:
        notify_from_result(sys.argv[1])
