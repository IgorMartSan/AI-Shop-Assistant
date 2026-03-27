

uv init py-zcommonlib --lib 
uv init py-api 
uv init py-basecamp

source .venv/bin/activate
deactivate

Não precisa de usar o sync pode usar o run que ele vai instalar caso nao esteja instalado
uv sync
uv run python main.py