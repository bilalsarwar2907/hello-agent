# main.py - CLI - Only UI, no logic
from agent import ask_agent
from logger import load_old_chats
from memory import history

# Load old chats once (from your old code)
old = load_old_chats()
if old != "No previous chats" and len(old) > 10:
    print(f"Loaded previous chats")
    history.append(f"Previous session:\n{old}")

# ===== SWITCH - This is your switch =====
USE_AI_ROUTER = True  # Change to True to use AI router
# ========================================

print(f"Agent started [Router Mode: {'AI' if USE_AI_ROUTER else 'Keyword'}]. Type 'exit' to quit.")

while True:  # Fixed your while False bug here
    question = input("\nAsk (or type 'exit'): ")
    if question.lower() == "exit":
        break

    result = ask_agent(question, use_ai_router=USE_AI_ROUTER)
    
    print(f"[{result['tool']}]")
    print(f"Answer: {result['answer']}")