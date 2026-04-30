import os
import sys
import boto3
from decimal import Decimal

# Set env vars
os.environ["ITEMS_TABLE"] = "tracefind-items"
os.environ["MATCHES_TABLE"] = "tracefind-matches"
os.environ["NOTIFICATIONS_TABLE"] = "tracefind-notifications"
os.environ["SES_FROM_EMAIL"] = "no-reply@tracefind.local"
os.environ["COGNITO_USER_POOL_ID"] = "ap-south-1_vElJTbFVT"
os.environ["AWS_REGION"] = "ap-south-1"

sys.path.append("backend/src")
from contexts.notification.interfaces.events.on_match_found import lambda_handler

ddb = boto3.resource("dynamodb", region_name="ap-south-1")
table = ddb.Table("tracefind-matches")

print("Fetching pending matches...")
resp = table.scan()
items = resp.get("Items", [])
pending = [i for i in items if i.get("status") == "pending"]
print(f"Found {len(pending)} pending matches.")

records = []
for m in pending:
    records.append({
        "eventName": "INSERT",
        "dynamodb": {
            "NewImage": {
                "id": {"S": m["id"]},
                "score": {"N": str(m["score"])},
                "lost_item_id": {"S": m["lost_item_id"]},
                "found_item_id": {"S": m["found_item_id"]}
            }
        }
    })

if records:
    print("Running lambda_handler...")
    event = {"Records": records}
    result = lambda_handler(event, None)
    print(f"Result: {result}")
else:
    print("No pending matches to process.")
