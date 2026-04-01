from tools import search_tool, get_weather, calculate_budget, save_itinerary

# Test 1: Web search — see what type it returns
print("=== Testing Web Search ===")
result = search_tool.invoke("best budget hotels in Shibuya Tokyo 2026")
print(f"Type: {type(result)}")
print(result)

print("\n=== Testing Weather ===")
result = get_weather.invoke({"destination": "Tokyo", "month": "April"})
print(f"Type: {type(result)}")
print(str(result)[:500])

print("\n=== Testing Budget Calculator ===")
result = calculate_budget.invoke({
    "total_budget": 2000.0,
    "expenses": "hotel:600, flights:800, food:300"
})
print(result)

print("\n=== Testing Save Itinerary ===")
result = save_itinerary.invoke({
    "itinerary_text": "# Test Trip\n\nDay 1: Arrive in Tokyo",
    "filename": "test_trip.md"
})
print(result)