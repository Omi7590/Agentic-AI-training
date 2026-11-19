# RTI Mitra - graph.py
# Rebuilds the RTI Mitra agent in LangGraph with:
#   - Memory (conversation history across turns via MemorySaver)
#   - One real approval step using langgraph.types.interrupt()
#     that pauses the graph before executing draft_rti tool
# Powers POST /agent in app/main.py

import os
from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import StructuredTool
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import interrupt
from pydantic import BaseModel as PydanticBase
from pydantic import Field
from typing_extensions import TypedDict

from app.rag import ask as rag_ask
from app.tools import draft_rti_application as _draft_tool

load_dotenv()

MODEL = "qwen/qwen3.8-27b"


# ── Tool schemas ──────────────────────────────────────────────────────────────

class RagSearchInput(PydanticBase):
    question: str = Field(description="The RTI question to search in the rule database.")


class DraftRtiInput(PydanticBase):
    applicant_name: str = Field(description="Full name of the RTI applicant.")
    applicant_address: str = Field(description="Address of the RTI applicant.")
    authority_name: str = Field(description="Name of the public authority / PIO.")
    authority_address: str = Field(description="Address of the public authority.")
    information_sought: str = Field(
        description="The information being requested (max 150 words for Maharashtra)."
    )
    jurisdiction: str = Field(default="Maharashtra", description="Central or Maharashtra.")
    is_bpl: bool = Field(default=False, description="True if applicant is BPL (fee exempt).")
    via_apio: bool = Field(default=False, description="True if filing through APIO (+5 days).")


# ── Tool implementations ──────────────────────────────────────────────────────

def _rag_search(question: str) -> str:
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
    return {"messages": [response]}


def tool_node(state: AgentState) -> AgentState:
    """
    Execute tool calls. For draft_rti, uses interrupt() to pause
    and ask the user for approval before executing.
    """
    last = state["messages"][-1]
    tool_messages = []

    if hasattr(last, "tool_calls") and last.tool_calls:
        for tc in last.tool_calls:
            # ── Approval step via interrupt() ─────────────────────────────
            if tc["name"] == "draft_rti":
                # interrupt() pauses graph execution and waits for human input.
                # When resumed, the return value is the human's approval decision.
                approval = interrupt({
                    "action": "approval_required",
                    "tool": "draft_rti",
                    "message": (
                        "RTI Mitra wants to draft an RTI application with these details: "
                        + str(tc["args"])
                        + " — reply 'yes' to confirm or 'no' to cancel."
                    ),
                })
                if str(approval).strip().lower() not in ("yes", "y", "approve", "ok"):
                    tool_messages.append(
                        ToolMessage(
                            content="Draft cancelled by user.",
                            tool_call_id=tc["id"],
                        )
                    )
                    continue

            # ── Execute tool ──────────────────────────────────────────────
            tool_fn = TOOL_MAP.get(tc["name"])
            if tool_fn:
                try:
                    result = tool_fn.invoke(tc["args"])
                except (ValueError, RuntimeError, TypeError) as e:
                    result = f"Tool error: {e}"
            else:
                result = f"Unknown tool: {tc['name']}"

            tool_messages.append(
                ToolMessage(content=str(result), tool_call_id=tc["id"])
            )

    return {"messages": tool_messages}


# ── Routing ───────────────────────────────────────────────────────────────────

def route_after_agent(state: AgentState) -> str:
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END


# ── Build Graph ───────────────────────────────────────────────────────────────

def build_graph():
    memory = MemorySaver()
    builder = StateGraph(AgentState)

    builder.add_node("agent", agent_node)
    builder.add_node("tools", tool_node)

    builder.set_entry_point("agent")
    builder.add_conditional_edges(
        "agent", route_after_agent, {"tools": "tools", END: END}
    )
    builder.add_edge("tools", "agent")

    return builder.compile(checkpointer=memory)


_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


def run_graph(question: str, thread_id: str = "default", approval: str | None = None) -> dict:
    """
    Run the LangGraph agent with memory.

    - First call: pass question only. If draft_rti is needed, graph pauses
      at interrupt() and returns pending_approval=True.
    - Second call: pass the same thread_id and approval='yes' to resume.
    """
    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id}}

    if approval is not None:
        # Resume after interrupt with the user's approval decision
        final_state = graph.invoke(approval, config=config)
    else:
        initial_state = {"messages": [HumanMessage(content=question)]}
        final_state = graph.invoke(initial_state, config=config)

    # Check if graph is interrupted (waiting for approval)
    snapshot = graph.get_state(config)
    is_interrupted = bool(snapshot.next)

    if is_interrupted:
        interrupt_data = None
        for task in snapshot.tasks:
            if hasattr(task, "interrupts") and task.interrupts:
                interrupt_data = task.interrupts[0].value
                break
        return {
            "question": question,
            "answer": "Approval required before drafting the RTI application.",
            "pending_approval": True,
            "interrupt_data": interrupt_data,
            "thread_id": thread_id,
        }

    last_message = final_state["messages"][-1]
    return {
        "question": question,
        "answer": last_message.content if hasattr(last_message, "content") else str(last_message),
        "pending_approval": False,
        "thread_id": thread_id,
    }


if __name__ == "__main__":
    print("Test 1: RTI fee (no approval needed)")
    r = run_graph("What is the RTI fee in Maharashtra?", thread_id="t1")
    print("Pending:", r["pending_approval"])
    print("Answer:", r["answer"][:300])

    print("\nTest 2: Draft RTI (triggers interrupt approval)")
    r = run_graph(
        "Draft an RTI to Kopargaon Panchayat Samiti for the 2026 road-repair work order.",
        thread_id="t2",
    )
    print("Pending approval:", r["pending_approval"])
    if r["pending_approval"]:
        print("Resuming with approval='yes'...")
        r2 = run_graph("", thread_id="t2", approval="yes")
        print("Answer:", r2["answer"][:300])
