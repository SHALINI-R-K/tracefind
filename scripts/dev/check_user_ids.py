import boto3
from decimal import Decimal

ddb = boto3.resource("dynamodb", region_name="ap-south-1")
table = ddb.Table("tracefind-items")

resp = table.scan()
items = resp.get("Items", [])

for item in items:
    print(f"ID: {item['id']}, Type: {item['type']}, UserID: {item['user_id']}")
