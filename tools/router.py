def decide_tool(question):
    q = question.lower()

    # FIX: Check for return address FIRST - must go to search
    if "return address" in q or "shipping" in q:
        return "search"

    # Then check refund - removed "return" alone, it's too broad
    if any(w in q for w in ["refund", "money back", "funds reversed"]):
        return "refund"
    
    if any(w in q for w in ["mission", "about you", "who are you"]):
        return "mission"
    
    if any(w in q for w in ["privacy", "my data"]):
        return "privacy"
    
    if any(w in q for w in ["+", "-", "*", "/"]):
        return "calculator"
    
    return "search" # default RAG search