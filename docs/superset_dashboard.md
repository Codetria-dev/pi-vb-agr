# Dashboard no Apache Superset

> **Atalho:** o dashboard completo (12 gráficos: 4 KPIs, 4 pizzas e 4 tabelas)
> é criado automaticamente com `bash scripts/08_criar_dashboard.sh` e fica em
> http://localhost:8088/superset/dashboard/agr-engajamento-digital/.
> As receitas abaixo servem para ajustes manuais.

Este guia monta o dashboard **AGR - Engajamento Digital** a partir das tabelas
da camada Gold. O Superset lê os dados via **Trino** (catálogo `hive`).

> Pré-requisito: o pipeline já rodou até o fim
> (`bash scripts/04_pipeline_completo.sh`) e o container `agr-superset` está de pé.
> A conexão `Trino AGR` e os datasets da camada Gold são registrados
> automaticamente pelos scripts `04_pipeline_completo.sh` / `05_superset_datasets.sh`.

---

## 1. Acessar

- URL: <http://localhost:8088>
- Usuário: `admin`
- Senha: `admin`

Se o login falhar, recrie a senha:

```bash
docker compose -f infra/docker-compose.yml exec superset superset fab reset-password \
  --username admin --password admin
```

---

## 2. Conectar o Superset ao Trino

A conexão já é criada automaticamente com o nome **`Trino AGR`** e a URI
`trino://admin@trino:8080/hive`. Para conferir (ou recriar manualmente):

1. Menu **Settings → Database Connections**.
2. Confirme a conexão **Trino AGR** (ou clique em **+ Database**).
3. Se criar manualmente, preencha:
   - **Display Name:** `Trino AGR`
   - **SQLAlchemy URI:** `trino://admin@trino:8080/hive`
4. Clique em **Test Connection** (deve aparecer "Connection looks good!").
5. Clique em **Connect**.

> Use o hostname `trino` (nome do serviço no Docker Compose), e **não**
> `localhost`. O Superset fala com o Trino pela rede interna do Compose.

---

## 3. Criar os datasets

O script `bash scripts/05_superset_datasets.sh` registra automaticamente todos
os datasets abaixo. Se precisar criar/renomear manualmente, use
**Data → Datasets → + Dataset** e, para cada tabela, selecione:

- **Database:** `Trino AGR`
- **Schema:** `gold`
- **Table:** a tabela indicada

| Dataset | Para que serve |
|---|---|
| `engajamento_plataforma` | Média de curtidas/comentários por plataforma |
| `engajamento_tipo_midia` | Média de curtidas por tipo de mídia (Image/Video/Sidecar) |
| `sentimento_google` | Positivo / Neutro / Negativo |
| `temas` | Temas mais citados (NLP básico) |
| `frequencia_engajamento` | Dia da semana × horário × engajamento |
| `evolucao_temporal` | Evolução mês a mês |
| `kpis` | Cartões de KPI |

> Se a tabela não aparecer, rode no Trino:
> `SHOW TABLES FROM hive.gold;` e confira os logs do Hive
> (`docker compose logs hive-server`).

---

## 4. Criar os gráficos

Menu **Charts → + Chart**. Para cada gráfico, escolha o dataset, o tipo de
gráfico e configure as colunas abaixo. Use **Create New Chart** ao final.

### 4.1 Pizza — Sentimento das avaliações do Google

- **Dataset:** `sentimento_google`
- **Chart type:** Pie Chart
- **Dimensions:** `sentimento`
- **Metric:** `SUM(total)`
- **Row limit:** 10
- **Customize → Labels:** percentual + valor

### 4.2 Barras — Média de curtidas por post no Instagram

- **Dataset:** `engajamento_tipo_midia`
- **Chart type:** Bar Chart
- **X-axis:** `tipo_midia`
- **Metrics:** `MAX(media_curtidas)`
- **Sort by:** `MAX(media_curtidas)` (descendente)

> Alternativa com uma única barra: use o dataset `engajamento_plataforma`,
> filtre `plataforma = instagram` e use a métrica `MAX(media_curtidas)`.
> A versão por tipo de mídia deixa o gráfico mais informativo.

### 4.3 Barras horizontais — Temas mais citados

- **Dataset:** `temas`
- **Chart type:** Bar Chart
- **Orientation:** Horizontal
- **Y-axis:** `tema`
- **Metrics:** `SUM(mencoes)`
- **Sort by:** `SUM(mencoes)` (descendente)
- **Row limit:** 15

