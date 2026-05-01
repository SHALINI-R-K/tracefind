import boto3

ddb = boto3.resource("dynamodb", region_name="ap-south-1")
table = ddb.Table("tracefind-items")

resp = table.scan()
items = resp.get("Items", [])

for item in items:
    print(f"ID: {item['id'][:8]}, Model: {item.get('embedding_model_version')}, Len: {len(item.get('embedding', []))}, Type: {item['type']}, Desc: {item['description'][:30]}")
