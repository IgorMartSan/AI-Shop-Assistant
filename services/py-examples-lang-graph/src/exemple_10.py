# main.py

from typing import Annotated, TypedDict, Literal
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import START, StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
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


model = init_chat_model(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    model_provider="groq",
    temperature=0,
)


llm = init_chat_model(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    model_provider="groq",
    temperature=0,
)


#State
class ChatState(TypedDict):
    messages: Annotated[list, add_messages]

#Nodes

def limit_checkpoint_size(state: ChatState):
    messages = state["messages"]

    numMessages = -10

    system_messages = [m for m in messages if m.type == "system"]
    other_messages = [m for m in messages if m.type != "system"]

    limited_messages = system_messages + other_messages[numMessages:]

    return {
        "messages": limited_messages
    }



class RouteDecision(TypedDict):
    next_node: str


router_llm = llm.with_structured_output(RouteDecision)




def decide_next_node(state: ChatState):
    msg = state["messages"][-1].content

    allowed_nodes = ["chat_node", "sql_node"]

    try:
        decision: RouteDecision = router_llm.invoke([
            SystemMessage(content=f"""
                Classifique a mensagem do usuário.

                Escolha exatamente um dos nodes abaixo:

                - chat_node → conversa normal
                - sql_node → perguntas sobre SQL, banco, tabelas, colunas ou dados

                Responda apenas com o campo next_node.
                O valor deve ser exatamente um destes:
                {", ".join(allowed_nodes)}
                """),
            HumanMessage(content=msg)
        ])

        next_node = decision["next_node"].strip()

        # 🔥 VALIDAÇÃO (ESSENCIAL)
        if next_node in allowed_nodes:
            return next_node

        # fallback se vier errado
        return "chat_node"

    except Exception:
        return "chat_node"

def call_model(state: ChatState):
    response = llm.invoke(state["messages"])

    return {
        "messages": [response]
    }







def build_graph():
    graph = StateGraph(ChatState)

    graph.add_node("call_model", call_model)
    graph.add_node("limit_checkpoint_size", limit_checkpoint_size)
    graph.add_edge(START, "limit_checkpoint_size")
    graph.add_edge("limit_checkpoint_size", "call_model")
    graph.add_edge("call_model", END)

    return graph


graph = build_graph()

with PostgresSaver.from_conn_string(connection_string) as checkpointerPostgres:
    checkpointerPostgres.setup()
    app = graph.compile(checkpointer=checkpointerPostgres)


    user_id = "1"
    config = {
        "configurable": {
            "thread_id": f"user:{user_id}"
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