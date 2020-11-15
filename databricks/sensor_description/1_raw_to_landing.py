# Databricks notebook source
# MAGIC %md # Import libraries

# COMMAND ----------

import pyspark.sql.functions as F 
from pyspark.sql.types import ArrayType, StructType, StructField, StringType
from delta.tables import *

# COMMAND ----------

# MAGIC %md # Read input data

# COMMAND ----------

regex_exp = "_([0-9]+).json.gz"

reader = (
  spark.readStream 
  .format("abs-aqs") 
  .option("fileFormat", "text") 
  .option("queueName", "sensor-description-queue") 
  .option("connectionString", conn_datalake) 
  .schema(StructType([StructField("value", StringType())])) 
  .load()
  
  .withColumn("source_file", F.input_file_name())
  .withColumn("process_date", F.current_timestamp())
  .withColumn("load_date", F.regexp_extract(F.col("source_file"), regex_exp, 1))
  .withColumn("load_date", F.to_timestamp(F.col("load_date"), "yyyyMMddHHmm"))
  .withColumn("hour_key", F.date_format(F.col("load_date"), "yyyyMMddHH"))
)

# COMMAND ----------

# MAGIC %md # Define sink path

# COMMAND ----------

landing_path = f"abfss://datalake@{stgendpoint}.dfs.core.windows.net/landing/sensor_description/"

# COMMAND ----------

# MAGIC %md # Write streaming

# COMMAND ----------

query = (
  reader
  .writeStream
  .outputMode("append")
  .foreachBatch(
    lambda batch_df, batch_id: 
    merge(
      batch_df, 
      batch_id, 
      sink_path = landing_path + "delta_table/", 
      merge_columns = ["load_date"], 
      partition_column = "hour_key"))
  .option("checkpointLocation", landing_path + "checkpoint/")
  .trigger(once = True)
  .start()
).awaitTermination()

# COMMAND ----------

dbutils.notebook.exit(1)