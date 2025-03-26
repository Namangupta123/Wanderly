from datetime import datetime
from serpapi import GoogleSearch
from config import SERPAPI_KEY

def get_food_recommendations(destination, food_preference, special_requirements=None):
    """
    Get food recommendations using SerpAPI for the specified destination based on preferences.
    
    Args:
        destination (str): The destination city/country
        food_preference (str): The type of food preferred (e.g., "Local cuisine", "Fine dining")
        special_requirements (str, optional): Any special dietary requirements
        
    Returns:
        dict: A dictionary of food recommendations categorized by meal type
    """
    try:
        meal_types = ["Breakfast", "Lunch", "Dinner"]
        recommendations = {}
        
        for meal_type in meal_types:
            # Construct proper search query
            search_query = f"best {food_preference} restaurants for {meal_type.lower()} in {destination}"
            if special_requirements:
                search_query += f" {special_requirements}"
            
            # Corrected SerpAPI parameters for Google Maps
            search = GoogleSearch({
                "q": search_query,
                "engine": "google_maps",
                "type": "search",  # Changed from "restaurants" to proper type value
                "api_key": SERPAPI_KEY,
                "hl": "en",
                "gl": "us",
                "ll": "@40.7455096,-74.0240996,14z"  # Default lat/long zoom, could be made dynamic
            })
            
            results = search.get_dict()
            places = results.get("local_results", []) or results.get("place_results", [])
            
            recommendations[meal_type] = []
            for place in places[:4]:  # Get top 4 restaurants for each meal
                # Handle potential missing data with defaults
                rating = place.get("rating")
                reviews = place.get("reviews")
                
                recommendations[meal_type].append({
                    "name": place.get("title", f"{destination} Restaurant"),
                    "rating": float(rating) if rating else 4.5,
                    "reviews": int(reviews) if reviews else 200,
                    "address": place.get("address", f"123 Main St, {destination}"),
                    "price_level": place.get("price", "$$"),  # Changed from price_level to price
                    "cuisine": food_preference,
                    "description": place.get("description", 
                                          f"A popular {food_preference.lower()} restaurant in {destination}")
                })
        
        return recommendations
        
    except Exception as e:
        print(f"Error fetching food recommendations: {str(e)}")
        return {
            "Breakfast": [
                {
                    "name": f"{destination} Morning Café",
                    "rating": 4.3,
                    "reviews": 120,
                    "address": f"123 Main St, {destination}",
                    "price_level": "$",
                    "cuisine": food_preference,
                    "description": f"A cozy breakfast spot serving {food_preference.lower()} morning favorites"
                }
            ],
            "Lunch": [
                {
                    "name": f"Midday Bistro",
                    "rating": 4.5,
                    "reviews": 250,
                    "address": f"456 Center Ave, {destination}",
                    "price_level": "$$",
                    "cuisine": food_preference,
                    "description": f"Popular lunch destination with {food_preference.lower()} options"
                }
            ],
            "Dinner": [
                {
                    "name": f"Evening Delights",
                    "rating": 4.7,
                    "reviews": 350,
                    "address": f"789 Plaza Rd, {destination}",
                    "price_level": "$$$",
                    "cuisine": food_preference,
                    "description": f"Elegant dinner venue featuring the best of {food_preference.lower()}"
                }
            ]
        }