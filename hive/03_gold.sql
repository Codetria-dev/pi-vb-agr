-- ===========================================================================
-- GOLD: agregações analíticas prontas para o Trino e o Superset.
-- Materializadas em Parquet no warehouse do Hive.
-- ===========================================================================

-- 1) Engajamento por plataforma -------------------------------------------
DROP TABLE IF EXISTS gold.engajamento_plataforma;
CREATE TABLE gold.engajamento_plataforma
STORED AS PARQUET
AS
SELECT
  plataforma,
  tipo,
  COUNT(*)                        AS total_registros,
  ROUND(AVG(curtidas), 2)         AS media_curtidas,
  ROUND(AVG(comentarios), 2)      AS media_comentarios,
  ROUND(AVG(engajamento), 2)      AS media_engajamento,
  SUM(curtidas)                   AS total_curtidas,
  SUM(comentarios)                AS total_comentarios
FROM silver.interacoes
GROUP BY plataforma, tipo;

-- 2) Sentimento das avaliações do Google ----------------------------------
DROP TABLE IF EXISTS gold.sentimento_google;
CREATE TABLE gold.sentimento_google
STORED AS PARQUET
AS
SELECT
  s.sentimento,
  s.total,
  ROUND(s.total * 100.0 / t.total_geral, 2) AS percentual
FROM (
  SELECT
    CASE
      WHEN nota >= 4 THEN 'Positivo'
      WHEN nota = 3  THEN 'Neutro'
      ELSE 'Negativo'
    END AS sentimento,
    COUNT(*) AS total
  FROM silver.google
  WHERE nota IS NOT NULL
  GROUP BY
    CASE
      WHEN nota >= 4 THEN 'Positivo'
      WHEN nota = 3  THEN 'Neutro'
      ELSE 'Negativo'
    END
) s
CROSS JOIN (
  SELECT COUNT(*) AS total_geral
  FROM silver.google
  WHERE nota IS NOT NULL
) t;

-- 3) Temas mais citados (NLP básico por palavras-chave) -------------------
DROP TABLE IF EXISTS gold.temas;
CREATE TABLE gold.temas
STORED AS PARQUET
AS
SELECT
  palavra AS tema,
  COUNT(*) AS mencoes
FROM silver.interacoes
LATERAL VIEW explode(
  array(
    'transporte', 'onibus', 'passagem', 'rodoviaria', 'tarifa',
    'agua', 'esgoto', 'energia', 'enel', 'iluminacao',
    'atendimento', 'fiscalizacao', 'regulacao', 'servico',
    'saude', 'hospital', 'ouvidoria', 'governo',
    'reclamacao', 'denuncia', 'goiania', 'goias'
  )
) t AS palavra
WHERE instr(texto_normalizado, palavra) > 0
GROUP BY palavra;

-- 4) Frequência de postagem × engajamento --------------------------------
DROP TABLE IF EXISTS gold.frequencia_engajamento;
CREATE TABLE gold.frequencia_engajamento
STORED AS PARQUET
AS
SELECT
  dia_semana,
  hora,
  COUNT(*)                    AS posts,
  ROUND(AVG(engajamento), 2)  AS media_engajamento,
  ROUND(AVG(curtidas), 2)     AS media_curtidas,
  ROUND(AVG(comentarios), 2)  AS media_comentarios
FROM silver.interacoes
WHERE plataforma = 'instagram'
GROUP BY dia_semana, hora;

-- 5) Evolução temporal ----------------------------------------------------
DROP TABLE IF EXISTS gold.evolucao_temporal;
CREATE TABLE gold.evolucao_temporal
STORED AS PARQUET
AS
SELECT
  ano_mes,
  plataforma,
  COUNT(*)                    AS total,
  ROUND(AVG(engajamento), 2)  AS media_engajamento,
  SUM(curtidas)               AS total_curtidas,
  SUM(comentarios)            AS total_comentarios
FROM silver.interacoes
GROUP BY ano_mes, plataforma;

