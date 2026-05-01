import os
import boto3
from decimal import Decimal

# Set env vars to match the scan results
os.environ["ITEMS_TABLE"] = "tracefind-items"
os.environ["MATCHES_TABLE"] = "tracefind-matches"
os.environ["NOTIFICATIONS_TABLE"] = "tracefind-notifications"
os.environ["SES_FROM_EMAIL"] = "no-reply@tracefind.local"
os.environ["COGNITO_USER_POOL_ID"] = "ap-south-1_vElJTbFVT"
os.environ["AWS_REGION"] = "ap-south-1"

from contexts.notification.interfaces.events.on_match_found import lambda_handler

# Mock a real match event from the scan
event = {
    "Records": [{
        "eventName": "INSERT",
        "dynamodb": {
            "NewImage": {
                "id": {"S": "dab12be6-df20-4fa9-93f2-ba8b7cd3265b"},
                "score": {"N": "0.927658"},
                "lost_item_id": {"S": "d7302590-9c12-43a2-a2ff-8c23c399b5d4"},
                "found_item_id": {"S": "1685c3db-951d-494d-a0e0-c9c8dd3e77da"}
            }
        }
    }]
}

print("Running lambda_handler...")
try:
    result = lambda_handler(event, None)
    print(f"Result: {result}")
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
