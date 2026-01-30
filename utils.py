import json
import os

class InterviewLogger:
    def __init__(self, folder: str = "data"):
        self.file_path = os.path.join(folder, "interview_log.json")
        self.participant_name = ""
        os.makedirs(folder, exist_ok=True)

    def log_session(self, state: dict):
        """Метод вызывается один раз в конце для записи лога с именем."""
        data = {
            "participant_name": self.participant_name, # Техническое поле в начале лога
            "final_feedback": state.get("final_report"),
            "history": [
                {"role": m.type, "content": m.content} for m in state.get("messages", [])
            ]
        }
        
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)