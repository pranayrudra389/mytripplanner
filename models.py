from pydantic import BaseModel

class TripPreferences(BaseModel):
    """What the user wants - gathered through conversation."""
    destination: str = ""
    num_days: int = 0
    budget: float = 0.0
    travel_mode: str = ""       # "flight" or "roadtrip"
    interests: list[str] = []   # ["food", "history", "adventure"]
    accommodation: str = ""     # "budget", "mid-range", "luxury"
    notes: str = ""             # any extra details from the user
    

class DayPlan(BaseModel):
    """One day of the itinerary."""
    day_number: int
    date: str = ""
    location: str = ""
    morning: str = ""
    afternoon: str = ""
    evening: str = ""
    hotel: str = ""
    estimated_cost: float = 0.0
    
class Itinerary(BaseModel):
    """The complete trip plan."""
    destination: str
    total_days: int
    total_estimated_cost: float = 0.0
    days: list[DayPlan] = []
    travel_tips: list[str] = []
    budget_summary: str = ""
    