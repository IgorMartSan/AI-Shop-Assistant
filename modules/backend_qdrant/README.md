# backend_qdrant

API minima em FastAPI para busca vetorial no Qdrant.

## Endpoint

- `POST /qdrant/search`

## Variaveis de ambiente

- `QDRANT_URL` (padrao: `http://127.0.0.1:6333`)
- `GLOBAL_RATE_LIMIT` (padrao: `20/second`)
- `LOG_DIR` (padrao local: `modules/backend_qdrant/logs`)

## Docker

- servico: `backend_qdrant`
- porta: `8010`

source .venv/bin/activate
