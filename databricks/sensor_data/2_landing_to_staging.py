# Databricks notebook source
# MAGIC %md # Import libraries

# COMMAND ----------

import pyspark.sql.functions as F 
from pyspark.sql.types import ArrayType, StructType, StructField, StringType
from delta.tables import *

# COMMAND ----------

# MAGIC %md # Define input and output delta paths

# COMMAND ----------

source_path = f"abfss://datalake@{stgendpoint}.dfs.core.windows.net/landing/sensor_data/"
sink_path = f"abfss://datalake@{stgendpoint}.dfs.core.windows.net/staging/sensor_data/"

# COMMAND ----------

# MAGIC %md # Define schema

# COMMAND ----------

schema = """
{
    "miv": 
    {
        "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance", 
    "@xsi:noNamespaceSchemaLocation": "http://miv.opendata.belfla.be/miv-verkeersdata.xsd", 
    "@schemaVersion": "1.0.0", 
    "tijd_publicatie": "2020-07-26T16:05:00.24+01:00", 
    "tijd_laatste_config_wijziging": "2019-12-05T10:26:49+01:00", 
    "meetpunt": [
        {"@beschrijvende_id": "H222L10", 
            "@unieke_id": "29", 
            "lve_nr": "55", 
            "tijd_waarneming": "2020-07-26T16:03:00+01:00", 
            "tijd_laatst_gewijzigd": "2020-07-26T16:04:24+01:00", 
            "actueel_publicatie": "1", 
            "beschikbaar": "1", "defect": "0", "geldig": "0", 
            "meetdata": [
                {"@klasse_id": "1", "verkeersintensiteit": "26", "voertuigsnelheid_rekenkundig": "0", "voertuigsnelheid_harmonisch": "252"}, 
                {"@klasse_id": "2", "verkeersintensiteit": "8", "voertuigsnelheid_rekenkundig": "0", "voertuigsnelheid_harmonisch": "252"}, 
                {"@klasse_id": "3", "verkeersintensiteit": "12", "voertuigsnelheid_rekenkundig": "0", "voertuigsnelheid_harmonisch": "252"}, 
                {"@klasse_id": "4", "verkeersintensiteit": "15", "voertuigsnelheid_rekenkundig": "0", "voertuigsnelheid_harmonisch": "252"}, 
                {"@klasse_id": "5", "verkeersintensiteit": "10", "voertuigsnelheid_rekenkundig": "0", "voertuigsnelheid_harmonisch": "252"}
            ], 
            "rekendata": {"bezettingsgraad": "0", "beschikbaarheidsgraad": "100", "onrustigheid": "0"}}]}}
"""
df = sc.parallelize([schema])
schema = spark.read.json(df).schema

# COMMAND ----------

# MAGIC %md # Read input data

# COMMAND ----------

reader = (
    spark
      .readStream
      .format("delta")
      .load(source_path + "delta_table/")
      .withColumn("value", F.from_json(F.col("value"), schema))
      .transform(sensor_data_staging_transform)
 )

# COMMAND ----------

# MAGIC %md # Write streaming

# COMMAND ----------

query = (
  reader
  .writeStream
  .outputMode("append")
  .foreachBatch(lambda batch_df, batch_id: merge(batch_df, batch_id, sink_path = sink_path + "delta_table/", merge_columns = ["load_date", "sensor_id", "descriptive_id", "vehicle_class"], partition_column = "hour_key"))
  .option("checkpointLocation", sink_path + "checkpoint/")
  .trigger(once = True)
  .start()
).awaitTermination()

# COMMAND ----------

dbutils.notebook.exit(1)