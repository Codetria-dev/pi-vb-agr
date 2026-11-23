-- Bancos das três camadas do lakehouse.
CREATE DATABASE IF NOT EXISTS bronze
  LOCATION 'hdfs://namenode:9000/lake/warehouse/bronze.db';

CREATE DATABASE IF NOT EXISTS silver
  LOCATION 'hdfs://namenode:9000/lake/warehouse/silver.db';

CREATE DATABASE IF NOT EXISTS gold
  LOCATION 'hdfs://namenode:9000/lake/warehouse/gold.db';
