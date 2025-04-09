import requests
from datetime import datetime
from config import TRAVEL

def get_flight_options(departure_city, destination, departure_date, budget):
    """
    Get flight options using RapidAPI Google Search for the specified route and date within budget.
    """
    try:
        formatted_date = departure_date.strftime("%Y-%m-%d")
        search_query = f"flights from {departure_city} to {destination} on {formatted_date}"
        
        url = "https://google-search74.p.rapidapi.com/"
        
        querystring = {
            "query": search_query,
            "limit": "10",
            "related_keywords": "true"
        }
        
        headers = {
            "x-rapidapi-key": TRAVEL,
            "x-rapidapi-host": "google-search74.p.rapidapi.com"
        }
        
        response = requests.get(url, headers=headers, params=querystring)
        results = response.json()
        flights = []
        for result in results.get('results', [])[:5]:
            title = result.get('title', '')
            description = result.get('description', '')
            price = budget * 0.4
            price_index = description.find('$')
            if price_index != -1:
                try:
                    price_str = description[price_index:].split()[0].replace('$', '').replace(',', '')
                    extracted_price = float(price_str)
                    if extracted_price <= budget:
                        price = extracted_price
                except ValueError:
                    pass
            
            if price <= budget:
                flights.append({
                    "airline": title.split('-')[0].strip() if '-' in title else "Various Airlines",
                    "departure_time": "Morning",
                    "arrival_time": "Afternoon",
                    "duration": "NA",
                    "price": f"${price:.2f}",
                    "stops": "Direct"
                })
        
        return flights if flights else [
            {
                "airline": "Sample Airline",
                "departure_time": "10:00",
                "arrival_time": "14:00",
                "duration": "4h 00m",
                "price": f"${round(budget * 0.4, 2)}",
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
                "price": f"${round(budget * 0.4, 2)}",
                "stops": "Nonstop"
            }
        ]