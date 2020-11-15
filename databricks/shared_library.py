# Databricks notebook source
def merge(batch_df, batch_id, sink_path, merge_columns, partition_column):
  """
  Merge a batch from the streaming with the sink data source based on columns parameters.
  The sink dataset can be partitioned too.
  """
  # Check if delta table exists
  try:
    sink = DeltaTable.forPath(spark, sink_path)
  except:
    if partition_column is None:
      batch_df.write.format("delta").save(sink_path)
      return
    else:
      batch_df.write.format("delta").partitionBy(partition_column).save(sink_path)
      return
  
  # Define conds
  conds = " and ".join([f"source.{col} = sink.{col}" for col in merge_columns])
  
  # Execute merge
  (
    sink.alias("source")
      .merge(
        batch_df.alias("sink"),
        conds
      )
      .whenNotMatchedInsertAll()
  ).execute()


# COMMAND ----------

def merge_traffic_status(batch_df, batch_id, sink_path, merge_columns, partition_column):
  """
  Merge a batch from the streaming with the sink data source based on columns parameters.
  The sink dataset can be partitioned also.
  """
  # Check if delta table exists
  try:
    sink = DeltaTable.forPath(spark, sink_path)
  except:
    if partition_column is None:
      traffic_status_logic(batch_df).write.format("delta").save(sink_path)
      return
    else:
      traffic_status_logic(batch_df).write.format("delta").partitionBy(partition_column).save(sink_path)
      return
    
  traffic_status = traffic_status_logic(batch_df)
  
  # Define conds
  conds = " and ".join([f"source.{col} = sink.{col}" for col in merge_columns])
  
  # Execute merge
  (
    sink.alias("source")
      .merge(
        traffic_status.alias("sink"),
        conds
      )
      .whenNotMatchedInsertAll()
      .whenMatchedUpdateAll()
  ).execute()


# COMMAND ----------

def traffic_status_logic(df):
  D_sensor_description = (
    spark
    .read
    .format("delta")
    .load(source_sensor_description_path)
  )
  
  updated_sde = (
    D_sensor_description
    .groupBy("sensor_id", "descriptive_id")
    .agg(
      F.max(F.col("load_date")).alias("date"),
      F.first(F.col("latitude")).alias("latitude"),
      F.first(F.col("longitude")).alias("longitude")
    )
  )
  
  filtered_traffic_df = (
    df
      .filter(F.col("load_date") > F.date_sub(F.col("load_date"), 7))
      .withColumn("week_day", F.dayofweek(F.col("generated_date")))
      .withColumn("hour", F.date_format(F.col("generated_date"), 'H'))
  )

  traffic_mean = filtered_traffic_df.groupBy("sensor_id", "descriptive_id", "week_day", "hour").agg(F.avg(F.col("vehicles_number")).alias("avg_vehicles"))  
  
  traffic_status = updated_sde.join(traffic_mean, ["sensor_id", "descriptive_id"])
  
  return traffic_status

# COMMAND ----------

def merge_advertising(batch_df, batch_id, sink_path, merge_columns, partition_column):
  """
  Merge a batch from the streaming with the sink data source based on columns parameters.
  The sink dataset can be partitioned also.
  """
  # Check if delta table exists
  try:
    sink = DeltaTable.forPath(spark, sink_path)
  except:
    if partition_column is None:
      advertising_logic(batch_df).write.format("delta").save(sink_path)
      return
    else:
      advertising_logic(batch_df).write.format("delta").partitionBy(partition_column).save(sink_path)
      return
    
  advertising = advertising_logic(batch_df)
  
  # Define conds
  conds = " and ".join([f"source.{col} = sink.{col}" for col in merge_columns])
  
  # Execute merge
  (
    sink.alias("source")
      .merge(
        advertising.alias("sink"),
        conds
      )
      .whenNotMatchedInsertAll()
      .whenMatchedUpdateAll()
  ).execute()

# COMMAND ----------

