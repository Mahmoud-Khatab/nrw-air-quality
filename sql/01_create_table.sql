-- NRW air quality (OpenAQ) — Athena table definition
-- Runs on Amazon Athena over the gzipped CSV files I copied into S3.
-- Mahmoud Khatab

CREATE DATABASE openaq_db;

-- External table over my OpenAQ archive files in S3.
-- I use OpenCSVSerde here because the source files are inconsistently
-- quoted: some rows wrap fields in double quotes, some don't. With a
-- plain reader, "pm10" and pm10 came out as two different pollutants.
-- OpenCSVSerde strips the quotes so the values are clean. The catch is
-- it reads every column as text, so I CAST the numbers in the queries.
CREATE EXTERNAL TABLE openaq_db.measurements (
  location_id STRING,
  sensors_id STRING,
  location STRING,
  datetime STRING,
  lat STRING,
  lon STRING,
  parameter STRING,
  units STRING,
  value STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  'separatorChar' = ',',
  'quoteChar' = '"',
  'escapeChar' = '\\'
)
STORED AS TEXTFILE
LOCATION 's3://mahmoud-khatab-openaq-data-2026/raw-archive/'
TBLPROPERTIES ('skip.header.line.count'='1');
