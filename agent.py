import os
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from models import TripPreferences
from tools import get_tools

load_dotenv()

class AgentState(TypedDict):
    """The shared state that flow through the graph."""
    messages: Annotated[list, add_messages]
    preferences: dict
    planning_stage: str     # "gathering", "researching", "building", "reflecting", "presenting"
    research_count: int     # how many research cycles we've done
    itinerary_draft: str    # the current itinerary text

# --- LLM and Tools ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
tools = get_tools()
llm_with_tools = llm.bind_tools(tools)

# --- Node: Gather Preferences ---
GATHER_SYSTEM = """You are a friendly trip planning assistant gathering travel preferences.
Collect these details through natural conversation:
- Destination
- Departure city (where they're traveling from)
- Dates or number of days
- Budget (total trip budget in USD)
- Travel mode (flight or road trip)
- Accommodation preference (budget, mid-range, luxury)
- Interests (food, history, adventure, shopping, nature, etc.)
- Number of travelers
- Any split stay preferences (e.g., 3 nights Tokyo + 2 nights Kyoto)

Rules:
- Ask for 1-2 missing things at a time, not everything at once
- Be conversational and enthusiastic
- When you have ALL the details listed above, end your message with EXACTLY: PLANNING_READY
- Do not say PLANNING_READY until you have destination, dates, budget, travel mode, and accommodation"""


def gather_node(state: AgentState) -> dict:
    """Collect trip preferences through conversation."""
    messages = [SystemMessage(content=GATHER_SYSTEM)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}


EXTRACT_SYSTEM = """Extract trip preferences from this conversation as JSON.
Return ONLY valid JSON with these fields (use empty string or 0 if not mentioned):
{{
    "destination": "main destination",
    "departure_city": "where they're leaving from",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD", 
    "num_days": 0,
    "num_travelers": 1,
    "budget": 0.0,
    "travel_mode": "flight or roadtrip",
    "accommodation": "budget or mid-range or luxury",
    "interests": ["list", "of", "interests"],
    "split_stays": [{{"city": "name", "nights": 0, "accommodation": "level"}}],
    "notes": "any other details mentioned"
}}"""


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
        return {"preferences": prefs, "planning_stage": "researching"}
    except (json.JSONDecodeError, Exception) as e:
        print(f"Warning: Could not parse preferences: {e}")
        return {"planning_stage": "researching"}


# --- Node: Research ---
RESEARCH_SYSTEM = """You are a trip planning researcher. You MUST use the available tools to search for real information.

User's trip preferences:
- Destination: {destination}
- Departure: {departure}
- Dates: {start_date} to {end_date} ({num_days} days)
- Budget: ${budget}
- Travel mode: {travel_mode}
- Accommodation: {accommodation}
- Interests: {interests}
- Travelers: {num_travelers}
- Split stays: {split_stays}

Your task — use these tools NOW:
1. Call search_hotels for each city in the trip
2. Call search_attractions for each city
3. Call search_transport for getting to the destination
4. Call get_weather for the destination during the travel month

DO NOT make up information. You MUST call at least 2 tools before responding.
After tool results come back, summarize your findings.

CRITICAL: When tool results come back, extract specific hotel names, prices, 
restaurant names, and attraction details. Include these EXACT details in your 
summary — do not substitute with generic information from your training data."""

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

