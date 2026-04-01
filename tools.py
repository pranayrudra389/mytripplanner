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
def get_weather(destination: str, month: str) -> str:
    """Get typical weather information for a destination during a specific month.
    Use this to help travelers know what to pack and plan outdoor activities."""
    
    # For now, we use the search tool to find weather info
    # In production, we use a weather API like OpenWeatherMap
    query = f"typical weather in {destination} during {month} temperature rainfall what to pack"
    results = search_tool.invoke(query)
    return results

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
    return [search_tool, get_weather, calculate_budget, save_itinerary]

