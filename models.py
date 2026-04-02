from pydantic import BaseModel, field_validator

class TripPreferences(BaseModel):
    """What the user wants - gathered through conversation."""
    destination: str = ""
    departure_city: str = ""
    start_date: str = ""
    end_date: str = ""
    num_days: int = 0
    num_travelers: int = 1
    budget: float = 0.0
    currency: str = "USD"
    travel_mode: str = ""       # "flight" or "roadtrip"
    interests: list[str] = []   # ["food", "history", "adventure"]
    accommodation: str = ""     # "budget", "mid-range", "luxury"
    split_stays: list[dict] = []
    notes: str = ""             # any extra details from the user
    
    @field_validator("budget")
    @classmethod
    def budget_must_be_positive(cls, v):
        if v < 0:
            raise ValueError("Budget cannot be negative")
        return v

    @field_validator("num_travelers")
    @classmethod
    def travelers_must_be_positive(cls, v):
        if v < 1:
            raise ValueError("Must have at least 1 traveler")
        return v

    def is_complete(self) -> bool:
        """Check if we have enough info to start planning."""
        return all([
            self.destination,
            self.num_days > 0 or (self.start_date and self.end_date),
            self.budget > 0,
            self.travel_mode,
        ])
        
    def missing_fields(self) -> list[str]:
        """Return list of fields still needed from the user."""
        missing = []
        if not self.destination:
            missing.append("destination")
        if self.num_days <= 0 and not (self.start_date and self.end_date):
            missing.append("dates (start and end date, or number of days)")
        if self.budget <= 0:
            missing.append("budget")
        if not self.travel_mode:
            missing.append("travel mode (flight or road trip)")
        return missing

class DayPlan(BaseModel):
    """One day of the itinerary."""
    day_number: int
    date: str = ""
    city: str = ""
    morning: str = ""
    afternoon: str = ""
    evening: str = ""
    hotel: str = ""
    hotel_cost: float = 0.0
    activity_cost: float = 0.0
    food_cost: float = 0.0
    transport_cost: float = 0.0
    daily_total: float = 0.0
    
    def calculate_daily_total(self) -> float:
        self.daily_total = self.hotel_cost + self.activity_cost + self.food_cost + self.transport_cost
        return self.daily_total
    
class Itinerary(BaseModel):
    """The complete trip plan."""
    destination: str
    departure_city: str = ""
    total_days: int
    num_travelers: int = 1
    days: list[DayPlan] = []
    travel_tips: list[str] = []
    packing_suggestions: list[str] = []
    budget_total: float = 0.0
    budget_remaining: float = 0.0
    flight_info: str = ""
    transport_between_cities: str = ""
    
    def calculate_totals(self) -> None:
        """Recalculate total costs from all days."""
        self.budget_total = sum(day.daily_total for day in self.days)
    