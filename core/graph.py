from langgraph.graph import StateGraph, END
from agents.nodes import strategist_node, interviewer_node
from core.models import AgentState

def create_graph():
    builder = StateGraph(AgentState)
    builder.add_node("strategist", strategist_node)
    builder.add_node("interviewer", interviewer_node)
    builder.set_entry_point("strategist")
    builder.add_edge("strategist", "interviewer")
    builder.add_edge("interviewer", END)
    return builder.compile()