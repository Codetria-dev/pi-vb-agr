-- Consultas de exemplo no Trino (catálogo "hive").
-- UI: http://localhost:8080 · CLI:
--   docker compose -f infra/docker-compose.yml exec trino trino

SHOW SCHEMAS FROM hive;
SHOW TABLES FROM hive.gold;

-- 1) Engajamento por plataforma
SELECT * FROM hive.gold.engajamento_plataforma ORDER BY plataforma;

-- 2) Sentimento das avaliações do Google
SELECT * FROM hive.gold.sentimento_google
ORDER BY CASE sentimento
  WHEN 'Positivo' THEN 1 WHEN 'Neutro' THEN 2 ELSE 3 END;

-- 3) Temas mais citados
SELECT * FROM hive.gold.temas ORDER BY mencoes DESC LIMIT 15;

-- 4) Frequência de postagem × engajamento
SELECT * FROM hive.gold.frequencia_engajamento
ORDER BY media_engajamento DESC LIMIT 10;

-- 5) Evolução temporal
SELECT * FROM hive.gold.evolucao_temporal ORDER BY ano_mes, plataforma;

-- Extras para o dashboard
SELECT * FROM hive.gold.kpis ORDER BY metrica;
SELECT * FROM hive.gold.engajamento_tipo_midia ORDER BY media_curtidas DESC;
SELECT * FROM hive.gold.instagram_top_posts ORDER BY engajamento DESC;
SELECT * FROM hive.gold.google_maps_avaliacoes_por_nota ORDER BY stars;
SELECT * FROM hive.gold.google_maps_avaliacoes_recentes ORDER BY published_at DESC LIMIT 10;

-- Conferência das camadas
SELECT 'bronze.instagram_raw' AS tabela, COUNT(*) AS linhas FROM hive.bronze.instagram_raw
UNION ALL SELECT 'bronze.google_raw', COUNT(*) FROM hive.bronze.google_raw
UNION ALL SELECT 'silver.instagram', COUNT(*) FROM hive.silver.instagram
UNION ALL SELECT 'silver.google', COUNT(*) FROM hive.silver.google
UNION ALL SELECT 'silver.interacoes', COUNT(*) FROM hive.silver.interacoes
UNION ALL SELECT 'gold.kpis', COUNT(*) FROM hive.gold.kpis;
