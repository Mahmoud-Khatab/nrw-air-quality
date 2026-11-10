"""
Narrow the German OpenAQ locations down to North Rhine-Westphalia.
The catalogue has no "state" field, so I just keep the stations whose
coordinates fall inside a rough box around NRW. It's approximate (a
rectangle, not the real border), which is fine for this project.
Writes nrw_ids.txt, one location id per line.
"""
import json

# rough box around NRW (south/north latitude, west/east longitude)
LAT_MIN, LAT_MAX = 50.3, 52.6
LON_MIN, LON_MAX = 5.8, 9.5

with open("locations.json") as f:
    locations = json.load(f)

ids = []
for l in locations:
    if l.get("country", {}).get("code") != "DE":
        continue
    if l.get("datetimeLast") is None:
        continue
    c = l.get("coordinates") or {}
    lat, lon = c.get("latitude"), c.get("longitude")
    if lat is None or lon is None:
        continue
    if LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX:
        ids.append(str(l["id"]))

with open("nrw_ids.txt", "w") as out:
    out.write("\n".join(ids))

print(f"NRW (approx by bounding box): {len(ids)} locations -> nrw_ids.txt")
