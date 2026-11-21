# RTI Mitra - agent_loop.py
# Hand-written agent loop that can call:
#   1. RAG search (app/rag.py)
#   2. draft_rti_application tool (app/tools.py)
# The agent decides which tool to call based on the user question,
# calls it, and returns a final answer with citations.

import json
import os

from dotenv import load_dotenv
from groq import Groq

from app.rag import ask as rag_ask
from app.tools import draft_rti_application

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "qwen/qwen3.8-27b"

AGENT_SYSTEM_PROMPT = """You are RTI Mitra, an intelligent agent that helps citizens with RTI (Right to Information) queries.

You have access to two tools:

1. rag_search(question) — searches the RTI rule database and returns grounded answers with citations.
   Use this for: fee questions, deadline questions, exemption questions, portal questions.

2. draft_rti_application(...) — drafts a complete RTI application with correct fee, word count and reply dates.
   Use this when the user wants to draft or write an RTI application.

To call a tool, respond with EXACTLY this JSON format (nothing else):
{"tool": "rag_search", "args": {"question": "..."}}
or
{"tool": "draft_rti", "args": {"applicant_name": "...", "applicant_address": "...", "authority_name": "...", "authority_address": "...", "information_sought": "...", "jurisdiction": "Maharashtra", "is_bpl": false}}

After you receive the tool result, provide a final helpful answer to the user.
If the question cannot be answered from RTI rules (e.g. live case data), say: "I don't know — RTI Mitra does not have access to live case records."
Always end with: "This is general information on the RTI Act, not legal advice."
"""


def call_llm(messages: list) -> str:
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()


def parse_tool_call(text: str):
    """Try to extract a JSON tool call from the LLM response."""
    try:
        # Find JSON block in response
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(text[start:end])
            if "tool" in data and "args" in data:
                return data
    except (json.JSONDecodeError, ValueError):
        pass
    return None


def run_tool(tool_call: dict) -> str:
    """Execute the tool and return the result as a string."""
    tool = tool_call["tool"]
    args = tool_call["args"]

    if tool == "rag_search":
        result = rag_ask(args["question"], top_k=5)
        citations = [f"[{c['title']}]({c['source']})" for c in result["citations"]]
        return f"Answer: {result['answer']}\n\nCitations: {', '.join(citations)}"

    elif tool == "draft_rti":
        result = draft_rti_application(
            applicant_name=args.get("applicant_name", "Applicant"),
            applicant_address=args.get("applicant_address", "Address not provided"),
            authority_name=args.get("authority_name", "Public Information Officer"),
            authority_address=args.get("authority_address", "Address not provided"),
            information_sought=args.get("information_sought", ""),
            jurisdiction=args.get("jurisdiction", "Maharashtra"),
            is_bpl=args.get("is_bpl", False),
            via_apio=args.get("via_apio", False),
        )
        return (
            f"Draft RTI Application:\n\n{result['draft']}\n\n"
            f"Word count: {result['word_count']}/{result['word_limit']} | "
            f"Fee: {result['fee']} | "
            f"Reply due: {result['reply_due']} | "
            f"Appeal due: {result['appeal_due']}"
        )

    return f"Unknown tool: {tool}"


def run_agent(user_question: str, max_steps: int = 3) -> dict:
    """
    Hand-written agent loop:
    1. Send question to LLM with tool descriptions
    2. If LLM returns a tool call JSON, execute the tool
    3. Feed tool result back to LLM
    4. Return final answer
    """
    messages = [
        {"role": "system", "content": AGENT_SYSTEM_PROMPT},
        {"role": "user", "content": user_question},
    ]

    steps = []

    for step in range(max_steps):
        response = call_llm(messages)
        tool_call = parse_tool_call(response)

        if tool_call:
            # Execute tool
            tool_result = run_tool(tool_call)
            steps.append({
                "step": step + 1,
                "tool": tool_call["tool"],
                "args": tool_call["args"],
                "result_preview": tool_result[:200],
            })
            # Feed result back
            messages.append({"role": "assistant", "content": response})
            messages.append({"role": "user", "content": f"Tool result:\n{tool_result}\n\nNow give the final answer to the user."})
        else:
            # LLM gave a direct answer — done
            return {
                "question": user_question,
                "answer": response,
                "steps": steps,
                "total_steps": len(steps),
            }

    # Final answer after max steps
    final = call_llm(messages)
    return {
        "question": user_question,
        "answer": final,
        "steps": steps,
        "total_steps": len(steps),
    }


if __name__ == "__main__":
    questions = [
        "What is the RTI application fee in Maharashtra?",
        "Draft an RTI to Kopargaon Panchayat Samiti asking for the 2026 road-repair work order.",
    ]
    for q in questions:
        print(f"\n{'='*60}")
        print(f"Q: {q}")
        result = run_agent(q)
        print(f"Steps used: {result['total_steps']}")
        print(f"Answer:\n{result['answer'][:400]}")
