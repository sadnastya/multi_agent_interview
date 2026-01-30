import json
from langchain_core.messages import BaseMessage
from core.llm_factory import get_llm
from core.models import FinalFeedback

class Analyst:
    def __init__(self):
        self.llm = get_llm()

    def generate_final_report(self, participant_name: str, turns: list) -> dict:
        # ПРЕОБРАЗОВАНИЕ: Превращаем объекты сообщений в JSON-совместимый формат
        serializable_turns = []
        for turn in turns:
            if isinstance(turn, BaseMessage):
                # Если это объект сообщения LangChain
                serializable_turns.append({
                    "role": turn.type, 
                    "content": turn.content
                })
            elif isinstance(turn, dict):
                # Если это уже словарь из лога
                serializable_turns.append(turn)
            else:
                # На случай других типов данных
                serializable_turns.append(str(turn))

        full_history = json.dumps(serializable_turns, ensure_ascii=False, indent=2)
        
        prompt = f"""
        Ты - Senior Engineering Manager. Твоя задача: проанализировать логи интервью с {participant_name}.
        
        Используй историю диалога для выявления сильных и слабых сторон кандидата. А также для составления подробного фидбэка по следующим пунктам:
        1. Вердикт: Определи уровень (Junior / Middle / Senior), рекомендацию по найму (Hire / No Hire / Strong Hire) и уверенность в решении (0-100).
        2. Hard Skills: Проанализируй технические навыки, выдели темы, в которых кандидат показал себя хорошо, и темы с пробелами
        
        ДАННЫЕ ИНТЕРВЬЮ:
        {full_history}
        """
        
        structured_llm = self.llm.with_structured_output(FinalFeedback, method="json_mode")
        report = structured_llm.invoke(prompt)
        return report.model_dump()