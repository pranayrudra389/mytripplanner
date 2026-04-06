import os
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from langchain_core.tools import tool

load_dotenv()

search_tool = TavilySearch(
    max_results=5,
    topic="general"
)

@tool
def search_hotels(destination: str, check_in: str, check_out: str, budget_level: str, num_guests: int = 2) -> str:
    """Search for hotels at a specific destination.
    budget_level should be 'budget', 'mid-range', or 'luxury'.
    check_in and check_out should be dates like '2026-04-05'.
    Returns hotel names, prices, ratings, and amenities."""
    
    price_map = {"budget": "under $80/night", "mid-range": "$80-200/night", "luxury": "over $200/night"}
    price_hint = price_map.get(budget_level, "$80-200/night")
    
    query = f"best {budget_level} hotels in {destination} {price_hint} {check_in} for {num_guests} guests amenities ratings"
    results = search_tool.invoke(query)
    
    # Extract clean text from search results
    if isinstance(results, dict) and "results" in results:
        summaries = []
        for r in results["results"][:5]:
            summaries.append(f"- {r.get('title', '')}: {r.get('content', '')[:200]}")
        return f"Hotels in {destination} ({budget_level}):\n" + "\n".join(summaries)
    
    return str(results)

@tool
def search_attractions(destination: str, interests: str) -> str:
    """Search for attractions and activities at a destination.
    interests should be comma-separated like 'food, temples, shopping'.
    Returns top attractions with descriptions and estimated costs."""

    query = f"top things to do in {destination} {interests} hidden gems local favorites with prices and tips 2026"
    results = search_tool.invoke(query)

    if isinstance(results, dict) and "results" in results:
        summaries = []
        for r in results["results"][:5]:
            summaries.append(f"- {r.get('title', '')}: {r.get('content', '')[:200]}")
        return f"Attractions in {destination}:\n" + "\n".join(summaries)

    return str(results)


@tool
def search_transport(departure: str, destination: str, travel_mode: str, date: str = "") -> str:
    """Search for transportation options between two places.
    travel_mode should be 'flight' or 'roadtrip'.
    Returns options with estimated prices and duration."""

    if travel_mode == "flight":
        query = f"flights from {departure} to {destination} {date} estimated price duration airlines 2026"
    else:
        query = f"road trip from {departure} to {destination} driving time route gas cost tips 2026"

    results = search_tool.invoke(query)

    if isinstance(results, dict) and "results" in results:
        summaries = []
        for r in results["results"][:5]:
            summaries.append(f"- {r.get('title', '')}: {r.get('content', '')[:200]}")
        return f"Transport from {departure} to {destination} ({travel_mode}):\n" + "\n".join(summaries)

    return str(results)

@tool
def get_weather(destination: str, month: str) -> str:
    """Get typical weather information for a destination during a specific month.
    Use this to help travelers know what to pack and plan outdoor activities."""
    
    # For now, we use the search tool to find weather info
    # In production, we use a weather API like OpenWeatherMap
    query = f"typical weather in {destination} during {month} temperature rainfall what to pack"
    results = search_tool.invoke(query)
    if isinstance(results, dict) and "results" in results:
        summaries = []
        for r in results["results"][:3]:
            summaries.append(r.get("content", "")[:200])
        return f"Weather in {destination} during {month}:\n" + "\n".join(summaries)

    return str(results)


@tool
def calculate_budget(total_budget: float, expenses: str) -> str:
    """Calculate remaining budget after expenses.
    Pass expenses as a comma-separated string like: 'hotel:500,flights:800,food:200'.
    Returns a budget breakdown showing what's spent and what's remaining."""
    
    parsed_expenses: dict[str, float] = {}
    total_spent = 0.0
    
    for item in expenses.split(","):
        item = item.strip()
        if ":" in item:
            name, value = item.split(":", 1)
            try:
                amount = float(value.strip())
                parsed_expenses[name.strip()] = amount
                total_spent += amount
            except ValueError:
                continue
    
    remaining = total_budget - total_spent
    
    result = "Budget Breakdown:\n"
    for name, amount in parsed_expenses.items():
        result += f"  {name}: ${amount:,.2f}\n"
    result += f"\nTotal spent: ${total_spent:,.2f}"
    result += f"\nBudget: ${total_budget:,.2f}"
    result += f"\nRemaining: ${remaining:,.2f}"
    
    if remaining < 0:
        result += "\n⚠️ WARNING: Over budget!"
    elif remaining < total_budget * 0.1:
        result += "\n⚠️ Less than 10% budget remaining"
    
    return result

@tool
def save_itinerary(itinerary_text: str, filename: str = "trip_itinerary.md") -> str:
    """Save the final trip itinerary to a markdown file.
    Only use this after the user has approved the itinerary."""
    
    filepath = os.path.join(os.getcwd(), filename)
    with open(filepath, "w") as f:
        f.write(itinerary_text)
    
    return f"Itinerary saved to {filepath}"


def get_tools():
    """Return all available tools for the agent."""
    return [search_hotels, search_attractions, search_transport, get_weather, calculate_budget, save_itinerary]

