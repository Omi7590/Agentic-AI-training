# RTI Mitra - llm.py
# Groq provider wrapper for the RTI Mitra chat endpoint.
# Reads GROQ_API_KEY from .env (never committed).

import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "qwen/qwen3.8-27b"

SYSTEM_PROMPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "prompts", "system_prompt.txt"
)

def load_system_prompt() -> str:
    with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()

def chat(user_message: str, system_prompt: str | None = None) -> dict:
    """
    Send a message to the Groq LLM and return a structured response.
    Returns: { answer, confidence, follow_up }
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set. Add it to your .env file.")

    client = Groq(api_key=GROQ_API_KEY)

    if system_prompt is None:
        system_prompt = load_system_prompt()

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.3,
        max_tokens=1024,
    )

    answer = response.choices[0].message.content.strip()

    # Simple confidence heuristic based on response length and keywords
    low_confidence_phrases = [
        "i don't know", "i am not sure", "please check", "unclear", "not certain"
    ]
    is_low = any(phrase in answer.lower() for phrase in low_confidence_phrases)
    confidence = "low" if is_low else "high"

    # Generate a follow-up suggestion
    follow_up = generate_follow_up(user_message)

    return {
        "answer": answer,
        "confidence": confidence,
        "follow_up": follow_up,
    }

def generate_follow_up(user_message: str) -> str:
    """Suggest a relevant follow-up question based on keywords in the user message."""
    msg = user_message.lower()
    if "fee" in msg or "cost" in msg:
        return "Would you like to know if you qualify for a BPL fee exemption?"
    elif "deadline" in msg or "days" in msg or "reply" in msg:
        return "Would you like to know what to do if the PIO does not reply in time?"
    elif "draft" in msg or "application" in msg or "write" in msg:
        return "Would you like to know the reply deadline and first appeal process after submitting?"
    elif "appeal" in msg:
        return "Would you like to know how to file a second appeal with the State Information Commission?"
    elif "exempt" in msg or "section 8" in msg:
        return "Would you like to know which exemptions are most commonly used to refuse RTI requests?"
    elif "maharashtra" in msg or "panchayat" in msg or "state" in msg:
        return "Would you like to know how to file your RTI online through the Aaple Sarkar portal?"
    else:
        return "Would you like me to draft a sample RTI application for your question?"
