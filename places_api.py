import requests
import json
from typing import Dict, List

class PlacesAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://google-map-places-new-v2.p.rapidapi.com/v1/places:autocomplete"
        self.headers = {
            "x-rapidapi-key": api_key,
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

    def get_attractions(self, city: str, interests: List[str]) -> Dict[str, List[Dict]]:
        # Hardcoded coordinates for demo - in production, you'd want to geocode the city name
        sample_coordinates = {
            "New York": (40.7128, -74.0060),
            "London": (51.5074, -0.1278),
            "Tokyo": (35.6762, 139.6503),
            "Paris": (48.8566, 2.3522),
            "New Delhi": (28.6139, 77.2090),
            "Mumbai": (19.0760, 72.8777),
            "Bengaluru": (12.9716, 77.5946),
            "Uttarakhand": (30.0668, 79.0193),
            "Bihar": (25.0961, 85.3131),
            "Uttar Pradesh": (26.8467, 80.9462),
            "Kolkata": (22.5726, 88.3639),
            "Stanford": (37.4275, -122.1697),
            "San Francisco": (37.7749, -122.4194),
            "Los Angeles": (34.0522, -118.2437),
            "Chicago": (41.8781, -87.6298),
            "Houston": (29.7633, -95.3632),
            "Phoenix": (33.4484, -112.0739),
            "Philadelphia": (39.9523, -75.1633),
            "San Diego": (32.7157, -117.1611),
            "Dallas": (32.7763, -96.7969),
            "San Jose": (37.3382, -121.8863),
            "Austin": (30.2672, -97.7431),
            "Jacksonville": (30.3322, -81.6551),
            "San Antonio": (29.4241, -98.4937),
            "Indianapolis": (39.7683, -86.1580),
            "Columbus": (39.9612, -82.9988),
            "Fort Worth": (32.7554, -97.3308),
            "Charlotte": (35.2271, -80.8431)
        }

        lat, lon = sample_coordinates.get(city, (0, 0))
        attractions = {}

        for interest in interests:
            query = f"{interest} in {city}"
            places = self.search_places(query, lat, lon)
            attractions[interest] = places[:5]  # Get top 5 results for each interest

        return attractions 