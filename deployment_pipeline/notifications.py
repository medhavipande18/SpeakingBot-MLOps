# deployment_pipeline/notifications.py

import requests
from config import SLACK_WEBHOOK_URL

def send_slack_alert(message: str):
    payload = {"text": f":warning: *Data Drift Alert* :warning:\n{message}"}
    try:
        response = requests.post("https://hooks.slack.com/services/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", json=payload)
        if response.status_code == 200:
            print("Slack alert sent")
        else:
            print(f"Failed to send Slack alert: {response.status_code} | {response.text}")
    except Exception as e:
        print(f"Exception while sending Slack alert: {e}")
