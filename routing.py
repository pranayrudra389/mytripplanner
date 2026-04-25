from state import AgentState
from langgraph.graph import END

MAX_RESEARCH_ROUNDS = 3
MAX_REVISION_ROUNDS = 2


# --- Routing Logic ---
def route_after_gather(state: AgentState) -> str:
    """Decide what to do after gathering preferences."""
    last_message = state["messages"][-1]
    
    if hasattr(last_message, "content") and "PLANNING_READY" in last_message.content:
        return "extract"
    return END # keep gathering


def route_after_extract(state: AgentState) -> str:
    """Only continue if extraction produced a usable preference set."""
    if state.get("planning_stage") == "researching":
        return "research"
    return END

def route_after_research(state: AgentState) -> str:
    """Decide what to do after research."""
    last_message = state["messages"][-1]
    
    # if the LLM wants to use a tool, go to the tool node
    if (
        hasattr(last_message, "tool_calls")
        and last_message.tool_calls
        and state.get("research_count", 0) < MAX_RESEARCH_ROUNDS
    ):
        return "tools"
    
    return "build"


def route_after_reflect(state: AgentState) -> str:
    """Limit itinerary rebuilds so the graph cannot loop forever."""
    if (
        state.get("planning_stage") == "revising"
        and state.get("revision_count", 0) < MAX_REVISION_ROUNDS
    ):
        return "build"
    return "present"
