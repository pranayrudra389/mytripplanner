from models import TripPreferences, DayPlan, Itinerary

# Test creating preferences incrementally
prefs = TripPreferences(destination="Tokyo")
print(f"Destination: {prefs.destination}")
print(f"Budget: {prefs.budget}")
print(f"Days: {prefs.num_days}")

# Update preferences as user provides more info
prefs.budget = 2000.0
prefs.num_days = 5
prefs.interests = ["food", "temples", "shopping"]
print(f"\nUpdated: {prefs}")

# Test creating a day plan
day1 = DayPlan(
    day_number=1,
    location="Shibuya, Tokyo",
    morning="visit Meiji Shrine",
    afternoon="Explore Harajuku",
    evening="Dinner in Shibuya",
    estimated_cost=150.0
)
print(f"\nDay 1: {day1}")

# Test the full itinerary
trip = Itinerary(
    destination="Tokyo",
    total_days=5,
    days=[day1]
)
print(f"\nTrip: {trip.destination}, {trip.total_days} days, {len(trip.days)} day(s) planned")
