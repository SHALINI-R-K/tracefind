import boto3, json
from decimal import Decimal
import math

ddb = boto3.resource("dynamodb", region_name="ap-south-1")
table = ddb.Table("tracefind-items")

# Get both items with embeddings
resp = table.scan()
items = resp.get("Items", [])

lost = None
found = None
for item in items:
    if item["type"] == "lost":
        lost = item
    elif item["type"] == "found":
        found = item

if not lost or not found:
    print("Need both a lost and found item")
    exit()

print(f"Lost:  {lost['description']}")
print(f"Found: {found['description']}")
print(f"Lost model:  {lost.get('embedding_model_version')}")
print(f"Found model: {found.get('embedding_model_version')}")

emb_lost = lost.get("embedding", [])
emb_found = found.get("embedding", [])
print(f"\nLost embedding length:  {len(emb_lost)}")
print(f"Found embedding length: {len(emb_found)}")

if len(emb_lost) > 0 and len(emb_found) > 0 and len(emb_lost) == len(emb_found):
    a = [float(x) for x in emb_lost]
    b = [float(x) for x in emb_found]
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(x*x for x in b))
    cosine = dot / (na * nb) if na > 0 and nb > 0 else 0
    print(f"\nCosine similarity: {cosine:.4f}")
    print(f"Match threshold:   0.75 (default)")
    print(f"Would match:       {'YES' if cosine >= 0.75 else 'NO'}")
else:
    print(f"\nEmbeddings empty or different lengths - cannot compute similarity")
    if len(emb_lost) > 0:
        print(f"Lost embedding sample: {[float(x) for x in emb_lost[:5]]}")
    if len(emb_found) > 0:
        print(f"Found embedding sample: {[float(x) for x in emb_found[:5]]}")

# Also check GSI1 key format
print(f"\nLost  GSI1 PK: {lost.get('gsi1_pk')}")
print(f"Found GSI1 PK: {found.get('gsi1_pk')}")
