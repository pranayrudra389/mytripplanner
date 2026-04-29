from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, AIMessage

from state import AgentState
from config import get_config_from_env, get_llm_model
from tools import get_tools
from prompts import (
    BUILD_SYSTEM,
    EXTRACT_SYSTEM,
    GATHER_SYSTEM,
    REFLECT_SYSTEM,
    RESEARCH_SYSTEM,
)
from routing import (
    route_after_extract,
    route_after_gather,
    route_after_reflect,
    route_after_research,
)


def _missing_preference_fields(preferences: dict) -> list[str]:
    """Return the minimum fields required to plan a trip safely."""
    missing = []

    if not preferences.get("destination"):
        missing.append("destination")
    if not preferences.get("departure_city"):
        missing.append("departure city")
    if not (preferences.get("start_date") and preferences.get("end_date")) and not preferences.get("num_days"):
        missing.append("dates or trip length")
    if not preferences.get("budget"):
        missing.append("budget")
    if not preferences.get("travel_mode"):
        missing.append("travel mode")
    if not preferences.get("accommodation"):
        missing.append("accommodation preference")

    return missing


def create_agent():
    """Create and compile the trip planner agent graph."""
    
    config = get_config_from_env()
    llm = get_llm_model(config)
    tools = get_tools()
    llm_with_tools = llm.bind_tools(tools)

    # -- Node: Present ---
    def present_node(state: AgentState) -> dict:
        """Present the final itinerary to the user."""
        draft = state.get("itinerary_draft", "")
        message = f"""Here's your trip plan! Please review it:

        {draft}

        Would you like me to:
        - **Save** this itinerary to a file
        - **Adjust** anything (budget, activities, hotels)
        - **Start over** with different preferences"""

        return {"messages": [AIMessage(content=message)]}

    def gather_node(state: AgentState) -> dict:
        """Collect trip preferences through conversation."""
        messages = [SystemMessage(content=GATHER_SYSTEM)] + state["messages"]
        response = llm.invoke(messages)
        return {"messages": [response]}

    
    def extract_preferences(state: AgentState) -> dict:
        """Parse conversation into structured preferences."""
        import json

        messages = [SystemMessage(content=EXTRACT_SYSTEM)] + state["messages"]
        response = llm.invoke(messages)

        try:
            text = response.content.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            prefs = json.loads(text)
            missing_fields = _missing_preference_fields(prefs)

            if missing_fields:
                follow_up = (
                    "I still need a few details before I can research your trip: "
                    + ", ".join(missing_fields)
                    + "."
                )
                return {
                    "messages": [AIMessage(content=follow_up)],
                    "preferences": prefs,
                    "planning_stage": "gathering",
                }

            return {"preferences": prefs, "planning_stage": "researching"}
        except (json.JSONDecodeError, Exception) as e:
            print(f"Warning: Could not parse preferences: {e}")
            return {
                "messages": [
                    AIMessage(
                        content=(
                            "I couldn't structure your trip details yet. "
                            "Please restate your destination, departure city, dates or trip length, "
                            "budget, travel mode, and accommodation preference."
                        )
                    )
                ],
                "planning_stage": "gathering",
            }
    
    def research_node(state: AgentState) -> dict:
        """Research hotels, attractions, transport based on preferences."""
        prefs = state["preferences"]
        system = RESEARCH_SYSTEM.format(
            destination=prefs.get("destination", "unknown"),
            departure=prefs.get("departure_city", "unknown"),
            start_date=prefs.get("start_date", ""),
            end_date=prefs.get("end_date", ""),
            num_days=prefs.get("num_days", 0),
            budget=prefs.get("budget", 0),
            travel_mode=prefs.get("travel_mode", ""),
            accommodation=prefs.get("accommodation", "mid-range"),
            interests=", ".join(prefs.get("interests", [])),
            num_travelers=prefs.get("num_travelers", 1),
            split_stays=prefs.get("split_stays", []),
        )
        messages = [SystemMessage(content=system)] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {
            "messages": [response],
            "research_count": state.get("research_count", 0) + 1,
        }

    def build_node(state: AgentState) -> dict:
        """Build the day-by-day itinerary from research."""
        prefs = state.get("preferences", {})
        budget = prefs.get("budget", 1500)
        num_days = prefs.get("num_days", 5)
        daily_budget = round(budget / max(num_days, 1), 2)

        system = BUILD_SYSTEM.format(
            budget=budget,
            daily_budget=daily_budget,
            destination=prefs.get("destination", ""),
            start_date=prefs.get("start_date", ""),
            end_date=prefs.get("end_date", ""),
            accommodation=prefs.get("accommodation", "mid-range"),
            interests=", ".join(prefs.get("interests", [])),
            num_travelers=prefs.get("num_travelers", 1),
            split_stays=prefs.get("split_stays", []),
        )
        messages = [SystemMessage(content=system)] + state["messages"]
        response = llm.invoke(messages)
        return {
            "messages": [response],
            "itinerary_draft": response.content,
            "planning_stage": "reflecting",
        }


    def reflect_node(state: AgentState) -> dict:
        """Review the itinerary for quality and budegt compliance."""
        prefs = state.get("preferences", {})
        system = REFLECT_SYSTEM.format(
            itinerary=state.get("itinerary_draft", "No itinerary"),
            budget=prefs.get("budget", 0),
            accommodation=prefs.get("accommodation", "mid-range"),
        )
        messages = [SystemMessage(content=system)] + state["messages"]
        response = llm.invoke(messages)
        needs_revision = "PLAN_REVISE" in response.content
        return {
            "messages": [response],
            "planning_stage": "revising" if needs_revision else "presenting",
            "revision_count": state.get("revision_count", 0) + (1 if needs_revision else 0),
        }

    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("gather", gather_node)
    graph.add_node("research", research_node)
    graph.add_node("tools", ToolNode(tools))
    graph.add_node("build", build_node)
    graph.add_node("reflect", reflect_node)
    graph.add_node("present", present_node)
    graph.add_node("extract", extract_preferences)
    
    # Add edges
    graph.add_edge(START, "gather")
    
    graph.add_conditional_edges("gather", route_after_gather, {
        END: END,
        "extract": "extract"
    })
    graph.add_conditional_edges("extract", route_after_extract, {
        END: END,
        "research": "research",
    })
    graph.add_conditional_edges("research", route_after_research, {
        "tools": "tools",
        "build": "build"
    })
    
    graph.add_edge("tools", "research")   # after tool, back to research
    graph.add_edge("build", "reflect")    # after build, always reflect
    graph.add_conditional_edges("reflect", route_after_reflect, {
        "build": "build",
        "present": "present",
    })
    graph.add_edge("present", END)        # after present, wait for user

    return graph.compile()
