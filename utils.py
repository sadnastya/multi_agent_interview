import json
import os

class InterviewLogger:
    def __init__(self, folder: str = "data"):
        self.file_path = os.path.join(folder, "interview_log.json")
        self.participant_name = "Садовая Анастасия Романовна"
        os.makedirs(folder, exist_ok=True)

    def log_session(self, state: dict):
        report = state.get("final_report", {})
        
        internal_feedback = (
            f"ИТОГОВЫЙ ГРЕЙД: {report.get('grade', 'N/A')}. "
            f"РЕКОМЕНДАЦИЯ: {report.get('hiring_recommendation', 'N/A')}. "
            f"УВЕРЕННОСТЬ: {report.get('confidence_score', 0)}/10. "
            f"АНАЛИЗ: {report.get('clarity', 'N/A')}, честность: {report.get('honesty', 'N/A')}, "
            f"вовлеченность: {report.get('engagement', 'N/A')}."
        )

        skills_list = []
        if report.get("hard_skills_analysis"):
            for skill in report["hard_skills_analysis"]:
                status = "освоено" if skill.get("status") == "Passed" else "нужно подтянуть"
                comment = f" ({skill.get('correct_answer')})" if skill.get("correct_answer") else ""
                skills_list.append(f"{skill.get('topic')} — {status}{comment}")
        
        skills_feedback = "Разбор навыков: " + "; ".join(skills_list) if skills_list else "Технические навыки не оценены."
        
        roadmap_text = ""
        if report.get("roadmap"):
            roadmap_text = " Рекомендации по обучению: " + ", ".join(report["roadmap"]) + "."

        candidate_feedback = f"{skills_feedback}{roadmap_text}"

        full_feedback_text = f"{internal_feedback}\n\n{candidate_feedback}"

        turns = []
        messages = state.get("messages", [])
        thoughts_history = state.get("thoughts_history", [])

        turn_id = 1
        for i in range(0, len(messages) - 1, 2):
            if i + 1 < len(messages):
                ai_msg = messages[i].content
                user_msg = messages[i+1].content
                thoughts = thoughts_history[turn_id-1] if turn_id-1 < len(thoughts_history) else ""
                
                turns.append({
                    "turn_id": turn_id,
                    "agent_visible_message": ai_msg,
                    "user_message": user_msg,
                    "internal_thoughts": thoughts
                })
                turn_id += 1

        data = {
            "participant_name": self.participant_name,
            "turns": turns,
            "final_feedback": full_feedback_text
        }
        
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)