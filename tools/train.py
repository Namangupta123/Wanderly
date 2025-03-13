import os
import requests
import json
from datetime import datetime
from config import SERPAPI_API_KEY

def get_train_options(departure_city, destination, departure_date, budget):
    """
    Get train options for the specified route and date within budget.
    
    Args:
        departure_city (str): The departure city
        destination (str): The destination city/country
        departure_date (datetime): The departure date
        budget (float): The maximum budget for train tickets
        
    Returns:
        list: A list of train options with details
    """
    try:
        # Format the date for API request
        formatted_date = departure_date.strftime("%Y-%m-%d")
        
        # Prepare the SerpAPI request
        serpapi_key = SERPAPI_API_KEY
        if not serpapi_key:
            raise ValueError("SerpAPI key is not set")
        
        # Construct the search query for trains
        # Note: SerpAPI doesn't have a direct train search engine, so we'll use a general search
        params = {
            "engine": "google",
            "q": f"train from {departure_city} to {destination} on {formatted_date}",
            "api_key": serpapi_key
        }
        
        # Make the API request
        response = requests.get("https://serpapi.com/search", params=params)
        
        if response.status_code != 200:
            raise Exception(f"API request failed with status code {response.status_code}")
        
        # In a real application, we would parse the actual response from SerpAPI
        # For demonstration purposes, we'll create sample train data
        
        # Generate sample train data
        train_options = []
        sample_train_companies = ["Amtrak", "Eurostar", "Deutsche Bahn", "SNCF", "Trenitalia"]
        sample_times = ["07:30", "09:45", "12:15", "14:50", "17:30"]
        sample_durations = ["3h 15m", "4h 30m", "5h 45m", "6h 20m", "7h 10m"]
        sample_prices = [round(budget * 0.15), round(budget * 0.2), round(budget * 0.25), round(budget * 0.3), round(budget * 0.35)]
        sample_classes = ["Economy", "Business", "First Class", "Economy", "Business"]
        
        for i in range(5):
            train_options.append({
                "company": sample_train_companies[i % len(sample_train_companies)],
                "departure_time": sample_times[i],
                "arrival_time": "Varies",
                "duration": sample_durations[i],
                "price": f"${sample_prices[i]}",
                "class": sample_classes[i],
                "transfers": i % 3  # 0, 1, or 2 transfers
            })
        
        return train_options
        
    except Exception as e:
        print(f"Error fetching train options: {str(e)}")
        # Return some fallback options in case of error
        return [
            {
                "company": "Sample Train Company",
                "departure_time": "09:00 AM",
                "arrival_time": "1:00 PM",
                "duration": "4h 00m",
                "price": f"${round(budget * 0.25)}",
                "class": "Economy",
                "transfers": 0
            }
        ]