-- ===========================================================================
-- BRONZE: JSON Lines (um objeto por linha) no HDFS, sem transformação.
-- Cada linha é lida como texto e interpretada com get_json_object na Silver.
-- ===========================================================================

CREATE EXTERNAL TABLE IF NOT EXISTS bronze.instagram_raw (
  line STRING
)
STORED AS TEXTFILE
LOCATION 'hdfs://namenode:9000/lake/bronze/instagram';

CREATE EXTERNAL TABLE IF NOT EXISTS bronze.google_raw (
  line STRING
)
STORED AS TEXTFILE
LOCATION 'hdfs://namenode:9000/lake/bronze/google';

CREATE EXTERNAL TABLE IF NOT EXISTS bronze.instagram_perfil_raw (
  line STRING
)
STORED AS TEXTFILE
LOCATION 'hdfs://namenode:9000/lake/bronze/instagram_perfil';

CREATE EXTERNAL TABLE IF NOT EXISTS bronze.google_local_raw (
  line STRING
)
STORED AS TEXTFILE
LOCATION 'hdfs://namenode:9000/lake/bronze/google_local';
