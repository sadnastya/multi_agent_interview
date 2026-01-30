import chainlit as cl
from langchain_core.messages import HumanMessage
from engine import create_graph
from utils import InterviewLogger

graph = create_graph()
logger = InterviewLogger()

@cl.on_chat_start
async def start():
    state = {
        "messages": [],
        "participant_name": "Кандидат",
        "internal_thoughts": "Начало сессии",
        "next_instruction": "Начни интервью",
        "is_finished": False,
        "final_report": None
    }
    cl.user_session.set("state", state)
    
    # Первый запуск графа для приветствия
    res = await cl.make_async(graph.invoke)(state)
    cl.user_session.set("state", res)
    await cl.Message(content=res["messages"][-1].content).send()

@cl.on_message
async def main(message: cl.Message):
    state = cl.user_session.get("state")
    if state.get("final_report"): return

    # Добавляем сообщение пользователя
    state["messages"].append(HumanMessage(content=message.content))

    async with cl.Step(name="Анализ ответа") as step:
        state = await cl.make_async(graph.invoke)(state)
        step.output = state["internal_thoughts"]
    
    cl.user_session.set("state", state)
    
    # Отправляем ответ Интервьюера (последнее сообщение в списке)
    await cl.Message(content=state["messages"][-1].content).send()

    if state.get("final_report"):
        await cl.Message(content="**Интервью завершено. Отчет сформирован.**").send()
        logger.log_session(state)