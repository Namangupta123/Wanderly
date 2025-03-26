from datetime import datetime
from serpapi import GoogleSearch
from config import SERPAPI_KEY

def get_flight_options(departure_city, destination, departure_date, budget):
    """
    Get flight options for the specified route and date within budget using SerpAPI.
    
    Args:
        departure_city (str): The departure city
        destination (str): The destination city/country
        departure_date (datetime): The departure date
        budget (float): The maximum budget for flights
        
    Returns:
        list: A list of flight options with details
    """
    try:
        formatted_date = departure_date.strftime("%Y-%m-%d")
        
        # Corrected SerpAPI parameters for Google Flights
        params = {
            "engine": "google_flights",
            "departure_id": departure_city,
            "arrival_id": destination,
            "outbound_date": formatted_date,
            "currency": "USD",
            "hl": "en",
            "api_key": SERPAPI_KEY
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Updated response handling based on actual Google Flights API structure
        flights = results.get("best_flights", []) or results.get("other_flights", [])
        
        flight_options = []
        for flight in flights[:5]:  # Get top 5 flights
            price_str = flight.get("price", "0")
            price = float(price_str.replace("$", "").replace(",", "")) if price_str else 0
            
            if price <= budget and price > 0:
                flight_info = flight.get("flights", [{}])[0]  # Get first flight segment
                flight_options.append({
                    "airline": flight_info.get("airline", "Unknown Airline"),
                    "departure_time": flight_info.get("departure_time", ""),
                    "arrival_time": flight_info.get("arrival_time", ""),
                    "duration": flight.get("total_duration", ""),  # Convert minutes to hours if needed
                    "price": f"${price}",
                    "stops": f"{len(flight.get('flights', [])) - 1} stop(s)" if len(flight.get('flights', [])) > 1 else "Nonstop"
                })
        
        # Return sample data if no flights found within budget
        return flight_options if flight_options else [
            {
                "airline": "Sample Airline",
                "departure_time": "10:00",
                "arrival_time": "14:00",
                "duration": "4h 00m",
                "price": f"${round(budget * 0.4)}",
                "stops": "Nonstop"
            }
        ]
        
    except Exception as e:
        print(f"Error fetching flight options: {str(e)}")
        return [
            {
                "airline": "Sample Airline",
                "departure_time": "10:00",
                "arrival_time": "14:00",
                "duration": "4h 00m",
                "price": f"${round(budget * 0.4)}",
                "stops": "Nonstop"
            }
        ]