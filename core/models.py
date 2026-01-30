from enum import Enum
from typing import List, TypedDict, Annotated, Optional
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

class UserIntent(str, Enum):
    GREETING = "greeting"     # Приветствие
    ANSWER = "answer"         # Ответ на вопрос
    QUESTION = "question"     # Кандидат сам задает вопрос
    NONSENSE = "nonsense"     # Бред/Галлюцинация/Троллинг
    COMMAND = "command"       # Команда (стоп, фидбэк)
    IDK = "i_dont_know"        # Не знаю/Не уверен

class ReflectionOutput(BaseModel):
    intent: UserIntent = Field(default=UserIntent.ANSWER)
    is_correct: bool = Field(default=True)
    analysis: str = Field(default="Анализ выполнен.")
    strategy: str = Field(default="Продолжаем по плану.")
    instruction: str = Field(description="Инструкция для Рекрутера")
    stop_interview: bool = Field(default=False)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "История диалога"]
    internal_thoughts: str
    next_instruction: str
    turn_id: int
    is_finished: bool


class HardSkillItem(BaseModel):
    topic: str
    status: str = Field(description="Корректно / Пробел в знаниях")
    correct_answer: Optional[str] = Field(None, description="Правильный ответ, если кандидат ошибся")

class FinalFeedback(BaseModel):
    # А. Вердикт
    grade: str = Field(description="Junior / Middle / Senior")
    hiring_recommendation: str = Field(description="Hire / No Hire / Strong Hire")
    confidence_score: int = Field(ge=0, le=100)
    
    # Б. Hard Skills
    hard_skills_analysis: List[HardSkillItem]
    
    # В. Soft Skills
    clarity: str
    honesty: str
    engagement: str
    
    # Г. Roadmap
    roadmap: List[str]