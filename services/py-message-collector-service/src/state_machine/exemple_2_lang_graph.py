from typing import TypedDict
from langgraph.graph import StateGraph

# - State - estrutura de dados que vai passar e poder ser atualizada pelos nodes. Ela deve conter tudo que os nodes precisam para processar a informação e tomar decisões.
class State(TypedDict):
    user_id: str
    massages: list[str]

# 2 - Nodes - funções que recebem o state, processam a informação e atualizam o state. Cada node tem uma responsabilidade específica, como atualizar o estado de processamento, gerar resumos, etc.
def node_a(input_state: State) -> None:
    # processa state e atualiza informações
    concat_msgs  = " ".join(input_state["massages"])
    input_state["massages"] = [concat_msgs]  # Exemplo de atualização do state
    print(f"Node A processou as mensagens para o user_id={input_state['user_id']}")
    return input_state



def node_b(input_state: State) -> None:
    # processa state e atualiza informações
    print(f"Node B recebeu as mensagens processadas: {input_state['massages']} para o user_id={input_state['user_id']}")
    return input_state

# 3 - State Machine -

builder = StateGraph(State, context_schema=None, input_schema=State, output_schema=State)

builder.add_node("A", node_a)
builder.add_node("B", node_b)

#Conectar as edges ou arestas entre os nodes, definindo a lógica de transição
builder.add_edge("__start__", "A")
builder.add_edge("A", "B")
builder.add_edge("B", "__end__")  # Exemplo de transição para o final


graph_compiled = builder.compile()


graph_compiled.invoke({ "user_id": "123", "massages": ["Ola", "Tudo bem ?"] })