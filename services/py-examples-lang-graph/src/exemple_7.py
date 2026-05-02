from typing import Annotated, Literal, TypedDict
#https://docs.langchain.com/oss/python/langchain/messages
from langchain_core.messages import HumanMessage, BaseMessage, SystemMessage, ToolMessage

from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from infra.postgres.connection import PostgresConnection
import os

load_dotenv()

IP = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


postgres_connection = PostgresConnection(
    host=IP,
    port=int(POSTGRES_PORT),
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    database=POSTGRES_DB,
)

sql_database = postgres_connection.get_sql_database()


llm = init_chat_model(    
    #model=GROQ_MODEL,
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    model_provider="groq",
    temperature=0,)

system_msg = SystemMessage(
    content=(
        """Voce e um agente SQL com acesso a ferramentas de banco de dados. 
        "Nao responda com explicacoes teoricas, exemplos genericos ou placeholders. "
        "Sempre use as ferramentas para obter os dados reais do banco. "
        "Se o usuario pedir tabelas, primeiro use sql_db_list_tables. "
        "Se o usuario pedir contagem de registros por tabela, descubra as tabelas reais e depois execute consultas reais com sql_db_query. "
        "Nunca diga que nao tem acesso ao banco, porque voce tem acesso pelas tools. "
        "Baseie a resposta final apenas nos resultados retornados pelas tools."""
    )
)


toolkit = SQLDatabaseToolkit(
    db=sql_database,
    llm=llm,
)

print("Tools available in the toolkit:")
for tool in toolkit.get_tools():
    print(f"Tool name: {tool.name}: {tool.description} \n")


tools = toolkit.get_tools()


llm_with_tools = llm.bind_tools(tools)


# Criar state para o grafo
class GraphState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    route: str
    





def need_use_sql_tools_node(state: GraphState):
    question = state["messages"][-1].content

    prompt = f"""
    Você é um roteador de intenções.
    Responda somente com:
    - direct
    - sql

    Use:
    - direct: se a pergunta puder ser respondida sem banco
    - sql: se precisar consultar banco

    Pergunta: {question}
    """

    response = llm.invoke(prompt)
    route = response.content.strip().lower()

    if route not in {"direct", "sql"}:
        route = "direct"

    return {"route": route}

#Arestas condicionais para o router node

def route_after_router(state: GraphState):
    if state["route"] == "sql":
        return "sql_agent"
    return "direct_answer"

########################################################

def call_model_node(state: GraphState) -> GraphState:
    response = toolkit.run(state["messages"])
    return {"messages": state["messages"] + [ToolMessage(content=response)]}


llm_with_tools = llm.bind_tools(tools)

def sql_agent_node(state: GraphState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

########################################################


def route_after_sql_agent(state: GraphState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"


def direct_answer_node(state: GraphState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}





graph = StateGraph(GraphState)

graph.add_node("router", need_use_sql_tools_node)
graph.add_node("direct_answer", direct_answer_node)
graph.add_node("sql_agent", sql_agent_node)
graph.add_node("tools", ToolNode(tools))


graph.add_edge(START, "router")
graph.add_conditional_edges(
    "router",
    route_after_router,
    {
        "sql_agent": "sql_agent",
        "direct_answer": "direct_answer",
    },
)
graph.add_edge("direct_answer", END)
graph.add_conditional_edges(
    "sql_agent",
    route_after_sql_agent,
    {
        "tools": "tools",
        "end": END,
    },
)
graph.add_edge("tools", "sql_agent")

compiled_graph = graph.compile()

question = "List all tables in my database and count how many records each table has."




if __name__ == "__main__":  
    result = compiled_graph.invoke(
    {
        "messages": [HumanMessage(content=question)],
        "route": "",
    })

    for message in result["messages"]:
        print(type(message).__name__, "->", message.content)
        print("\nResposta final:")
        print(result["messages"][-1].content)
