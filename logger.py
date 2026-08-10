from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "chat_log.txt")

def log_chat(question, answer):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{time}] Q: {question}\n")
        f.write(f"[{time}] A: {answer}\n\n")

def load_old_chats():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return f.read()[-1000:]
    except:
        return "No previous chats"