# backend/rules.py
import re

# Red-flag keywords for risky behavior
RED_FLAGS = {
    "gamble": 35,
    "casino": 35,
    "betting": 35,
    "urgent": 15,
    "emergency": 20,
    "owe money": 25,
    "loan shark": 40,
    "crypto": 30,
    "investment guaranteed": 50,
    "vacation": 25,
    "holiday": 25,
    "shopping": 20,
    "luxury": 20,
}

def detect_red_flags(text):
    text_lower = text.lower()
    score = 0
    flags_found = []

    for keyword, risk in RED_FLAGS.items():
        if keyword in text_lower:
            score += risk
            flags_found.append(keyword)

    return score, flags_found
