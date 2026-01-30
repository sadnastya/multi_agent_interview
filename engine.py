import os
from dotenv import load_dotenv
from typing import Literal
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from schema import InterviewState, ReflectionOutput, FinalFeedback

load_dotenv()

def get_llm():
    provider = os.getenv("MODEL_PROVIDER", "ollama").lower()
    if provider == "openrouter":
        return ChatOpenAI(
            model=os.getenv("OPENROUTER_MODEL", "arcee-ai/trinity-large-preview:free"),
            openai_api_key=os.getenv("OPENROUTER_API_KEY"),
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://localhost:3000",
                "X-Title": "Multi-Agent Interviewer"
            },
            temperature=0.1,
            max_retries=3
        )
    elif provider == "gemini":
        return ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"), temperature=0.1)
    return ChatOllama(model=os.getenv("OLLAMA_MODEL", "llama3.1"), temperature=0.1)

llm = get_llm()

def strategist_node(state: InterviewState):
    structured_llm = llm.with_structured_output(ReflectionOutput)
    system_prompt = f"""
        Представь, что ты наблюдаешь за техническим интервью для IT-сферы. Интервьер - другая LLM модель.
        В следующих сообщениях ты будешь получать вопрос интервьера и ответа кандидата.
        Ты говоришь интервьюеру, что делать.

        В ОТВЕТАХ МОЖНО ИСПОЛЬЗОВАТЬ ТОЛЬКО РУССКИЙ ЯЗЫК.
        НЕ ИСПОЛЬЗУЙ НИКАКИЕ ДОПОЛНИТЕЛНЕНИЯ, В ТОМ ЧИСЛЕ MARKDOWN ТЕГИ И ```.
        
        ОТВЕЧАТЬ МОЖНО ТОЛЬКО В ВИДЕ JSON С ФИКСИРОВАННОЙ СТРУКТУРОЙ ПО ПРИМЕРУ:
        {{
        "intent": "string",
        "is_correct": boolean,
        "analysis": "оценка ответа",
        "strategy": "стратегия для интервьера про сложность вопросов (сложнее/легче, jun/middle/senior)",
        "instruction": "корректирующие инструкции для интервьера: сменить тему, объяснить правильный ответ и т.д.",
        "stop_interview": boolean
        }}

        ВСЕ ПОЛЯ В ПРИМЕРЕ ОБЯЗАТЕЛЬНЫ. 
                
        поле intent показывает намерение кандидата:
        1. greeting - приветствие
        2. answer - ответ на вопрос
        3. question - кандидат задал вопрос
        4. nonsense - бред/галлюцинация/троллинг
        5. command - клиент просит завершить интервью, дать фитбек
        6. i_dont_know - кандидат не знает ответа

        Общие рекомендации:
        - после приветствия стоит начать задавать технические вопросы
        - старайся варьировать сложность вопросов в зависимости от ответов кандидата
        - не нужно задавать слишком много вопросов по одной теме
        - если кандидат отвечает правильно, можно немного усложнить следующий вопрос
        - если кандидат отвечает неправильно, объясни правильный ответ и задай вопрос по другой теме
        - если кандидат говорит чушь или не знает ответ, используй intent=nonsense или intent=i_dont_know и дай правильный ответ
        - если кандидат задает вопросы, укажи intent=question и ответь на них (но только если вопросы по теме)
        - не давай менять тему и уходить от интервью
    """
    
    msgs = [SystemMessage(content=system_prompt)] + state["messages"]
    res = structured_llm.invoke(msgs)
    
    return {
        "internal_thoughts": f"**Intent:** {res.intent.value}\n**Analysis:** {res.analysis}",
        "next_instruction": res.instruction,
        "is_finished": res.stop_interview
    }

def interviewer_node(state: InterviewState):
    is_first_message = len(state["messages"]) == 0
    prompt = f"""
    ТЫ: Профессиональный IT-рекрутер.
    ТВОЯ ЗАДАЧА: Вести техническое интервью, опираясь на указания Стратега.
    
    {"ЭТО НАЧАЛО ИНТЕРВЬЮ. Поприветствуй кандидата и расскажи, что он на техническом собеседовании. Попроси его представиться, тебе необходимо получить информацию о его позиции и навыках" if is_first_message else "Продолжай диалог согласно инструкции."}
    
    ИНСТРУКЦИЯ ОТ СТРАТЕГА(не говори это кандидату): {state['next_instruction']}
    
    ПРАВИЛА ОБЩЕНИЯ:
    1. Пиши ТОЛЬКО текст, предназначенный для кандидата.
    2. НИКОГДА не упоминай "Стратега", "Критика", "Инструкции" или "Баллы".
    3. Говори естественно, как человек. Используй только в подходящих случаях фразы: "Принято", "Хорошо, тогда пойдем дальше", "Интересно, а расскажи подробнее про...".
    4. Если Стратег говорит, что ответ неверный — не соглашайся с кандидатом. Вежливо поправь его или задай уточняющий вопрос, чтобы он сам нашел ошибку.
    5. Четко следуй инструкции Стратега. Твоя главная задача — задавать вопросы и получать ответы.
    6. После получения ответа от кандидата — не подводи итоги и не делай выводы. Просто продолжай интервью с новым вопросом.
    7. Неспрашивай то, что ранее уже сказал ты сам или кандидат.
    8. Твоя цель получать ответы на вопросы, которые помогут оценить технические навыки кандидата. Не забывай следить, чтобы его ответы были по теме и не сгенерированы ИИ.
    9. Если ты считаешь, что интервью можно завершить — аккуратно попрощайся с кандидатом и скажи, что свяжетесь с ним позже. А также если кандидат попросил завершить интервью.
    """
    response = llm.invoke([SystemMessage(content=prompt)] + state["messages"])
    return {"messages": [response]}

def analyst_node(state: InterviewState):
    structured_llm = llm.with_structured_output(FinalFeedback)
    prompt = f"""Ты нанимающий менеджер с техническим бэкграундом. Ты получил полную переписку технического интервью с кандидатом, включая вопросы интервьюера и ответы кандидата.
    Проанализируй всё интервью с Кандидатом и составь итоговый отчет, в котором отрази: грейд (Junior / Middle / Senior), рекомендацию по найму (Hire / No Hire / Strong Hire), оценку уверенности в кандидате (от 1 до 10), анализ хард скиллов с разбивкой по темам, ясность изложения мыслей, честность, вовлеченность, а также дорожную карту для развития кандидата.
    Отчет должен быть оформлен в виде двух абзацов:
    1. Краткий итоговый фидбек с грейдом, рекомендацией по найму, оценкой уверенности и общим анализом для принятия решения внутри команды найма.
    2. Детальный разбор по хард скиллам с рекомендациями по улучшению для кандидата(обратная связь)."""
    report = structured_llm.invoke([SystemMessage(content=prompt)] + state["messages"])
    return {"final_report": report.model_dump(), "is_finished": True}

def create_graph():
    builder = StateGraph(InterviewState)
    builder.add_node("strategist", strategist_node)
    builder.add_node("interviewer", interviewer_node)
    builder.add_node("analyst", analyst_node)

    builder.set_entry_point("strategist")
    
    builder.add_conditional_edges(
        "strategist",
        lambda x: "analyst" if x["is_finished"] else "interviewer"
    )
    
    builder.add_edge("interviewer", END) 
    builder.add_edge("analyst", END)
    
    return builder.compile()