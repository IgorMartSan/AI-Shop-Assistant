from langgraph.checkpoint.postgres import PostgresSaver
from langchain.chat_models import init_chat_model

#Memory

memory = PostgresSaver.from_conn_string(
    "postgresql://user:password@localhost:5432/meubanco"
)


llm = init_chat_model(    
    #model=GROQ_MODEL,
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    model_provider="groq",
    temperature=0,)