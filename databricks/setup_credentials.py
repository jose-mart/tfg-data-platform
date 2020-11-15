# Databricks notebook source
secretScope = "tfg_credentials"

stgendpoint = dbutils.secrets.get(scope = secretScope, key = 'stg-name')
stgkey = dbutils.secrets.get(scope = secretScope, key = 'stg-key')

spark.conf.set('fs.azure.account.key.' + stgendpoint + '.dfs.core.windows.net', stgkey)
spark.conf.set('fs.azure.account.key.' + stgendpoint + '.blob.core.windows.net', stgkey)

# COMMAND ----------

conn_datalake = dbutils.secrets.get(scope = secretScope, key = 'stg-connection-string')

# COMMAND ----------

jdbcHostname = dbutils.secrets.get(scope = secretScope, key = "db-hostname")
jdbcDatabase = dbutils.secrets.get(scope = secretScope, key = "db-database")
jdbcPort = "1433"
jdbcPassword = dbutils.secrets.get(scope = secretScope, key = "db-password")
jdbcUsername = dbutils.secrets.get(scope = secretScope, key = "db-username")
driver = "com.microsoft.sqlserver.jdbc.SQLServerDriver"

jdbcUrl = "jdbc:sqlserver://{0}:{1};database={2}".format(jdbcHostname, jdbcPort, jdbcDatabase)
connectionProperties = {
  "user" : jdbcUsername,
  "password" : jdbcPassword
}