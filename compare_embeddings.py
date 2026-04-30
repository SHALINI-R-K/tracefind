import boto3
import math
from decimal import Decimal

ddb = boto3.resource("dynamodb", region_name="ap-south-1")
table = ddb.Table("tracefind-items")

def get_item(item_id):
    resp = table.get_item(Key={"id": item_id})
    return resp.get("Item")

item_a = get_item("be863272-8fbd-4cdb-b340-4c08ac166662") # Found green milton
item_b = get_item("1f43a8d8-a385-4c0e-9cb5-9bb62f9ea7c5") # Lost green milton

if not item_a or not item_b:
    print("One or both items not found")
    exit()

print(f"Item A: {item_a['description']} ({item_a['type']})")
print(f"Item B: {item_b['description']} ({item_b['type']})")

emb_a = [float(x) for x in item_a.get("embedding", [])]
emb_b = [float(x) for x in item_b.get("embedding", [])]

print(f"Lengths: {len(emb_a)}, {len(emb_b)}")

if len(emb_a) > 0 and len(emb_b) > 0:
    dot = sum(x*y for x,y in zip(emb_a, emb_b))
    na = math.sqrt(sum(x*x for x in emb_a))
    nb = math.sqrt(sum(x*x for x in emb_b))
    cosine = dot / (na * nb) if na > 0 and nb > 0 else 0
    print(f"Cosine Similarity: {cosine:.4f}")
else:
    print("Embeddings are empty")
