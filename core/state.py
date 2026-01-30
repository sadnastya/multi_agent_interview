from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class InterviewState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    internal_thoughts: Annotated[List[BaseMessage], add_messages]
    metadata: dict 
    is_finished: bool
    final_report: str