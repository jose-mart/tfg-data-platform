# Databricks notebook source
# MAGIC %md # Read Fact Tables

# COMMAND ----------

traffic_status = spark.read.format("delta").load(f"abfss://datalake@{stgendpoint}.dfs.core.windows.net/curated/traffic_status/delta_table/")
advertising = spark.read.format("delta").load(f"abfss://datalake@{stgendpoint}.dfs.core.windows.net/curated/advertising/delta_table/")

# COMMAND ----------

# MAGIC %md # Write Fact Tables

# COMMAND ----------

(
  traffic_status
    .write
    .jdbc(url = jdbcUrl, table = "traffic_status", mode = "overwrite", properties = connectionProperties)
)

# COMMAND ----------

(
  advertising
    .write
    .jdbc(url = jdbcUrl, table = "advertising", mode = "overwrite", properties = connectionProperties)
)