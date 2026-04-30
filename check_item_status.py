import boto3

ddb = boto3.resource("dynamodb", region_name="ap-south-1")
table = ddb.Table("tracefind-items")

resp = table.scan()
items = resp.get("Items", [])

for item in items:
    print(f"ID: {item['id']}, Type: {item['type']}, Status: {item['status']}, Description: {item['description'][:50]}...")
