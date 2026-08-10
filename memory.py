history = []

def add_memory(question, answer):
    history.append(f"Q: {question}\nA: {answer}")

def get_memory():
    return "\n".join(history[-4:]) # last 4 conversations