> O Superset não tem nuvem de palavras nativa. A barra horizontal é a
> alternativa recomendada e cumpre o requisito de "temas mais citados".
> Se quiser nuvem de palavras, instale um plugin de word cloud no Superset.

### 4.4 Cartões (KPIs)

Crie um **Big Number** para cada métrica:

| Nome do cartão | Dataset | Filtro | Métrica |
|---|---|---|---|
| Posts coletados | `kpis` | `metrica = total_posts_instagram` | `SUM(valor)` |
| Avaliações Google | `kpis` | `metrica = total_avaliacoes_google` | `SUM(valor)` |
| Média de engajamento | `kpis` | `metrica = media_engajamento_instagram` | `SUM(valor)` |
| Média de curtidas | `kpis` | `metrica = media_curtidas_instagram` | `SUM(valor)` |

- **Chart type:** Big Number
- Em **Filters**, adicione `metrica` = o valor indicado.
- Em **Customize → Subheader**, escreva o rótulo do cartão.

### 4.5 Linha — Evolução temporal

- **Dataset:** `evolucao_temporal`
- **Chart type:** Line Chart
- **X-axis:** `ano_mes`
- **Metric:** `AVG(media_engajamento)`
- **Group by:** `plataforma`

### 4.6 Barras — Frequência de postagem × engajamento

- **Dataset:** `frequencia_engajamento`
- **Chart type:** Bar Chart
- **X-axis:** `dia_semana`
- **Metrics:** `AVG(media_engajamento)`
- **Sort by:** ordem dos dias (Segunda → Domingo), se disponível

---

## 5. Montar o dashboard

1. Menu **Dashboards → + Dashboard**.
2. Nome: `AGR - Engajamento Digital`.
3. Clique em **Edit dashboard**.
4. Arraste os gráficos criados para o layout:
   - Linha de KPIs no topo (4 cartões).
   - Pizza de sentimento + barras de temas na segunda linha.
   - Barras de curtidas + linha de evolução na terceira linha.
   - Frequência por dia/horário na parte de baixo.
5. Adicione um componente **Markdown** com o objetivo do projeto:

   ```markdown
   ## Diagnóstico de interatividade digital da AGR

   Fontes: Instagram @agrgoias e avaliações do Google Maps.
   Pipeline: Python → HDFS → Hive (Bronze/Silver/Gold) → Trino → Superset.
   ```

6. Clique em **Save**.

---

## 6. Consultas SQL de apoio (SQL Lab)

Se preferir criar os gráficos com SQL manual, use **SQL Lab → SQL Editor**,
selecione o banco `Trino AGR` e rode:

```sql
-- Sentimento
SELECT sentimento, total, percentual
FROM hive.gold.sentimento_google;

-- Média de curtidas por tipo de mídia
SELECT tipo_midia, media_curtidas, media_comentarios
FROM hive.gold.engajamento_tipo_midia;

-- Temas
SELECT tema, mencoes
FROM hive.gold.temas
ORDER BY mencoes DESC;

-- Frequência
SELECT dia_semana, hora, posts, media_engajamento
FROM hive.gold.frequencia_engajamento
ORDER BY media_engajamento DESC;

-- Evolução
SELECT ano_mes, plataforma, media_engajamento
FROM hive.gold.evolucao_temporal
ORDER BY ano_mes;

-- KPIs
SELECT metrica, valor
FROM hive.gold.kpis;
```

Em cada gráfico, ative a opção **Create Chart** a partir do resultado.

---

## 7. Problemas comuns

| Sintoma | Solução |
|---|---|
| "Connection refused" ao testar o Trino | Confirme `docker compose ps`; use o host `trino`, não `localhost` |
| Driver Trino não encontrado | `docker compose build --no-cache superset && docker compose up -d superset` |
| Tabela não aparece no dataset | Rode `SHOW TABLES FROM hive.gold;` no Trino e verifique `docker compose logs hive-server` |
| Erro de permissão no SQLite do Superset | `docker compose exec -u root superset chown -R superset:superset /app/superset_home` |
| Login admin/admin não funciona | `docker compose -f infra/docker-compose.yml exec superset superset fab reset-password --username admin --password admin` |

---

## 8. Entrega do dashboard

Para anexar ao trabalho:

1. Tire prints do dashboard em tela cheia.
2. Exporte o dashboard: **Dashboards → ... → Export**.
3. Salve os prints em `docs/` (eles não são dados brutos e podem ser versionados).