def advertising_logic(df):
  D_sensor_description = (
    spark
    .read
    .format("delta")
    .load(source_sensor_description_path)
  )
  
  updated_sde = (
    D_sensor_description
    .groupBy("sensor_id", "descriptive_id")
    .agg(
      F.max(F.col("load_date")).alias("date"),
      F.first(F.col("latitude")).alias("latitude"),
      F.first(F.col("longitude")).alias("longitude")
    )
  ).drop("date")
  
  mapping = {
    "1": 1,
    "2": 5,
    "3": 7,
    "4": 4,
    "5": 50
  }

  mapping_expr = F.create_map([F.lit(x) for x in chain(*mapping.items())])  

  people_df = (
    df
      .withColumn("people_count", F.col("vehicles_number") * mapping_expr[F.col("vehicle_class")])
      .groupBy("sensor_id", "descriptive_id", "hour_key")
      .agg(
        F.sum(F.col("people_count")).alias("people_count")
      )
    .withColumn("date", F.to_timestamp(F.col("hour_key"), "yyyyMMddHH"))
  )
  
  advertising = updated_sde.join(people_df, ["sensor_id", "descriptive_id"])
  
  return advertising

# COMMAND ----------

def sensor_data_staging_transform(df):
  return (
    df
      .select("*", "value.*").drop("value")
      .select("*", "miv.*").drop("miv")
      .withColumn("meetpunt", F.explode(F.col("meetpunt")))
      .select("*", "meetpunt.*").drop("meetpunt")
      .withColumn("meetdata", F.explode(F.col("meetdata")))
      .select("*", "meetdata.*", "rekendata.*").drop("meetdata", "rekendata")
      .withColumnRenamed('tijd_laatste_config_wijziging', 'last_modified')
      .withColumn('last_modified', F.col('last_modified').cast('timestamp'))
      .withColumnRenamed('tijd_publicatie', 'generated_date')
      .withColumn('generated_Date', F.col('generated_date').cast('timestamp'))
      .withColumnRenamed('@beschrijvende_id','descriptive_id')
      .withColumnRenamed('@unieke_id','sensor_id')
      .withColumnRenamed('actueel_publicatie','recent_data')
      .withColumnRenamed('beschikbaar','availability')
      .withColumnRenamed('defect','failure_status')
      .withColumnRenamed('geldig','data_regularity')
      .withColumnRenamed('lve_nr','local_processing_unit')
      .withColumnRenamed('tijd_laatst_gewijzigd','measurement_date')
      .withColumnRenamed('tijd_waarneming','observation_time')
      .withColumnRenamed('beschikbaarheidsgraad','availability_degree')
      .withColumnRenamed('bezettingsgraad','occupancy')
      .withColumnRenamed('onrustigheid','average_speed')
      .withColumnRenamed('@klasse_id','vehicle_class')
      .withColumnRenamed('verkeersintensiteit','vehicles_number')
      .withColumnRenamed('voertuigsnelheid_harmonisch','harmonic_average_speed')
      .withColumnRenamed('voertuigsnelheid_rekenkundig','arithmetic_average_speed')
)

# COMMAND ----------

def sensor_description_staging_transform(df):
  return (
    df
      .select("*", "value.*").drop("value")
      .select("*", "mivconfig.*").drop("mivconfig")
      .withColumn("meetpunt", F.explode(F.col("meetpunt")))
      .select("*", "meetpunt.*").drop("meetpunt")
      .withColumnRenamed('tijd_laatste_config_wijziging', 'last_modified')
      .withColumn('last_modified', F.col('last_modified').cast('timestamp'))
      .withColumnRenamed('Ident_8', 'road_id')
      .withColumnRenamed('Kmp_Rsys', 'reference_point')
      .withColumnRenamed('Rijstrook', 'lane')
      .withColumnRenamed('X_coord_EPSG_31370', 'coord_X_Belge_1972')
      .withColumnRenamed('Y_coord_EPSG_31370', 'coord_Y_Belge_1972')
      .withColumnRenamed('@unieke_id','sensor_id')
      .withColumnRenamed('beschrijvende_id','descriptive_id')
      .withColumnRenamed('breedtegraad_EPSG_4326','latitude')
      .withColumnRenamed('lengtegraad_EPSG_4326','longitude')
      .withColumnRenamed('lve_nr','local_processing_unit')
      .withColumnRenamed('volledige_naam','rough_textual_description')
  )