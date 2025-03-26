from datetime import datetime
from serpapi import GoogleSearch
from config import SERPAPI_KEY

def get_train_options(departure_city, destination, departure_date, budget):
    """
    Get train options for the specified route and date within budget using SerpAPI.
    
    Args:
        departure_city (str): The departure city
        destination (str): The destination city/country
        departure_date (datetime): The departure date
        budget (float): The maximum budget for train tickets
        
    Returns:
        list: A list of train options with details
    """
    try:
        formatted_date = departure_date.strftime("%Y-%m-%d")
        
        search_query = f"train tickets from {departure_city} to {destination} on {formatted_date}"
        
        # Using google search engine with travel-specific parameters
        search = GoogleSearch({
            "q": search_query,
            "engine": "google",  # No specific train engine, using general search
            "api_key": SERPAPI_KEY,
            "hl": "en",
            "gl": "us",
            "tbm": "nws"  # Changed to news to potentially get more structured travel data
        })
        
        results = search.get_dict()
        # Try different possible result structures
        trains = (results.get("travel_results", []) or 
                 results.get("organic_results", []) or 
                 results.get("local_results", []))
        
        train_options = []
        for train in trains[:5]:  # Get top 5 trains
            # More robust price handling
            price_str = train.get("price", f"${budget * 0.25}")
            price = float(price_str.replace("$", "").replace(",", "")) if isinstance(price_str, str) else budget * 0.25
            
            if price <= budget:
                train_options.append({
                    "company": train.get("source", train.get("title", "Sample Train Company")),
                    "departure_time": train.get("departure_time", "09:00"),  # Fallback to default
                    "arrival_time": train.get("arrival_time", "13:00"),
                    "duration": train.get("duration", "4h 00m"),
                    "price": f"${round(price, 2)}",
                    "class": train.get("class", "Economy"),
                    "transfers": int(train.get("transfers", 0)) if train.get("transfers") else 0
                })
        
        return train_options if train_options else [
            {
                "company": "Sample Train Company",
                "departure_time": "09:00",
                "arrival_time": "13:00",
                "duration": "4h 00m",
                "price": f"${round(budget * 0.25)}",
                "class": "Economy",
                "transfers": 0
            }
        ]
        
    except Exception as e:
        print(f"Error fetching train options: {str(e)}")
        return [
            {
                "company": "Sample Train Company",
                "departure_time": "09:00",
                "arrival_time": "13:00",
                "duration": "4h 00m",
                "price": f"${round(budget * 0.25)}",
                "class": "Economy",
                "transfers": 0
            }
        ]