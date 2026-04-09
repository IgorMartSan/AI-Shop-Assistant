
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import HumanMessage
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os

load_dotenv()

llm = init_chat_model(    
    model="allam-2-7b",
    model_provider="groq",
    temperature=0,)


#3 - Definir o StateGraph - onde vamos adicionar os nodes e definir as transições entre eles.

class GraphState(BaseModel):
    input: str
    output: str


# 4 - Criar o grafo e adicionar os nodes e as transições entre eles.

def node_call_llm(state):
    input_message = state.input
    response = llm.invoke([HumanMessage(content=input_message)])
    return GraphState(input=input_message, output=response.content)

# 5 Criando o graph
graph = StateGraph(GraphState)
graph.add_node("call_llm", node_call_llm)

graph.set_entry_point("call_llm")
graph.set_finish_point("call_llm")

# 6 - Compilar o grafo
compiled_graph = graph.compile()

if __name__ == "__main__":
    # 7 - Invocar o grafo com um estado inicial
    result = compiled_graph.invoke(GraphState(input="Olá, como vai?", output=""))
    print("Graph result:", result)

    #Visualizar o grafo
    drawable = compiled_graph.get_graph()
    # Mermaid texto
    print(drawable.draw_mermaid())

    png_data = drawable.draw_mermaid_png()
    with open("./graph_visualization.png", "wb") as f:
        f.write(png_data)
  