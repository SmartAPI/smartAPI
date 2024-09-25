import boto3
import os
import requests

from datetime import datetime


# Create the expected file name
today_date = datetime.today().strftime("%Y%m%d")
expected_file = f"{os.getenv('S3_FOLDER')}smartapi_{today_date}.zip"

# Create the S3 client
s3_client = boto3.client("s3", region_name=os.getenv("AWS_REGION"))

# Try to fetch the file metadata
try:
    s3_client.head_object(Bucket=os.getenv("BACKUP_BUCKET_NAME"), Key=expected_file)
    print(f"Backup file {expected_file} exists, no action needed")
except s3_client.exceptions.ClientError:
    print(f"Backup file {expected_file} does NOT exist.")

    # Create the payload for Slack
    slack_data = {
        "channel": os.getenv("SLACK_CHANNEL"),
        "username": "SmartAPI",
        "icon_emoji": ":thumbsdown:",
        "text": f":alert: The backup file {expected_file} was NOT created today!",
    }

    try:
        response = requests.post(os.getenv("SLACK_WEBHOOK_URL"), json=slack_data, timeout=10)
        if response.status_code == 200:
            print(" └─ Slack notification sent successfully.")
        else:
            print(f" └─ Failed to send message to Slack: {response.status_code}, {response.text}")
    except requests.exceptions.Timeout:
        print(" └─ Request timed out to Slack WebHook URL.")
    except requests.exceptions.RequestException as e:
        print(f" └─ Failed to send Slack notification. Error: {str(e)}")
