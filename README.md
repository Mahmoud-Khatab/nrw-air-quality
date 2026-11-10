# NRW Air Quality — A Serverless Data Pipeline on AWS

Ingesting, cleaning and analysing **2.5 million air-quality readings** from monitoring
stations across **North Rhine-Westphalia (NRW), Germany**, using **Amazon S3 + Athena**,
and visualising the results in an interactive **Tableau** dashboard.

**Author:** Mahmoud Khatab · [ORCID 0009-0003-6416-1006](https://orcid.org/0009-0003-6416-1006)

📊 **Live dashboard:** https://public.tableau.com/app/profile/mahmoud.khatab/viz/NRW_AirQuality/Dashboard1

---

## Overview

In this project I built an end-to-end, **serverless** data pipeline on Amazon Web Services for
open air-quality data. I ingested raw measurements from the public **OpenAQ** open-data archive
into **Amazon S3**, queried them in place with **Amazon Athena (SQL)**, summarised them, and
visualised the results in an interactive **Tableau** dashboard. The scope is deliberately a
data-engineering and analytics demonstration — building a reproducible pipeline and descriptive
analysis.

## Architecture

```
OpenAQ public S3 archive (us-east-1, gzipped CSV)
        │   Python + boto3 — anonymous (unsigned) read,
        │   credentialed write; streamed through RAM (no local disk)
        ▼
Amazon S3  —  raw-archive/ (my private bucket)
        │   Amazon Athena external table (OpenCSVSerde)
        ▼
SQL aggregation in Athena  →  summary CSV (~8,372 rows)
        ▼
Tableau Public  —  interactive dashboard (trend · map · ranking)
```

## Data source

- **Provider:** [OpenAQ](https://openaq.org) — a non-profit aggregator of global, ground-level
  air-quality data.
- **Access route:** the OpenAQ public open-data archive on AWS (`s3://openaq-data-archive`,
  us-east-1), gzipped CSV, partitioned by location / year / month.
- **Scope:** a sample of **~27 NRW monitoring stations** (filtered from the German set by an
  approximate lat/lon bounding box), yielding **2,535,748 hourly readings** across six pollutants
  (NO₂, PM10, PM2.5, O₃, NO, SO₂).

## Method

1. **Catalogue** — I fetched the OpenAQ location catalogue via the v3 REST API (paginated), then
   filtered it to NRW stations by bounding box (`scripts/get_nrw_ids.py`).
2. **Ingestion** — I copied each station's archive files from the public bucket into my own
   private S3 bucket. Because the public bucket allows anonymous reads but denies signed reads,
   my script uses an *unsigned* client to read and a *credentialed* client to write, streaming
   each file through memory so my laptop storage was not a constraint (`scripts/copy_archive.py`).
3. **Table definition** — I defined an Athena external table over the raw files
   (`sql/01_create_table.sql`).
4. **Cleaning & analysis** — see below (`sql/02_analysis_queries.sql`).
5. **Visualisation** — I exported a compact summary CSV and built the Tableau dashboard.

## Design decision: handling inconsistent quoting

My first table used a plain delimited reader, and it produced duplicated categories — `"pm10"`
and `pm10` were counted as different pollutants — because the archive files are inconsistently
quoted (some rows wrap fields in double quotes, some do not). I fixed this by redefining the
table with the quote-aware **OpenCSVSerde**, which strips quotes uniformly. Since this SerDe
reads every column as text, I convert numeric columns at query time with `TRY_CAST` (which
safely ignores malformed values), and I apply a `value BETWEEN 0 AND 2000` filter to remove
negative readings and implausible spikes.

## Findings

**Readings per pollutant**

| Pollutant | Readings |
|-----------|---------:|
| NO₂       | 751,774 |
| PM10      | 703,999 |
| PM2.5     | 492,703 |
| O₃        | 385,825 |
| NO        | 109,707 |
| SO₂       |  91,740 |

**Average and peak concentration per pollutant (µg/m³)**

| Pollutant | Average | Maximum |
|-----------|--------:|--------:|
| O₃        | 48.67 | 298.71 |
| NO₂       | 19.73 | 209.25 |
| PM10      | 15.62 | 1560.46 |
| PM2.5     |  9.30 | 1083.50 |
| NO        |  7.30 | 643.74 |
| SO₂       |  3.25 | 273.73 |

Ozone shows the highest average, consistent with its regional, photochemical nature; NO₂ reflects
traffic-related emissions. Very high maxima (e.g. PM10 at 1560) are isolated spikes or sensor
artefacts rather than typical levels.

## Repository structure

```
nrw-air-quality/
├── README.md
├── scripts/
│   ├── get_ids.py          # extract OpenAQ location IDs by country from the catalogue
│   ├── get_nrw_ids.py      # filter German stations to NRW by bounding box
│   └── copy_archive.py     # stream station files from the public archive into S3
├── sql/
│   ├── 01_create_table.sql # Athena database + external table (OpenCSVSerde)
│   └── 02_analysis_queries.sql # counts, per-pollutant statistics, summary export
└── docs/
    └── NRW_Air_Quality_Pipeline.pdf  # full write-up
```

## How to reproduce

**Requirements:** an AWS account (S3 + Athena), Python 3 with `boto3`, and the AWS CLI configured
with your credentials.

```bash
pip install boto3

# 1. (one-time) fetch the OpenAQ location catalogue into locations.json via the v3 API,
#    then pick the stations to copy:
python scripts/get_nrw_ids.py        # -> nrw_ids.txt

# 2. copy those stations' data from the public archive into your own S3 bucket
#    (edit DST_BUCKET inside the script to your bucket name first):
python scripts/copy_archive.py nrw_ids.txt

# 3. in the Athena console, run the SQL:
#    - sql/01_create_table.sql   (create database + table)
#    - sql/02_analysis_queries.sql (run each query one at a time)
```

Then export the summary query's result as CSV and load it into Tableau.

## Tools

Amazon S3 · Amazon Athena (Trino SQL) · Python (boto3) · AWS CLI · Tableau Public

---

*Data © OpenAQ contributors, used under the [OpenAQ terms of use](https://docs.openaq.org/about/terms).*
