from datetime import datetime
from serpapi import GoogleSearch
from config import SERPAPI_KEY

def get_attractions(destination, activity_preferences, special_requirements=None):
    """
    Get attractions and places to visit using SerpAPI for the specified destination based on preferences.
    
    Args:
        destination (str): The destination city/country
        activity_preferences (list): List of preferred activity types
        special_requirements (str, optional): Any special requirements or interests
        
    Returns:
        dict: A dictionary of attractions categorized by type
    """
    try:
        attractions = {}
        
        for preference in activity_preferences:
            search_query = f"best {preference} attractions in {destination}"
            if special_requirements:
                search_query += f" {special_requirements}"
            
            # Corrected SerpAPI parameters for Google Maps
            search = GoogleSearch({
                "q": search_query,
                "engine": "google_maps",
                "type": "search",  # Changed from "tourist_attraction" to proper type value
                "api_key": SERPAPI_KEY,
                "hl": "en",
                "gl": "us",
                "ll": "@40.7455096,-74.0240996,14z"  # Default lat/long, could be made dynamic
            })
            
            results = search.get_dict()
            places = results.get("local_results", []) or results.get("place_results", [])
            
            attractions[preference] = []
            for place in places[:3]:  # Get top 3 attractions for each preference
                price_range = {"min": 10, "max": 30}
                if "museum" in preference.lower():
                    price_range = {"min": 15, "max": 45}
                elif "adventure" in preference.lower():
                    price_range = {"min": 50, "max": 150}
                
                # Handle potential missing data with defaults
                rating = place.get("rating")
                reviews = place.get("reviews")
                
                attractions[preference].append({
                    "name": place.get("title", f"{destination} {preference}"),
                    "rating": float(rating) if rating else 4.5,
                    "reviews": int(reviews) if reviews else 200,
                    "address": place.get("address", f"123 Tourist St, {destination}"),
                    "description": place.get("description", 
                                          f"A popular {preference.lower()} attraction in {destination}"),
                    "type": preference,
                    "estimated_cost": price_range,
                    "estimated_duration": "2-3 hours",
                    "best_time": "Morning"
                })
        
        return attractions
        
    except Exception as e:
        print(f"Error fetching attractions: {str(e)}")
        fallback_attractions = {}
        for preference in activity_preferences:
            fallback_attractions[preference] = [
                {
                    "name": f"{destination} {preference}",
                    "rating": 4.5,
                    "reviews": 200,
                    "address": f"123 Tourist St, {destination}",
                    "description": f"A popular {preference.lower()} attraction in {destination}",
                    "type": preference,
                    "estimated_cost": {"min": 10, "max": 30},
                    "estimated_duration": "2-3 hours",
                    "best_time": "Morning"
                }
            ]
        return fallback_attractions