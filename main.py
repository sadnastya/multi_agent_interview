from langchain_core.messages import HumanMessage
from core.graph import create_graph
from utils.logger import InterviewLogger
from agents.analyst import Analyst
import json

def main():
    logger = InterviewLogger()
    flow = create_graph()
    
    state = {
        "messages": [],
        "internal_thoughts": "Init",
        "next_instruction": "Начни интервью: поздоровайся и спроси кандидата о его опыте.",
        "turn_id": 1,
        "is_finished": False
    }

    while not state["is_finished"]:
        output = flow.invoke(state)
        state.update(output)
        
        reply = state["messages"][-1].content
        print(f"\nAI: {reply}")
        
        user_in = input("You: ")
        logger.log_turn(state["turn_id"], reply, user_in, state["internal_thoughts"])
        
        state["messages"].append(HumanMessage(content=user_in))
        state["turn_id"] += 1
    
    if state["is_finished"]:
        print("\nAI: Интервью завершено. Анализирую ваши ответы и готовлю отчет...")
        with open(logger.file_path, 'r', encoding='utf-8') as f:
            log_content = json.load(f)
        
        analyst = Analyst()
        final_report = analyst.generate_final_report(
            state["participant_name"], 
            log_content["turns"]
        )
    
    # 3. Сохраняем результат в лог
    logger.finalize_log(final_report)
    
    print(f"--- Фидбек для {state['participant_name']} успешно сформирован в {logger.file_path} ---")

if __name__ == "__main__":
    main()