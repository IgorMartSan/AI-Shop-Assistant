# main.py

from typing import Annotated, TypedDict
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import START, StateGraph, END
from langgraph.graph.message import add_messages

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from psycopg_pool import ConnectionPool

from langchain.chat_models import init_chat_model
from prompts.sql_agent_prompt import system_message

import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_HOST_TEST = os.getenv("POSTGRES_HOST_TEST", "localhost")
POSTGRES_PORT_TEST = int(os.getenv("POSTGRES_PORT_TEST", "5432"))
POSTGRES_USER_TEST = os.getenv("POSTGRES_USER_TEST", "postgres")
POSTGRES_PASSWORD_TEST = os.getenv("POSTGRES_PASSWORD_TEST", "")
POSTGRES_DB_TEST = os.getenv("POSTGRES_DB_TEST", "postgres")

connection_string = (
    f"postgresql://{POSTGRES_USER_TEST}:{POSTGRES_PASSWORD_TEST}"
    f"@{POSTGRES_HOST_TEST}:{POSTGRES_PORT_TEST}/{POSTGRES_DB_TEST}"
)

# Pool de conexões PostgreSQL
pool = ConnectionPool(
    conninfo=connection_string,
    min_size=1,
    max_size=10,
    kwargs={
        "autocommit": True,
        "prepare_threshold": 0,
    },
)

# SHORT MEMORY
checkpointer = PostgresSaver(pool)
checkpointer.setup()

# LONG MEMORY
store = PostgresStore(pool)
store.setup()


llm = init_chat_model(
    model="llama3.2",
    model_provider="ollama",
    base_url="http://localhost:11434",
    temperature=0,
)


# State
class ChatState(TypedDict):
    messages: Annotated[list, add_messages]


# Nodes
def limit_checkpoint_size(state: ChatState):
    messages = state["messages"]

    num_messages = -10

    system_messages = [m for m in messages if m.type == "system"]
    other_messages = [m for m in messages if m.type != "system"]

    limited_messages = system_messages + other_messages[num_messages:]

    return {
        "messages": limited_messages
    }


class RouteDecision(TypedDict):
    next_node: str


router_llm = llm.with_structured_output(RouteDecision)


def decide_next_node(state: ChatState):
    msg = state["messages"][-1].content

    allowed_nodes = ["A", "B"]

    try:
        decision: RouteDecision = router_llm.invoke([
            SystemMessage(content=f"""
                Classifique a mensagem do usuário.

                Escolha exatamente um dos nodes abaixo:

                - A → conversa normal
                - B → perguntas sobre SQL, banco, tabelas, colunas ou dados

                Responda apenas com o campo next_node.
                O valor deve ser exatamente um destes:
                {", ".join(allowed_nodes)}
            """),
            HumanMessage(content=msg)
        ])

        next_node = decision["next_node"].strip()

        if next_node in allowed_nodes:
            return next_node

        return "A"

    except Exception:
        return "A"


def call_model(state: ChatState):
    response = llm.invoke(state["messages"])

    return {
        "messages": [response]
    }


def sql_node(state: ChatState):
    response = llm.invoke(state["messages"])

    return {
        "messages": [response]
    }






# Build 

def build_graph():
    graph = StateGraph(ChatState)

    graph.add_node("limit_checkpoint_size", limit_checkpoint_size)
    graph.add_node("call_model", call_model)
    graph.add_node("sql_node", sql_node)



    graph.add_edge(START, "limit_checkpoint_size")

    graph.add_conditional_edges("limit_checkpoint_size",
        decide_next_node,
        {
            "A": "call_model",
            "B": "sql_node",
        }
    )

    graph.add_edge("call_model", END)

    graph.add_edge("sql_node", END)


    return graph


graph = build_graph()

app = graph.compile(
    checkpointer=checkpointer,
    store=store,
)




user_id = "1"

config = {
    "configurable": {
        "thread_id": f"user:{user_id}",
        "user_id": user_id,
    }
}


app.invoke(
    {
        "messages": [
            system_message,
            HumanMessage(content="Quais são as tabelas disponíveis no banco de dados?")
        ]
    },
    config=config
)


print("Chat iniciado. Digite 'sair' para encerrar.\n")

try:
    while True:
        user_input = input("Você: ")

        if user_input.lower() == "sair":
            break

        result = app.invoke(
            {
                "messages": [
                    HumanMessage(content=user_input)
                ]
            },
            config=config
        )

        state = app.get_state(config)

        messages = state.values.get("messages", [])

        print("Quantidade de mensagens:", len(messages))
        print("IA:", result["messages"][-1].content)
        print()

finally:
    pool.close()
