FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

# 1. Copia só arquivos de dependência
COPY libs/common/pyproject.toml /app/libs/common/pyproject.toml
COPY libs/common/uv.lock /app/libs/common/uv.lock
COPY message-aggregator-service/pyproject.toml /app/message-aggregator-service/pyproject.toml
COPY message-aggregator-service/uv.lock /app/message-aggregator-service/uv.lock

# 2. Copia o pacote common, porque ele é dependência local
COPY libs/common /app/libs/common

# 3. Instala dependências do serviço
WORKDIR /app/message-aggregator-service
RUN uv sync --frozen --no-install-project

# 4. Agora copia o código do serviço
COPY message-aggregator-service /app/message-aggregator-service

# 5. Instala o projeto em si
RUN uv sync --frozen

CMD ["uv", "run", "python", "src/main.py"]