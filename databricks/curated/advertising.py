# Databricks notebook source
# MAGIC %md # Import libraries

# COMMAND ----------

import pyspark.sql.functions as F 
from delta.tables import *
from itertools import chain

# COMMAND ----------

source_sensor_description_path = f"abfss://datalake@{stgendpoint}.dfs.core.windows.net/staging/sensor_description/delta_table"
source_sensor_data_path = f"abfss://datalake@{stgendpoint}.dfs.core.windows.net/staging/sensor_data/delta_table"
sink_path = f"abfss://datalake@{stgendpoint}.dfs.core.windows.net/curated/advertising/"

# COMMAND ----------

# MAGIC %md # Read dimension tables

# COMMAND ----------

D_sensor_data = (
  spark
  .readStream
  .format("delta")
  .load(source_sensor_data_path)
  .withWatermark("load_date", "7 days")
)

# COMMAND ----------

# MAGIC %md # Write stream

# COMMAND ----------

query = (
  D_sensor_data
  .writeStream
  .outputMode("append")
  .foreachBatch(lambda batch_df, batch_id: merge_advertising(batch_df, batch_id, sink_path = sink_path + "delta_table/", merge_columns = ["sensor_id", "descriptive_id", "hour_key"], partition_column = "hour_key"))
  .option("checkpointLocation", sink_path + "checkpoint/")
  .trigger(once = True)
  .start()
).awaitTermination()

# COMMAND ----------

dbutils.notebook.exit(1)