-- ===========================================================================
-- SILVER: limpeza, padronização e tipagem em HiveQL.
-- Lê o JSON Lines da Bronze com get_json_object e grava Parquet.
-- ===========================================================================

-- --------------------------------------------------------------- Instagram
DROP TABLE IF EXISTS silver.instagram;
CREATE TABLE silver.instagram
STORED AS PARQUET
AS
SELECT
  get_json_object(line, '$.id')                                  AS id,
  get_json_object(line, '$.plataforma')                          AS plataforma,
  get_json_object(line, '$.tipo')                                AS tipo,
  trim(get_json_object(line, '$.texto'))                         AS texto,
  lower(
    translate(
      lower(trim(get_json_object(line, '$.texto'))),
      'áàâãäéèêëíìîïóòôõöúùûüçñ',
      'aaaaaeeeeiiiiooooouuuucn'
    )
  )                                                              AS texto_normalizado,
  get_json_object(line, '$.data')                                AS data,
  substr(get_json_object(line, '$.data'), 1, 10)                 AS data_dia,
  substr(get_json_object(line, '$.data'), 12, 2)                 AS hora,
  CASE pmod(datediff(substr(get_json_object(line, '$.data'), 1, 10), '1970-01-05'), 7)
    WHEN 0 THEN 'Segunda'
    WHEN 1 THEN 'Terca'
    WHEN 2 THEN 'Quarta'
    WHEN 3 THEN 'Quinta'
    WHEN 4 THEN 'Sexta'
    WHEN 5 THEN 'Sabado'
    WHEN 6 THEN 'Domingo'
    ELSE 'Desconhecido'
  END                                                            AS dia_semana,
  substr(get_json_object(line, '$.data'), 1, 7)                  AS ano_mes,
  COALESCE(CAST(get_json_object(line, '$.curtidas') AS BIGINT), 0)     AS curtidas,
  COALESCE(CAST(get_json_object(line, '$.comentarios') AS BIGINT), 0)  AS comentarios,
  CAST(get_json_object(line, '$.nota') AS BIGINT)                AS nota,
  get_json_object(line, '$.autor')                               AS autor,
  get_json_object(line, '$.url')                                 AS url,
  get_json_object(line, '$.tipo_midia')                          AS tipo_midia,
  COALESCE(CAST(get_json_object(line, '$.curtidas') AS BIGINT), 0)
    + COALESCE(CAST(get_json_object(line, '$.comentarios') AS BIGINT), 0)
                                                                 AS engajamento
FROM bronze.instagram_raw
WHERE get_json_object(line, '$.id') IS NOT NULL
  AND get_json_object(line, '$.data') IS NOT NULL;

-- ------------------------------------------------------------ Google Maps
DROP TABLE IF EXISTS silver.google;
CREATE TABLE silver.google
STORED AS PARQUET
AS
SELECT
  get_json_object(line, '$.id')                                  AS id,
  get_json_object(line, '$.plataforma')                          AS plataforma,
  get_json_object(line, '$.tipo')                                AS tipo,
  trim(get_json_object(line, '$.texto'))                         AS texto,
  lower(
    translate(
      lower(trim(get_json_object(line, '$.texto'))),
      'áàâãäéèêëíìîïóòôõöúùûüçñ',
      'aaaaaeeeeiiiiooooouuuucn'
    )
  )                                                              AS texto_normalizado,
  get_json_object(line, '$.data')                                AS data,
  substr(get_json_object(line, '$.data'), 1, 10)                 AS data_dia,
  substr(get_json_object(line, '$.data'), 12, 2)                 AS hora,
  CASE pmod(datediff(substr(get_json_object(line, '$.data'), 1, 10), '1970-01-05'), 7)
    WHEN 0 THEN 'Segunda'
    WHEN 1 THEN 'Terca'
    WHEN 2 THEN 'Quarta'
    WHEN 3 THEN 'Quinta'
    WHEN 4 THEN 'Sexta'
    WHEN 5 THEN 'Sabado'
    WHEN 6 THEN 'Domingo'
    ELSE 'Desconhecido'
  END                                                            AS dia_semana,
  substr(get_json_object(line, '$.data'), 1, 7)                  AS ano_mes,
  COALESCE(CAST(get_json_object(line, '$.curtidas') AS BIGINT), 0)     AS curtidas,
  COALESCE(CAST(get_json_object(line, '$.comentarios') AS BIGINT), 0)  AS comentarios,
  CAST(get_json_object(line, '$.nota') AS BIGINT)                AS nota,
  get_json_object(line, '$.autor')                               AS autor,
  get_json_object(line, '$.url')                                 AS url,
  get_json_object(line, '$.tipo_midia')                          AS tipo_midia,
  COALESCE(CAST(get_json_object(line, '$.curtidas') AS BIGINT), 0)
    + COALESCE(CAST(get_json_object(line, '$.comentarios') AS BIGINT), 0)
                                                                 AS engajamento