-- 6) Engajamento por tipo de mídia ---------------------------------------
DROP TABLE IF EXISTS gold.engajamento_tipo_midia;
CREATE TABLE gold.engajamento_tipo_midia
STORED AS PARQUET
AS
SELECT
  tipo_midia,
  COUNT(*)                    AS posts,
  ROUND(AVG(curtidas), 2)     AS media_curtidas,
  ROUND(AVG(comentarios), 2)  AS media_comentarios,
  ROUND(AVG(engajamento), 2)  AS media_engajamento
FROM silver.interacoes
WHERE plataforma = 'instagram'
GROUP BY tipo_midia;

-- 7) KPIs para os cartões do dashboard -----------------------------------
DROP TABLE IF EXISTS gold.kpis;
CREATE TABLE gold.kpis
STORED AS PARQUET
AS
SELECT metrica, valor FROM (
  SELECT 'total_posts_instagram' AS metrica,
         CAST(COUNT(*) AS DOUBLE) AS valor
  FROM silver.interacoes WHERE plataforma = 'instagram'
  UNION ALL
  SELECT 'total_avaliacoes_google',
         CAST(COUNT(*) AS DOUBLE)
  FROM silver.interacoes WHERE plataforma = 'google_maps'
  UNION ALL
  SELECT 'total_interacoes_instagram',
         CAST(SUM(engajamento) AS DOUBLE)
  FROM silver.interacoes WHERE plataforma = 'instagram'
  UNION ALL
  SELECT 'media_engajamento_instagram',
         ROUND(AVG(engajamento), 2)
  FROM silver.interacoes WHERE plataforma = 'instagram'
  UNION ALL
  SELECT 'media_curtidas_instagram',
         ROUND(AVG(curtidas), 2)
  FROM silver.interacoes WHERE plataforma = 'instagram'
  UNION ALL
  SELECT 'media_nota_google',
         ROUND(AVG(nota), 2)
  FROM silver.interacoes
  WHERE plataforma = 'google_maps' AND nota IS NOT NULL
  UNION ALL
  SELECT 'seguidores_instagram',
         CAST(MAX(seguidores) AS DOUBLE)
  FROM silver.instagram_perfil
  UNION ALL
  SELECT 'nota_media_google',
         ROUND(AVG(nota_media), 2)
  FROM silver.google_local
  UNION ALL
  SELECT 'taxa_engajamento_pct',
         ROUND(100.0 * AVG(i.engajamento) / MAX(p.seguidores), 3)
  FROM silver.interacoes i
  CROSS JOIN silver.instagram_perfil p
  WHERE i.plataforma = 'instagram' AND p.seguidores > 0
) u;

-- 8) Top posts por engajamento -------------------------------------------
DROP TABLE IF EXISTS gold.instagram_top_posts;
CREATE TABLE gold.instagram_top_posts
STORED AS PARQUET
AS
SELECT
  i.id                              AS post_id,
  i.data                            AS posted_at,
  i.tipo_midia                      AS post_type,
  i.texto                           AS caption,
  i.url                             AS post_url,
  i.curtidas                        AS likes_count,
  i.comentarios                     AS comments_count,
  i.engajamento,
  ROUND(100.0 * i.engajamento / p.seguidores, 3) AS engagement_rate_pct
FROM silver.instagram i
CROSS JOIN silver.instagram_perfil p
ORDER BY i.engajamento DESC
LIMIT 20;

-- 9) Distribuição das avaliações por nota --------------------------------
DROP TABLE IF EXISTS gold.google_maps_avaliacoes_por_nota;
CREATE TABLE gold.google_maps_avaliacoes_por_nota
STORED AS PARQUET
AS
SELECT
  nota AS stars,
  COUNT(*) AS reviews
FROM silver.google
WHERE nota IS NOT NULL
GROUP BY nota;

-- 10) Avaliações mais recentes -------------------------------------------
DROP TABLE IF EXISTS gold.google_maps_avaliacoes_recentes;
CREATE TABLE gold.google_maps_avaliacoes_recentes
STORED AS PARQUET
AS
SELECT
  id        AS review_id,
  data      AS published_at,
  nota      AS stars,
  texto     AS review_text,
  curtidas  AS likes_count,
  autor     AS reviewer_name
FROM silver.google
ORDER BY data DESC
LIMIT 50;
