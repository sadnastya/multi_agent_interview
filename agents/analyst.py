import json
from core.llm_factory import get_llm
from core.models import FinalFeedback

class Analyst:
    def __init__(self):
        self.llm = get_llm()

    def generate_final_report(self, participant_name: str, turns: list) -> dict:
        # Превращаем историю в текст для анализа
        full_history = json.dumps(turns, ensure_ascii=False, indent=2)
        
        prompt = f"""
        Ты - Senior Engineering Manager. Твоя задача: проанализировать логи интервью с {participant_name}.
        
        Используй 'internal_thoughts' для выявления скрытых ошибок, которые рекрутер мог не озвучить.
        
        КРИТЕРИИ ДЛЯ ROADMAP:
        На основе ❌ Knowledge Gaps сформируй список конкретных тем для изучения.
        
        ДАННЫЕ ИНТЕРВЬЮ:
        {full_history}
        """
        
        structured_llm = self.llm.with_structured_output(FinalFeedback)
        report = structured_llm.invoke(prompt)
        return report.model_dump()