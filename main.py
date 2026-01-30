import chainlit as cl
import json
from langchain_core.messages import HumanMessage
from core.graph import create_graph
from utils.logger import InterviewLogger
from agents.analyst import Analyst

flow = create_graph()

@cl.on_chat_start
async def start():
    logger = InterviewLogger()
    
    state = {
        "participant_name": "Неизвестно",
        "messages": [],
        "internal_thoughts": "Инициализация",
        "next_instruction": "Поприветствуй кандидата и узнай его имя.",
        "turn_id": 1,
        "is_finished": False
    }
    
    cl.user_session.set("state", state)
    cl.user_session.set("logger", logger)

    async with cl.Step(name="Strategist"):
        output = await cl.make_async(flow.invoke)(state)
        state.update(output)
    
    ai_reply = state["messages"][-1].content
    await cl.Message(content=ai_reply).send()

@cl.on_message
async def main(message: cl.Message):
    state = cl.user_session.get("state")
    logger = cl.user_session.get("logger")
    
    if state["is_finished"]:
        return

    user_input = message.content
    state["messages"].append(HumanMessage(content=user_input))

    async with cl.Step(name="Thinking Process") as step:
        output = await cl.make_async(flow.invoke)(state)
        step.output = output.get("internal_thoughts", "Анализ...")
        state.update(output)

    if output.get("participant_name") and output["participant_name"] != "Неизвестно":
        logger.update_participant_name(output["participant_name"])

    ai_reply = state["messages"][-1].content
    logger.log_turn(state["turn_id"], ai_reply, user_input, state["internal_thoughts"])
    
    state["turn_id"] += 1
    await cl.Message(content=ai_reply).send()

    if state["is_finished"]:
        await cl.Message(content="\n**Интервью завершено. Подготовка отчета...**").send()
        
        async with cl.Step(name="Final Analysis"):
            analyst = Analyst()
            final_report = await cl.make_async(analyst.generate_final_report)(
                state["participant_name"], 
                state["messages"]
            )
            logger.finalize_log(final_report)
        
        await cl.Message(content=f"Фидбек для {state['participant_name']} сохранен в interview_log.json").send()