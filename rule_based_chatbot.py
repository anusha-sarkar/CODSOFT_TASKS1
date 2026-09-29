

import random
import re
from datetime import datetime


# ---------------------------------------------------------------------------
# 1. RULES: (regex pattern, list of possible responses)
#    The first rule whose pattern matches the input wins, so order matters:
#    put specific rules before general ones.
# ---------------------------------------------------------------------------
RULES = [
    (r"\b(hi|hello|hey|hola|namaste)\b",
     ["Hello! How can I help you today?",
      "Hi there! What would you like to talk about?",
      "Hey! Nice to see you."]),

    (r"\bhow are you\b|\bhow('s| is) it going\b",
     ["I'm doing great, thanks for asking! How about you?",
      "All systems running smoothly. How are you?"]),

    (r"\b(i am|i'm|im) (good|fine|great|okay|ok|well)\b",
     ["Glad to hear that!",
      "That's great! What can I do for you?"]),

    (r"\b(i am|i'm|im) (sad|tired|bored|stressed|upset)\b",
     ["I'm sorry to hear that. Want to talk about it?",
      "That sounds tough. Taking a short break might help."]),

    (r"\bwhat('s| is) your name\b|\bwho are you\b",
     ["I'm PyBot, a simple rule-based chatbot.",
      "You can call me PyBot!"]),

    (r"\bwhat can you do\b|\bhelp\b",
     ["I can chat, tell you the time or date, tell a joke, "
      "and remember your name. Try asking me something!"]),

    (r"\b(time)\b",
     ["__TIME__"]),          # special token, handled in code below

    (r"\b(date|today|day)\b",
     ["__DATE__"]),

    (r"\bjoke\b",
     ["Why do programmers prefer dark mode? Because light attracts bugs!",
      "Why did the developer go broke? He used up all his cache.",
      "There are 10 kinds of people: those who understand binary and those who don't."]),

    (r"\b(python|java|c\+\+|programming|coding)\b",
     ["Programming is a great skill! Which language are you learning?",
      "Python is a solid choice for beginners and for AI/ML."]),

    (r"\b(ai|machine learning|ml|nlp)\b",
     ["AI is fascinating! This bot is rule-based, while modern NLP uses "
      "machine learning models trained on lots of text."]),

    (r"\b(thanks|thank you|thx)\b",
     ["You're welcome!", "Happy to help!", "Anytime!"]),
]

EXIT_PATTERN = r"\b(bye|goodbye|exit|quit|see you)\b"

FALLBACK_RESPONSES = [
    "Sorry, I didn't understand that. Could you rephrase?",
    "Hmm, I'm not sure how to respond to that. Try asking for 'help'.",
    "I'm a simple bot, so that one is beyond me. Ask me something else!",
]


# ---------------------------------------------------------------------------
# 2. PREPROCESSING
# ---------------------------------------------------------------------------
def preprocess(text: str) -> str:
    """Lowercase, remove punctuation (keeping apostrophes), trim spaces."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s'+\-*/.]", "", text)
    return re.sub(r"\s+", " ", text)


# ---------------------------------------------------------------------------
# 3. RESPONSE LOGIC
# ---------------------------------------------------------------------------
def get_response(user_input: str, state: dict) -> str:
    """Return a reply for the user's input. `state` stores conversation memory."""
    text = preprocess(user_input)

    # Empty input
    if not text:
        return "Say something and I'll respond!"

    # Rule: user tells their name  ("my name is Anusha" / "call me Anusha")
    name_match = re.search(r"(?:my name is|call me|i am called)\s+([a-z]+)", text)
    if name_match:
        state["name"] = name_match.group(1).capitalize()
        return f"Nice to meet you, {state['name']}!"

    # Rule: user asks for their name
    if re.search(r"\bwhat('s| is) my name\b|\bdo you know my name\b", text):
        if state.get("name"):
            return f"Your name is {state['name']}."
        return "I don't know your name yet. Tell me with 'my name is ...'."

    # Simple arithmetic:  "what is 5 + 3"
    math_match = re.search(r"(-?\d+(?:\.\d+)?)\s*([+\-*/x])\s*(-?\d+(?:\.\d+)?)", text)
    if math_match:
        a, op, b = float(math_match[1]), math_match[2], float(math_match[3])
        if op == "+":
            result = a + b
        elif op == "-":
            result = a - b
        elif op in ("*", "x"):
            result = a * b
        else:
            if b == 0:
                return "I can't divide by zero!"
            result = a / b
        return f"The answer is {result:g}."

    # Generic rule table
    for pattern, responses in RULES:
        if re.search(pattern, text):
            reply = random.choice(responses)
            if reply == "__TIME__":
                return f"The current time is {datetime.now().strftime('%I:%M %p')}."
            if reply == "__DATE__":
                return f"Today is {datetime.now().strftime('%A, %d %B %Y')}."
            # Personalise greetings if we know the name
            if state.get("name") and pattern.startswith(r"\b(hi|hello"):
                return f"Hello, {state['name']}! How can I help you today?"
            return reply

    # Nothing matched
    return random.choice(FALLBACK_RESPONSES)


def is_exit(user_input: str) -> bool:
    return re.search(EXIT_PATTERN, preprocess(user_input)) is not None


# ---------------------------------------------------------------------------
# 4. MAIN CONVERSATION LOOP
# ---------------------------------------------------------------------------
def main():
    state = {}
    print("PyBot: Hi! I'm PyBot. Type 'bye' to exit.\n")

    while True:
        try:
            user_input = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nPyBot: Goodbye!")
            break

        if is_exit(user_input):
            name = f", {state['name']}" if state.get("name") else ""
            print(f"PyBot: Goodbye{name}! Have a great day.")
            break

        print(f"PyBot: {get_response(user_input, state)}\n")


if __name__ == "__main__":
    main()
