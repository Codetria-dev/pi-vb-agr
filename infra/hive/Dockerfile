FROM apache/hive:3.1.3

USER root

# A imagem traz um driver PostgreSQL 9.4 que nao suporta SCRAM-SHA-256
# (autenticacao padrao do PostgreSQL 15). Removemos antes de adicionar o 42.x.
RUN rm -f /opt/hive/lib/postgresql-9.4.1208.jre7.jar

# Driver JDBC usado pelo Hive Metastore para falar com o PostgreSQL.
ADD https://jdbc.postgresql.org/download/postgresql-42.7.12.jar /opt/hive/lib/postgresql.jar
RUN chmod 644 /opt/hive/lib/postgresql.jar

USER hive
