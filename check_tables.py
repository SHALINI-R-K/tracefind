import boto3
import json
from decimal import Decimal

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

ddb = boto3.resource("dynamodb", region_name="ap-south-1")
table = ddb.Table("tracefind-matches")

print("Checking tracefind-matches table...")
try:
    resp = table.scan()
    matches = resp.get("Items", [])
    print(f"Found {len(matches)} matches.")
    for m in matches:
        print(json.dumps(m, indent=2, default=decimal_default))
except Exception as e:
    print(f"Error: {e}")

table_notifications = ddb.Table("tracefind-notifications")
print("\nChecking tracefind-notifications table...")
try:
    resp = table_notifications.scan()
    notifications = resp.get("Items", [])
    print(f"Found {len(notifications)} notifications.")
    for n in notifications:
        print(json.dumps(n, indent=2, default=decimal_default))
except Exception as e:
    print(f"Error: {e}")