FROM bronze.google_raw
WHERE get_json_object(line, '$.id') IS NOT NULL
  AND get_json_object(line, '$.data') IS NOT NULL;

-- -------------------------------------------------- Perfil do Instagram
DROP TABLE IF EXISTS silver.instagram_perfil;
CREATE TABLE silver.instagram_perfil
STORED AS PARQUET
AS
SELECT
  get_json_object(line, '$.usuario')    AS usuario,
  get_json_object(line, '$.nome')       AS nome,
  get_json_object(line, '$.biografia')  AS biografia,
  COALESCE(CAST(get_json_object(line, '$.seguidores') AS BIGINT), 0) AS seguidores,
  COALESCE(CAST(get_json_object(line, '$.seguindo') AS BIGINT), 0)   AS seguindo,
  COALESCE(CAST(get_json_object(line, '$.posts') AS BIGINT), 0)      AS posts,
  CAST(get_json_object(line, '$.verificado') AS BOOLEAN)             AS verificado,
  get_json_object(line, '$.categoria')  AS categoria,
  get_json_object(line, '$.site')       AS site,
  get_json_object(line, '$.url')        AS url
FROM bronze.instagram_perfil_raw
WHERE get_json_object(line, '$.usuario') IS NOT NULL;

-- --------------------------------------------------- Local no Google Maps
DROP TABLE IF EXISTS silver.google_local;
CREATE TABLE silver.google_local
STORED AS PARQUET
AS
SELECT
  get_json_object(line, '$.nome')          AS nome,
  get_json_object(line, '$.categoria')     AS categoria,
  get_json_object(line, '$.endereco')      AS endereco,
  get_json_object(line, '$.bairro')        AS bairro,
  get_json_object(line, '$.cidade')        AS cidade,
  get_json_object(line, '$.estado')        AS estado,
  get_json_object(line, '$.cep')           AS cep,
  get_json_object(line, '$.telefone')      AS telefone,
  get_json_object(line, '$.site')          AS site,
  CAST(get_json_object(line, '$.nota_media') AS DOUBLE)              AS nota_media,
  COALESCE(CAST(get_json_object(line, '$.total_avaliacoes') AS BIGINT), 0) AS total_avaliacoes,
  CAST(get_json_object(line, '$.latitude') AS DOUBLE)                AS latitude,
  CAST(get_json_object(line, '$.longitude') AS DOUBLE)               AS longitude,
  get_json_object(line, '$.place_id')      AS place_id,
  get_json_object(line, '$.url')           AS url
FROM bronze.google_local_raw
WHERE get_json_object(line, '$.nome') IS NOT NULL;

-- ------------------------------------------- Visão unificada das interações
DROP TABLE IF EXISTS silver.interacoes;
CREATE TABLE silver.interacoes
STORED AS PARQUET
AS
SELECT
  id, plataforma, tipo, texto, texto_normalizado, data, data_dia, hora,
  dia_semana, ano_mes, curtidas, comentarios, nota, autor, url, tipo_midia,
  engajamento
FROM silver.instagram
UNION ALL
SELECT
  id, plataforma, tipo, texto, texto_normalizado, data, data_dia, hora,
  dia_semana, ano_mes, curtidas, comentarios, nota, autor, url, tipo_midia,
  engajamento
FROM silver.google;
