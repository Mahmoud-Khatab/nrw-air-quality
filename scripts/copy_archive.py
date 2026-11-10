"""
Copy OpenAQ archive data from the public S3 open-data bucket into my own
S3 bucket. Each file is streamed straight through memory, so nothing is
ever written to my local disk (my laptop storage stays free no matter how
much data I move).

The public source bucket lets anyone read it anonymously but refuses
signed requests, so I read it with an unsigned client and write to my own
bucket with my normal credentials.

Usage:  python copy_archive.py <ids_file.txt>
        where the ids file has one OpenAQ location id per line.
"""
import sys
import boto3
from botocore import UNSIGNED
from botocore.config import Config

SRC_BUCKET = "openaq-data-archive"                 # public OpenAQ archive (us-east-1)
DST_BUCKET = "mahmoud-khatab-openaq-data-2026"     # my own bucket

ids_file = sys.argv[1] if len(sys.argv) > 1 else "eg_ids.txt"

# unsigned client for the public source, normal client for my destination
src = boto3.client("s3", region_name="us-east-1", config=Config(signature_version=UNSIGNED))
dst = boto3.client("s3")

with open(ids_file) as f:
    ids = [line.strip() for line in f if line.strip()]

paginator = src.get_paginator("list_objects_v2")
total = 0
for loc in ids:
    prefix = f"records/csv.gz/locationid={loc}/"
    count = 0
    for page in paginator.paginate(Bucket=SRC_BUCKET, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            # read one file into memory, write it straight out, then move on
            body = src.get_object(Bucket=SRC_BUCKET, Key=key)["Body"].read()
            dst_key = "raw-archive/" + key.split("records/csv.gz/")[1]
            dst.put_object(Bucket=DST_BUCKET, Key=dst_key, Body=body)
            count += 1
            total += 1
    print(f"location {loc}: copied {count} files (running total {total})")

print(f"Done — copied {total} files from the archive into my bucket.")
