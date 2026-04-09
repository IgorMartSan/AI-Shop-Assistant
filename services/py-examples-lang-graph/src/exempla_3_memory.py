
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage #https://reference.langchain.com/python/langchain-core

from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.graph.message import Messages
from langchain.chat_models import init_chat_model

from langchain_groq import ChatGroq

import os
from dotenv import load_dotenv

load_dotenv()

#llm = init_chat_model(os.getenv("MODEL_NAME")) # Não precisa passra o key ele ja identifica a chave de ambiente e a biblioteca Groq SDK vai usar a chave automaticamente, mas é importante garantir que a chave esteja definida corretamente no ambiente para evitar erros de autenticação.

llm = init_chat_model(    
    model="allam-2-7b",
    model_provider="groq",
    temperature=0,)



# Não precisa disso  = add_messages
def reducer (a: Messages, b : Messages)-> Messages:
    print(">>> Reducer called with:", a, b)
    return add_messages(a, b)


# 1 - definir o State - estrutura de dados que vai passar e poder ser atualizada pelos nodes. Ela deve conter tudo que os nodes precisam para processar a informação e tomar decisões.
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], reducer]# Aqui estamos usando o Annotated para indicar que a lista de mensagens deve ser processada pelo reducer, que é uma função que recebe duas listas de mensagens e retorna uma nova lista combinando as mensagens. O reducer é usado para garantir que as mensagens sejam acumuladas corretamente à medida que passam pelos nodes do grafo.


# 2 - Definir os Nodes - funções que recebem o state, processam a informação e atualizam o state. Cada node tem uma responsabilidade específica, como atualizar o estado de processamento, gerar resumos, etc.
def node_call_llm(input_state: AgentState) -> None:

    llm_result = AIMessage("Oi como posso ajudar?")
    return llm_result
    #return {'messages': [BaseMessage(content="Hello from LLM!")]}

# 2 - Definir os Nodes - funções que recebem o state, processam a informação e atualizam o state. Cada node tem uma responsabilidade específica, como atualizar o estado de processamento, gerar resumos, etc.
def node_call_llm2(input_state: AgentState) -> AgentState:

    return input_state



# 3 - Definir o StateGraph - onde vamos adicionar os nodes e definir as transições entre eles.
# O argumento context_schema é opcional e pode ser usado para definir um schema para o contexto que será passado entre os nodes. 
# O input_schema e output_schema são usados para validar os dados de entrada e saída dos nodes, garantindo que eles estejam no formato esperado.
builder = StateGraph(AgentState, context_schema=None, input_schema=AgentState, output_schema=AgentState)


# Adicionar os nodes no grafo usando o método add_node, onde o primeiro argumento é o nome do node e o segundo argumento é a função que implementa a lógica do node.
builder.add_node("call_llm", node_call_llm)

builder.add_edge(START, "call_llm")
builder.add_edge("call_llm", END)


if __name__ == "__main__":
    graph_compiled = builder.compile()
    result = graph_compiled.invoke({"messages": []})
    print(">>> Result:", result)