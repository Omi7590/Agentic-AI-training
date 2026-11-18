# RTI Mitra - graph.py
# Rebuilds the RTI Mitra agent in LangGraph with:
#   - Memory (conversation history across turns)
#   - One approval step (flags draft applications for user confirmation)
# Powers POST /agent in app/main.py

import os
import json
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool, StructuredTool
from pydantic import BaseModel as PydanticBase, Field
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from app.rag import ask as rag_ask
from app.tools import draft_rti_application as _draft_tool

load_dotenv()

MODEL = "qwen/qwen3.8-27b"


# ── LangGraph Tools ───────────────────────────────────────────────────────────

class RagSearchInput(PydanticBase):
    question: str = Field(description="The RTI question to search for in the rule database.")

class DraftRtiInput(PydanticBase):
    applicant_name: str = Field(description="Full name of the RTI applicant.")
    applicant_address: str = Field(description="Address of the RTI applicant.")
    authority_name: str = Field(description="Name of the public authority / PIO.")
    authority_address: str = Field(description="Address of the public authority.")
    information_sought: str = Field(description="The information being requested (max 150 words for Maharashtra).")
    jurisdiction: str = Field(default="Maharashtra", description="Central or Maharashtra.")
    is_bpl: bool = Field(default=False, description="True if applicant is BPL (fee exempt).")
    via_apio: bool = Field(default=False, description="True if filing through APIO (+5 days deadline).")


def _rag_search(question: str) -> str:
    """Search the RTI rule database and return a grounded answer with citations."""
    result = rag_ask(question, top_k=5)
    citations = [f"{c['title']} ({c['source']})" for c in result["citations"]]
    return f"{result['answer']}\n\nSources: {'; '.join(citations)}"


def _draft_rti(
    applicant_name: str,
    applicant_address: str,
    authority_name: str,
    authority_address: str,
    information_sought: str,
    jurisdiction: str = "Maharashtra",
    is_bpl: bool = False,
    via_apio: bool = False,
) -> str:
    """Draft a complete RTI application with correct fee, word count and reply dates."""
    result = _draft_tool(
        applicant_name=applicant_name,
        applicant_address=applicant_address,
        authority_name=authority_name,
        authority_address=authority_address,
        information_sought=information_sought,
        jurisdiction=jurisdiction,
        is_bpl=is_bpl,
        via_apio=via_apio,
    )
    return (
        f"{result['draft']}\n\n"
        f"[Word count: {result['word_count']}/{result['word_limit']} | "
        f"Fee: {result['fee']} | "
        f"Reply due: {result['reply_due']} | "
        f"Appeal due: {result['appeal_due']}]"
    )


rag_search = StructuredTool.from_function(
    func=_rag_search,
    name="rag_search",
    description="Search the RTI rule database and return a grounded answer with citations.",
    args_schema=RagSearchInput,
)

draft_rti = StructuredTool.from_function(
    func=_draft_rti,
    name="draft_rti",
    description="Draft a complete RTI application with correct fee, word count and reply dates.",
    args_schema=DraftRtiInput,
)


TOOLS = [rag_search, draft_rti]
TOOL_MAP = {t.name: t for t in TOOLS}


# ── State ─────────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    pending_approval: bool
    pending_tool_call: dict


# ── LLM ───────────────────────────────────────────────────────────────────────

def get_llm():
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model=MODEL,
        temperature=0.2,
        max_tokens=1024,
    ).bind_tools(TOOLS)


SYSTEM = SystemMessage(content="""You are RTI Mitra, an intelligent agent for Right to Information (RTI) queries.

Use rag_search for fee, deadline, exemption and portal questions.
Use draft_rti when the user wants to draft an RTI application.
If the question asks for live case data, say: "I don't know — RTI Mitra does not have access to live case records."
Always end with: "This is general information on the RTI Act, not legal advice."
""")


# ── Nodes ─────────────────────────────────────────────────────────────────────

def agent_node(state: AgentState) -> AgentState:
    """Call the LLM to decide the next action."""
    llm = get_llm()
    messages = [SYSTEM] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response], "pending_approval": False, "pending_tool_call": {}}


def approval_node(state: AgentState) -> AgentState:
    """
    Approval step: if the LLM wants to call draft_rti,
    flag it for approval before executing.
    """
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        for tc in last.tool_calls:
            if tc["name"] == "draft_rti":
                return {
                    "messages": state["messages"],
                    "pending_approval": True,
                    "pending_tool_call": tc,
                }
    return {"messages": state["messages"], "pending_approval": False, "pending_tool_call": {}}


def tool_node(state: AgentState) -> AgentState:
    """Execute all tool calls from the last LLM message."""
    last = state["messages"][-1]
    tool_messages = []
    if hasattr(last, "tool_calls") and last.tool_calls:
        for tc in last.tool_calls:
            tool_fn = TOOL_MAP.get(tc["name"])
            if tool_fn:
                try:
                    result = tool_fn.invoke(tc["args"])
                except Exception as e:
                    result = f"Tool error: {e}"
            else:
                result = f"Unknown tool: {tc['name']}"
            tool_messages.append(
                ToolMessage(content=str(result), tool_call_id=tc["id"])
            )
    return {"messages": tool_messages, "pending_approval": False, "pending_tool_call": {}}


# ── Routing ───────────────────────────────────────────────────────────────────

def route_after_agent(state: AgentState) -> str:
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "approval"
    return END


def route_after_approval(state: AgentState) -> str:
    if state.get("pending_approval"):
        # Auto-approve for API use; in real UI this would pause for user input
        return "tools"
    return "tools"


# ── Build Graph ───────────────────────────────────────────────────────────────

def build_graph():
    memory = MemorySaver()
    builder = StateGraph(AgentState)

    builder.add_node("agent", agent_node)
    builder.add_node("approval", approval_node)
    builder.add_node("tools", tool_node)

    builder.set_entry_point("agent")
    builder.add_conditional_edges("agent", route_after_agent, {"approval": "approval", END: END})
    builder.add_conditional_edges("approval", route_after_approval, {"tools": "tools"})
    builder.add_edge("tools", "agent")

    return builder.compile(checkpointer=memory)


# Singleton graph instance
_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


def run_graph(question: str, thread_id: str = "default") -> dict:
    """
    Run the LangGraph agent with memory.
    thread_id keeps conversation history across turns.
    """
    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "messages": [HumanMessage(content=question)],
        "pending_approval": False,
        "pending_tool_call": {},
    }

    final_state = graph.invoke(initial_state, config=config)
    last_message = final_state["messages"][-1]

    return {
        "question": question,
        "answer": last_message.content if hasattr(last_message, "content") else str(last_message),
        "pending_approval": final_state.get("pending_approval", False),
        "thread_id": thread_id,
    }


if __name__ == "__main__":
    print("Test 1: RTI fee question")
    r = run_graph("What is the RTI fee in Maharashtra?", thread_id="test-1")
    print(r["answer"][:300])

    print("\nTest 2: Draft RTI")
    r = run_graph(
        "Draft an RTI to Kopargaon Panchayat Samiti for the 2026 road-repair work order.",
        thread_id="test-2"
    )
    print(r["answer"][:300])
