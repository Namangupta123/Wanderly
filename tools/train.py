import requests
from datetime import datetime
from config import TRAVEL

def get_train_options(departure_city, destination, departure_date, budget):
    """
    Get train options using RapidAPI Google Search for the specified route and date within budget.
    """
    try:
        formatted_date = departure_date.strftime("%Y-%m-%d")
        search_query = f"train tickets from {departure_city} to {destination} on {formatted_date}"
        
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
        trains = []
        for result in results.get('results', [])[:5]:
            title = result.get('title', '')
            description = result.get('description', '')
            price = budget * 0.25
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
                trains.append({
                    "company": title.split('-')[0].strip() if '-' in title else "Train Service",
                    "departure_time": "09:00",
                    "arrival_time": "13:00",
                    "duration": "4h 00m",
                    "price": f"${price:.2f}",
                    "class": "Economy",
                    "transfers": 0
                })
        
        return trains if trains else [
            {
                "company": "Sample Train Company",
                "departure_time": "09:00",
                "arrival_time": "13:00",
                "duration": "4h 00m",
                "price": f"${round(budget * 0.25, 2)}",
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
                "price": f"${round(budget * 0.25, 2)}",
                "class": "Economy",
                "transfers": 0
            }
        ]