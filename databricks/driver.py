# Databricks notebook source
# MAGIC %md # Setup credentials

# COMMAND ----------

# MAGIC %run ./setup_credentials

# COMMAND ----------

# MAGIC %run ./shared_library

# COMMAND ----------

# MAGIC %md # Landing

# COMMAND ----------

# MAGIC %run ./sensor_data/1_raw_to_landing

# COMMAND ----------

# MAGIC %run ./sensor_description/1_raw_to_landing

# COMMAND ----------

# MAGIC %md # Staging

# COMMAND ----------

# MAGIC %run ./sensor_data/2_landing_to_staging

# COMMAND ----------

# MAGIC %run ./sensor_description/2_landing_to_staging

# COMMAND ----------

# MAGIC %md # Curated

# COMMAND ----------

# MAGIC %run ./curated/advertising

# COMMAND ----------

# MAGIC %run ./curated/traffic_status

# COMMAND ----------

# MAGIC %md # Load to DB

# COMMAND ----------

# MAGIC %run ./dw/load_to_dw

# COMMAND ----------

dbutils.notebook.exit(1)