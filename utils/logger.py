import json
import os

class InterviewLogger:
    def __init__(self, folder: str = "data"):
        self.folder = folder
        self.file_path = os.path.join(folder, "interview_log.json")
        self.data = {"participant_name": "Садовая Анастасия Романовна", "turns": [], "final_feedback": ""}
        
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        self._initialize_file()

    def _initialize_file(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def finalize_log(self, feedback_data: dict):
        """Записывает структурированный отчет в поле final_feedback."""
        with open(self.file_path, 'r+', encoding='utf-8') as f:
            current_data = json.load(f)
            current_data["final_feedback"] = feedback_data
            f.seek(0)
            json.dump(current_data, f, ensure_ascii=False, indent=2)
            f.truncate()
    

    def log_turn(self, turn_id: int, agent_msg: str, user_msg: str, thoughts: str):
        with open(self.file_path, 'r+', encoding='utf-8') as f:
            current_data = json.load(f)
            current_data["turns"].append({
                "turn_id": turn_id,
                "agent_visible_message": agent_msg,
                "user_message": user_msg,
                "internal_thoughts": thoughts
            })
            f.seek(0)
            json.dump(current_data, f, ensure_ascii=False, indent=2)
            f.truncate()