# --- Node: Build Itinerary ---
BUILD_SYSTEM = """You are a trip itinerary builder. Using the research data from previous messages,
create a detailed day-by-day itinerary.

CRITICAL BUDGET RULE: The total trip cost MUST stay within ${budget}. 
Budget per day: approximately ${daily_budget}/day.
If costs exceed the budget, use cheaper alternatives.

STRICT BUDGET ENFORCEMENT:
- Calculate max daily budget: ${daily_budget}/day
- Hotels MUST be under $100/night for budget, under $150/night for mid-range
- Food budget: max $40/day for two people at budget level, $60/day for mid-range
- BEFORE writing the itinerary, calculate: (hotel_cost x nights) + (food_per_day x days) + activities + gas/electricity
- If this exceeds ${budget}, use cheaper hotels or fewer paid activities
- The grand total MUST be under ${budget} — not over, not "with adjustments needed"

SCHEDULE CONSTRAINTS:
- Check if the user mentioned work days or events on specific dates
- If the user mentioned work days or a specific schedule, follow their EXACT constraints from the conversation
- Do not assume work hours — use whatever times the user specified
- On conference/event days, only plan evening activities
- Weekends (Saturday/Sunday) are full free days

User preferences:
- Destination: {destination}
- Dates: {start_date} to {end_date}
- Accommodation: {accommodation}
- Interests: {interests}
- Travelers: {num_travelers}
- Split stays: {split_stays}

Format as markdown with:
- Day-by-day breakdown (morning/afternoon/evening)
- Hotel with nightly cost
- Activities with costs
- Food estimates
- Daily totals (MUST include hotel cost for that night + food + activities + transport)
- Running budget total
- Grand total (MUST be under ${budget})

Use actual data from the research. Do not fabricate prices.

IMPORTANT DATE RULES:
- Map user's specific schedule constraints EXACTLY as stated
- If the user mentions specific events on specific dates, place them on those EXACT dates
- Saturday and Sunday are NOT work days
- Calculate day-of-week correctly from the dates provided"""

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
    
# --- Node: Reflect ---
REFLECT_SYSTEM = """Review this itinerary critically. Budget limit is ${budget}.

{itinerary}

Check:
1. Does total cost exceed ${budget}? 
2. Are days balanced (not too packed or too empty)?
3. Are hotel prices realistic for {accommodation} level?

If the plan is acceptable (within 10% of budget), respond with: PLAN_APPROVED
If over budget, respond with: PLAN_APPROVED (but add a note about budget concerns)

IMPORTANT: If the total cost is within 5% of the budget, respond with PLAN_APPROVED.
If it exceeds the budget by more than 5%, respond with PLAN_APPROVED but include 
specific line items to cut (e.g., "Switch LUMA Hotel to HI San Francisco hostel to save $50/night").
Always end with PLAN_APPROVED — we present to the user regardless, but include your budget notes."""

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
    return {
        "messages": [response],
        "planning_stage": "presenting",
    }
    
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

# --- Routing Logic ---
def route_after_gather(state: AgentState) -> str:
    """Decide what to do after gathering preferences."""
    last_message = state["messages"][-1]
    
    if hasattr(last_message, "content") and "PLANNING_READY" in last_message.content:
        return "research"
    return END # keep gathering

def route_after_research(state: AgentState) -> str:
    """Decide what to do after research."""
    last_message = state["messages"][-1]
    
    # if the LLM wants to use a tool, go to the tool node
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    
    return "build"

def route_after_tools(state: AgentState) -> str:
    """After a tool runs, go back to research to process the results."""
    return "research"

def route_after_reflect(state: AgentState) -> str:
    """Decide if the plan is good enough or needs revision."""
    last_message = state["messages"][-1]
    
    if hasattr(last_message, "content") and "PLAN_APPROVED" in last_message.content:
        return "present"
    
    # If not approved and we haven't exceeded research limit, go back
    if state.get("research_count", 0) < 3:
        return "build"
    
    return "present" # present anyway after max iterations


# --- Build the Graph ---
def create_agent():
    """Create and compile the trip planner agent graph."""
    
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
        "research": "extract"
    })
    graph.add_edge("extract", "research")
    graph.add_conditional_edges("research", route_after_research, {
        "tools": "tools",
        "build": "build"
    })
    
    graph.add_edge("tools", "research")   # after tool, back to research
    graph.add_edge("build", "reflect")    # after build, always reflect
    graph.add_edge("reflect", "present")  # after reflect, always present (no loop back)
    graph.add_edge("present", END)        # after present, wait for user

    return graph.compile()