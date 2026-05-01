import os
import sys

# Set env vars
os.environ["ITEMS_TABLE"] = "tracefind-items"
os.environ["MATCHES_TABLE"] = "tracefind-matches"
os.environ["AWS_REGION"] = "ap-south-1"

sys.path.append("backend/src")

from contexts.matching.interfaces.events.on_item_reported import _command
from shared.infrastructure.aws.boto3_clients import dynamodb_resource

ddb = dynamodb_resource()
table = ddb.Table("tracefind-items")

print("Fetching active items...")
resp = table.scan()
items = resp.get("Items", [])

active_items = [i for i in items if i.get("status") == "active"]
print(f"Found {len(active_items)} active items.")

for item in active_items:
    item_id = item["id"]
    print(f"Triggering matching for item {item_id} ({item['type']})...")
    try:
        matches = _command.execute(item_id)
        print(f"  Found {len(matches)} matches.")
    except Exception as e:
        print(f"  Error: {e}")

print("Done.")
