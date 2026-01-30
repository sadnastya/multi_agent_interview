from enum import Enum
from typing import List, Optional, Annotated, TypedDict
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class UserIntent(str, Enum):
    GREETING = "greeting"
    ANSWER = "answer"
    QUESTION = "question"
    NONSENSE = "nonsense"
    COMMAND = "command"
    IDK = "i_dont_know"

class ReflectionOutput(BaseModel):
    """Выходные данные Стратега"""
    intent: UserIntent
    is_correct: bool
    analysis: str
    strategy: str
    instruction: str
    stop_interview: bool

class HardSkillItem(BaseModel):
    topic: str
    status: str
    correct_answer: Optional[str] = None

class FinalFeedback(BaseModel):
    """Выходные данные Аналитика"""
    grade: str = Field(description="Junior / Middle / Senior")
    hiring_recommendation: str = Field(description="Hire / No Hire / Strong Hire")
    confidence_score: int
    hard_skills_analysis: List[HardSkillItem]
    clarity: str
    honesty: str
    engagement: str
    roadmap: List[str]

class InterviewState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    internal_thoughts: str
    thoughts_history: List[str]
    next_instruction: str
    is_finished: bool
    final_report: Optional[dict]
