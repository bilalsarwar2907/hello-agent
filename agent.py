# agent.py - The Brain - ONE file controls everything
from groq import Groq
from dotenv import load_dotenv
import os
from tools.router import decide_tool
from rag import search
from tools.calculator import get_refund_policy, get_mission_statement, get_privacy_policy
from memory import add_memory, get_memory
from logger import log_chat
from vector_db import search_db as search

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "prompts", "system.txt"), "r", encoding="utf-8") as f:
    SYSTEM_TEMPLATE = f.read()

def ask_agent(question: str, use_ai_router: bool = False) -> dict:
    q_lower = question.lower()
    if "ignore previous" in q_lower or "ceo phone" in q_lower:
        return {"answer": "Blocked: safety check", "tool": "blocked", "context": ""}

    if use_ai_router:
        router_prompt = f"You are router. Reply ONE word only: refund, mission, privacy, calculator, or search\nQuestion: {question}\nWord:"
        try:
            r = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": router_prompt}]
            )
            tool = r.choices[0].message.content.strip().lower()
        except:
            tool = decide_tool(question)
    else:
        tool = decide_tool(question)

    if tool == "refund":
        doc = get_refund_policy()
    elif tool == "mission":
        doc = get_mission_statement()
    elif tool == "privacy":
        doc = get_privacy_policy()
    elif tool == "calculator":
        try:
            from tools.calculator import calculator as calc_fn
            result = calc_fn(question)
        except:
            try:
                from tools.calculator import calculate as calc_fn
                result = calc_fn(question)
            except:
                result = "could not calculate"
        doc = f"Calculator result for {question} is {result}. Use this to answer."
    else:
        doc = search(question)
        tool = "search"

    full_context = f"History:\n{get_memory()}\n\nDocs:\n{doc}"
    final_prompt = SYSTEM_TEMPLATE.format(context=full_context, question=question)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": final_prompt}]
    )
    answer = response.choices[0].message.content

    add_memory(question, answer)
    log_chat(question, answer)

    return {"answer": answer, "tool": tool, "context": doc}