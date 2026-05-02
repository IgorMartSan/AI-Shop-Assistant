from typing import Annotated
from pydantic import BaseModel
from dotenv import load_dotenv

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage

load_dotenv()


class SomaInput(BaseModel):
    a: int
    b: int


@tool(args_schema=SomaInput)
def somar(a: int, b: int) -> int:
    """Soma dois números."""
    return a + b


tools = [somar]


class GraphState(BaseModel):
    messages: Annotated[list[BaseMessage], 3]


llm = init_chat_model(
    model="qwen/qwen3-32b",
    model_provider="groq",
    temperature=0,
)

llm_with_tools = llm.bind_tools(tools)


def call_model(state: GraphState):
    response = llm_with_tools.invoke(state.messages)
    return {"messages": [response]}


def should_continue(state: GraphState):
    last_message = state.messages[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return "end"


graph = StateGraph(GraphState)

graph.add_node("call_model", call_model)
graph.add_node("tools", ToolNode(tools))

graph.set_entry_point("call_model")

graph.add_conditional_edges(
    "call_model",
    should_continue,
    {
        "tools": "tools",
        "end": "__end__",
    },
)

graph.add_edge("tools", "call_model")

compiled_graph = graph.compile()


if __name__ == "__main__":
    result = compiled_graph.invoke(
        {
            "messages": [HumanMessage(content="Quanto é 2 + 3?")]
        }
    )

    messages = result["messages"]

    for msg in messages:
        print("TIPO:", type(msg).__name__)
        print("CONTENT:", msg.content)
        if hasattr(msg, "tool_calls"):
            print("TOOL_CALLS:", msg.tool_calls)
        print("-" * 50)

    last_message = messages[-1]
    print("RESPOSTA FINAL DA LLM:")
    print(last_message.content)