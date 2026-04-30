import boto3

ddb = boto3.resource("dynamodb", region_name="ap-south-1")
table = ddb.Table("tracefind-matches")

print("Clearing tracefind-matches table...")
resp = table.scan()
items = resp.get("Items", [])

with table.batch_writer() as batch:
    for item in items:
        batch.delete_item(Key={"id": item["id"]})

print(f"Deleted {len(items)} matches.")
