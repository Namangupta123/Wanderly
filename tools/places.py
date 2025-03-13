# To find Places to Visit
import os
import requests
import json
from datetime import datetime
from config import SERPAPI_API_KEY
def get_attractions(destination, activity_preferences, special_requirements=None):
    """
    Get attractions and places to visit for the specified destination based on preferences.
    
    Args:
        destination (str): The destination city/country
        activity_preferences (list): List of preferred activity types
        special_requirements (str, optional): Any special requirements or interests
        
    Returns:
        dict: A dictionary of attractions categorized by type
    """
    try:
        # Prepare the SerpAPI request
        serpapi_key = SERPAPI_API_KEY
        if not serpapi_key:
            raise ValueError("SerpAPI key is not set")
        
        # Initialize attractions dictionary
        attractions = {preference: [] for preference in activity_preferences}
        
        # Make separate API requests for each activity preference
        for preference in activity_preferences:
            # Construct the search query for attractions
            query = f"best {preference} in {destination}"
            
            params = {
                "engine": "google_maps",
                "q": query,
                "type": "search",
                "api_key": serpapi_key
            }
            
            # Make the API request
            response = requests.get("https://serpapi.com/search", params=params)
            
            if response.status_code != 200:
                raise Exception(f"API request failed with status code {response.status_code}")
            
            data = response.json()
            
            # Process the attraction data
            if "local_results" in data and data["local_results"]:
                for place in data["local_results"]:
                    attraction = {
                        "name": place.get("title", "Unknown Attraction"),
                        "rating": place.get("rating", "N/A"),
                        "reviews": place.get("reviews", "N/A"),
                        "address": place.get("address", "N/A"),
                        "description": place.get("description", f"A popular {preference} attraction"),
                        "type": preference,
                        "estimated_cost": estimate_attraction_cost(preference),
                        "estimated_duration": estimate_attraction_duration(preference),
                        "best_time": suggest_best_time(preference)
                    }
                    attractions[preference].append(attraction)
            
            # If no results or not enough for this preference, add some sample attractions
            if len(attractions[preference]) < 5:
                sample_attractions = generate_sample_attractions(destination, preference, 5 - len(attractions[preference]))
                attractions[preference].extend(sample_attractions)
        
        return attractions
        
    except Exception as e:
        print(f"Error fetching attractions: {str(e)}")
        # Return some fallback attractions in case of error
        return generate_fallback_attractions(destination, activity_preferences)

def estimate_attraction_cost(attraction_type):
    """Estimate the cost range for an attraction based on its type"""
    cost_ranges = {
        "Historical sites": {"min": 10, "max": 25},
        "Museums": {"min": 15, "max": 30},
        "Nature": {"min": 0, "max": 15},
        "Adventure": {"min": 30, "max": 100},
        "Shopping": {"min": 0, "max": 0},  # Cost depends on purchases
        "Relaxation": {"min": 20, "max": 80},
        "Nightlife": {"min": 20, "max": 50}
    }
    
    range_data = cost_ranges.get(attraction_type, {"min": 10, "max": 30})
    return {"min": range_data["min"], "max": range_data["max"]}

def estimate_attraction_duration(attraction_type):
    """Estimate the typical duration for an attraction based on its type"""
    durations = {
        "Historical sites": "2-3 hours",
        "Museums": "2-4 hours",
        "Nature": "3-5 hours",
        "Adventure": "4-6 hours",
        "Shopping": "2-4 hours",
        "Relaxation": "2-3 hours",
        "Nightlife": "3-5 hours"
    }
    
    return durations.get(attraction_type, "2-3 hours")

def suggest_best_time(attraction_type):
    """Suggest the best time to visit an attraction based on its type"""
    best_times = {
        "Historical sites": "Morning",
        "Museums": "Morning or Afternoon",
        "Nature": "Morning or Late Afternoon",
        "Adventure": "Morning",
        "Shopping": "Afternoon",
        "Relaxation": "Afternoon",
        "Nightlife": "Evening"
    }
    
    return best_times.get(attraction_type, "Any time")

def generate_sample_attractions(destination, preference, count):
    """Generate sample attraction data based on preference"""
    sample_attractions = []
    
    # Different attraction names based on preference
    attraction_names = {
        "Historical sites": [
            f"{destination} Castle", 
            f"Ancient {destination} Ruins", 
            f"{destination} Historical Museum", 
            f"Old Town {destination}", 
            f"{destination} Cathedral"
        ],
        "Museums": [
            f"{destination} Art Gallery", 
            f"{destination} Science Museum", 
            f"Museum of {destination} History", 
            f"Modern Art Museum", 
            f"National Museum of {destination}"
        ],
        "Nature": [
            f"{destination} National Park", 
            f"{destination} Botanical Gardens", 
            f"{destination} Lake", 
            f"Mount {destination}", 
            f"{destination} Beach"
        ],
        "Adventure": [
            f"{destination} Zipline Adventure", 
            f"{destination} Rafting Experience", 
            f"Hiking Trails of {destination}", 
            f"{destination} Rock Climbing", 
            f"{destination} Safari"
        ],
        "Shopping": [
            f"{destination} Mall", 
            f"{destination} Market", 
            f"Boutique Street of {destination}", 
            f"{destination} Shopping District", 
            f"Artisan Market of {destination}"
        ],
        "Relaxation": [
            f"{destination} Spa", 
            f"{destination} Hot Springs", 
            f"Wellness Center of {destination}", 
            f"{destination} Beach Resort", 
            f"Meditation Retreat in {destination}"
        ],
        "Nightlife": [
            f"{destination} Club District", 
            f"Jazz Bars of {destination}", 
            f"{destination} Night Market", 
            f"Rooftop Bars in {destination}", 
            f"{destination} Theater District"
        ]
    }
    
    # Use the appropriate list or default to a generic one
    names_list = attraction_names.get(preference, [f"{destination} Attraction {i+1}" for i in range(5)])
    
    for i in range(count):
        name = names_list[i % len(names_list)]
        cost_data = estimate_attraction_cost(preference)
        
        sample_attractions.append({
            "name": name,
            "rating": round(4.0 + (i % 3) * 0.3, 1),  # Ratings between 4.0 and 4.9
            "reviews": (i + 1) * 100,
            "address": f"Sample Address {i+1}, {destination}",
            "description": f"A popular {preference.lower()} attraction in {destination}",
            "type": preference,
            "estimated_cost": cost_data,
            "estimated_duration": estimate_attraction_duration(preference),
            "best_time": suggest_best_time(preference)
        })
    
    return sample_attractions

def generate_fallback_attractions(destination, activity_preferences):
    """Generate fallback attractions in case of API failure"""
    attractions = {}
    
    for preference in activity_preferences:
        attractions[preference] = generate_sample_attractions(destination, preference, 3)
    
    return attractions