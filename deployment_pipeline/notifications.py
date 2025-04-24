import requests
from config import SLACK_WEBHOOK_URL

def send_slack_alert(message: str):
    if not SLACK_WEBHOOK_URL:
        print("⚠SLACK_WEBHOOK_URL not set. Skipping alert.")
        return

    payload = {"text": f":warning: *Data Drift Alert* :warning:\n{message}"}
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        if response.status_code == 200:
            print("Slack alert sent")
        else:
            print(f"Failed to send Slack alert: {response.status_code} | {response.text}")
    except Exception as e:
        print(f"Exception while sending Slack alert: {e}")
