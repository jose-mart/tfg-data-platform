# Databricks notebook source
# MAGIC %md # Import libraries

# COMMAND ----------

import pyspark.sql.functions as F 
from pyspark.sql.types import ArrayType, StructType, StructField, StringType
from delta.tables import *

# COMMAND ----------

# MAGIC %md # Define input and output delta paths

# COMMAND ----------

source_path = f"abfss://datalake@{stgendpoint}.dfs.core.windows.net/landing/sensor_description/"
sink_path = f"abfss://datalake@{stgendpoint}.dfs.core.windows.net/staging/sensor_description/"

# COMMAND ----------

# MAGIC %md # Define schema

# COMMAND ----------

schema = """
{"mivconfig": {"@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance", "@xsi:noNamespaceSchemaLocation": "http://miv.opendata.belfla.be/miv-config.xsd", "@schemaVersion": "1.0.0", "tijd_laatste_config_wijziging": "2019-12-05T10:26:49+01:00", "meetpunt": [{"@unieke_id": "3640", "beschrijvende_id": "H291L10", "volledige_naam": "Parking Kruibeke", "Ident_8": "A0140002", "lve_nr": "437", "Kmp_Rsys": "94,695", "Rijstrook": "R10", "X_coord_EPSG_31370": "144474,5297", "Y_coord_EPSG_31370": "208293,5324", "lengtegraad_EPSG_4326": "4,289731136", "breedtegraad_EPSG_4326": "51,18460764"}]}}
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
      .transform(sensor_description_staging_transform)
 )

# COMMAND ----------

# MAGIC %md # Write stream

# COMMAND ----------

query = (
  reader
  .writeStream
  .outputMode("append")
  .foreachBatch(lambda batch_df, batch_id: merge(batch_df, batch_id, sink_path = sink_path + "delta_table/", merge_columns = ["load_date", "sensor_id", "descriptive_id"], partition_column = "hour_key"))
  .option("checkpointLocation", sink_path + "checkpoint/")
  .trigger(once = True)
  .start()
).awaitTermination()

# COMMAND ----------

dbutils.notebook.exit(1)