import requests
import json
from typing import Dict, List
from config import RAPIDAPI_KEY

class PlacesAPI:
    def __init__(self):
        self.api_key = RAPIDAPI_KEY
        self.base_url = "https://google-map-places-new-v2.p.rapidapi.com/v1/places:autocomplete"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "google-map-places-new-v2.p.rapidapi.com",
            "Content-Type": "application/json",
            "X-Goog-FieldMask": "*"
        }

    def search_places(self, query: str, lat: float, lon: float, radius: int = 10000) -> List[Dict]:
        payload = {
            "input": query,
            "locationBias": {
                "circle": {
                    "center": {
                        "latitude": lat,
                        "longitude": lon
                    },
                    "radius": radius
                }
            },
            "includeQueryPredictions": True
        }

        try:
            response = requests.post(self.base_url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json().get('places', [])
        except Exception as e:
            print(f"Error fetching places: {e}")
            return []

def get_attractions(destination, activity_preferences, special_requirements=None):
    """
    Get attractions and places to visit using RapidAPI for the specified destination based on preferences.
    """
    try:
        sample_coordinates = {
            "New York": (40.7128, -74.0060),
            "London": (51.5074, -0.1278),
            "Tokyo": (35.6762, 139.6503),
            "Paris": (48.8566, 2.3522),
            "Rome": (41.9028, 12.4964),
            "Sydney": (-33.8688, 151.2093),
            "Dubai": (25.2048, 55.2708),
            "Singapore": (1.3521, 103.8198),
            "Hong Kong": (22.3193, 114.1694),
            "Barcelona": (41.3851, 2.1734),
            "New Delhi": (28.6139, 77.2090)
        }
        lat, lon = sample_coordinates.get(destination.split(',')[0].strip(), (40.7128, -74.0060))
        
        places_api = PlacesAPI()
        attractions = {}
        
        for preference in activity_preferences:
            search_query = f"{preference} attractions in {destination}"
            if special_requirements:
                search_query += f" {special_requirements}"
            
            places = places_api.search_places(search_query, lat, lon)
            
            attractions[preference] = []
            for place in places[:3]:
                price_range = {"min": 10, "max": 30}
                if "museum" in preference.lower():
                    price_range = {"min": 15, "max": 45}
                elif "adventure" in preference.lower():
                    price_range = {"min": 50, "max": 150}
                
                attractions[preference].append({
                    "name": place.get("name", f"{destination} {preference}"),
                    "rating": float(place.get("rating", 4.5)),
                    "reviews": int(place.get("user_ratings_total", 200)),
                    "address": place.get("formatted_address", f"123 Tourist St, {destination}"),
                    "description": place.get("editorial_summary", {}).get("overview", 
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