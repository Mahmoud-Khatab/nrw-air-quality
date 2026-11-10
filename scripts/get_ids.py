"""
Pull the OpenAQ location IDs for the countries I want out of
locations.json (the catalogue I fetched from the OpenAQ API).
Keeps only stations that actually have recent data, and writes
one id per line to <code>_ids.txt.
"""
import json

with open("locations.json") as f:
    locations = json.load(f)

for code in ["DE", "EG"]:
    ids = [str(l["id"]) for l in locations
           if l.get("country", {}).get("code") == code
           and l.get("datetimeLast") is not None]
    with open(f"{code.lower()}_ids.txt", "w") as out:
        out.write("\n".join(ids))
    print(f"{code}: wrote {len(ids)} ids to {code.lower()}_ids.txt")
