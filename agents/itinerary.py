import json
from datetime import datetime, timedelta
from fpdf import FPDF
from groq import Groq
import os

def generate_itinerary(user_preferences, transportation_options, accommodation_options, food_recommendations, attractions):
    """
    Generate a complete itinerary based on user preferences and gathered data using Groq AI.
    """
    try:
        groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        if not groq_client.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        system_prompt = """
        You are a travel expert creating a detailed itinerary for a trip. Based on the user preferences and data provided (transportation, accommodations, food, and attractions), create a comprehensive day-by-day itinerary that maximizes the travel experience while staying within budget constraints. Return the itinerary in strict JSON format with the following structure:
        {
            "destination": "string",
            "dates": "string",
            "total_budget": float,
            "days": [
                {
                    "day": int,
                    "date": "YYYY-MM-DD",
                    "transportation": [{"type": "string", "from": "string", "to": "string", "cost": float}],
                    "accommodation": {"name": "string", "description": "string", "cost": float},
                    "activities": [{"time": "string", "activity": "string", "description": "string", "location": "string", "cost": float}],
                    "meals": [{"type": "string", "recommendation": "string", "cuisine": "string", "cost": float}],
                    "daily_total": float
                }
            ],
            "total_cost": float,
            "remaining_budget": float
        }
        Ensure all costs are numbers (not strings with $), and wrap the JSON in ```json``` markers.
        """

        user_prompt = f"""
        Route: {user_preferences['departure_city']} to {user_preferences['destination']}
        Travel dates: {user_preferences['start_date']} to {user_preferences['end_date']} ({user_preferences['num_days']} days)
        Total Budget: ${user_preferences['budget']} USD
        Transport Budget: ${user_preferences['transport_budget']} USD
        Accommodation Budget: ${user_preferences['accommodation_budget']} USD
        Food Budget: ${user_preferences['food_budget']} USD
        Activities Budget: ${user_preferences['activities_budget']} USD
        Accommodation preference: {user_preferences['accommodation']}
        Food preference: {user_preferences['food']}
        Special requirements: {user_preferences['special_requirements']}
        Transportation mode: {user_preferences['transportation_mode']}
        
        Available data:
        TRANSPORTATION OPTIONS: {json.dumps(transportation_options, indent=2)}
        ACCOMMODATION OPTIONS: {json.dumps(accommodation_options, indent=2)}
        FOOD RECOMMENDATIONS: {json.dumps(food_recommendations, indent=2)}
        ATTRACTIONS: {json.dumps(attractions, indent=2)}
        """

        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )

        itinerary_text = response.choices[0].message.content.strip()
        print("Text returned by Groq: ")
        print(itinerary_text)
        if "```json" in itinerary_text:
            json_start = itinerary_text.index("```json") + 7
            json_end = itinerary_text.rindex("```")
            itinerary_text = itinerary_text[json_start:json_end].strip()

        try:
            itinerary = json.loads(itinerary_text)
            itinerary["user_preferences"] = user_preferences
        except json.JSONDecodeError as e:
            print(f"Invalid JSON response from Groq: {itinerary_text}")
            raise ValueError(f"Failed to parse Groq response as JSON: {str(e)}")

        return itinerary

    except Exception as e:
        print(f"Error generating itinerary: {str(e)}")
        return generate_fallback_itinerary(user_preferences)

def generate_pdf_itinerary(itinerary):
    """
    Generate a PDF from the itinerary data
    """
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, f"Wanderly Itinerary: {itinerary['user_preferences']['departure_city']} to {itinerary['destination']}", 0, 1, "C")
    pdf.cell(190, 10, f"{itinerary['dates']}", 0, 1, "C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "Trip Summary", 0, 1)
    pdf.set_font("Arial", "", 12)
    pdf.cell(190, 10, f"Total Budget: ${itinerary['total_budget']}", 0, 1)
    pdf.cell(190, 10, f"Estimated Cost: ${itinerary['total_cost']}", 0, 1)
    pdf.cell(190, 10, f"Remaining Budget: ${itinerary['remaining_budget']}", 0, 1)
    pdf.ln(10)
    
    for day in itinerary['days']:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, f"Day {day['day']} - {day['date']}", 0, 1)
        pdf.ln(5)
        
        if day.get('transportation'):
            pdf.set_font("Arial", "B", 12)
            pdf.cell(190, 10, "Transportation", 0, 1)
            pdf.set_font("Arial", "", 12)
            for transport in day['transportation']:
                pdf.cell(190, 10, f"{transport['type']}: {transport['from']} to {transport['to']} - ${transport['cost']}", 0, 1)
            pdf.ln(5)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "Accommodation", 0, 1)
        pdf.set_font("Arial", "", 12)
        pdf.cell(190, 10, f"{day['accommodation']['name']} - ${day['accommodation']['cost']}", 0, 1)
        pdf.multi_cell(190, 10, f"{day['accommodation']['description']}")
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "Activities", 0, 1)
        pdf.set_font("Arial", "", 12)
        for activity in day['activities']:
            pdf.set_font("Arial", "B", 11)
            pdf.cell(190, 10, f"{activity['time']}: {activity['activity']} - ${activity['cost']}", 0, 1)
            pdf.set_font("Arial", "", 11)
            pdf.multi_cell(190, 10, f"{activity['description']} at {activity['location']}")
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "Meals", 0, 1)
        pdf.set_font("Arial", "", 12)
        for meal in day['meals']:
            pdf.cell(190, 10, f"{meal['type']}: {meal['recommendation']} ({meal['cuisine']}) - ${meal['cost']}", 0, 1)
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, f"Daily Total: ${day['daily_total']}", 0, 1)
        pdf.ln(10)
    
    return pdf.output(dest="S").encode("latin1")

def generate_fallback_itinerary(user_preferences):
    """Generate a fallback itinerary in case the main generation fails"""
    try:
        departure_city = user_preferences["departure_city"]
        destination = user_preferences["destination"]
        start_date = datetime.strptime(user_preferences["start_date"], "%Y-%m-%d")
        end_date = datetime.strptime(user_preferences["end_date"], "%Y-%m-%d")
        num_days = user_preferences["num_days"]
        budget = float(user_preferences["budget"])
        
        if num_days <= 0:
            raise ValueError("Number of days must be positive")
            
        daily_budget = budget / num_days
        
        itinerary = {
            "user_preferences": user_preferences,
            "destination": destination,
            "dates": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "total_budget": budget,
            "days": [],
            "total_cost": 0.0,
            "remaining_budget": budget
        }
        
        current_date = start_date
        total_cost = 0.0
        
        for day in range(1, num_days + 1):
            accommodation_cost = daily_budget * 0.4
            
            activities = [
                {"time": "Morning", "activity": f"Explore {destination}", "description": "City sightseeing", "location": destination, "cost": daily_budget * 0.1},
                {"time": "Afternoon", "activity": "Local Culture", "description": "Visit a museum or market", "location": destination, "cost": daily_budget * 0.1},
                {"time": "Evening", "activity": "Relax", "description": "Evening stroll", "location": destination, "cost": daily_budget * 0.05}
            ]
            activity_cost_total = sum(a["cost"] for a in activities)
            
            meals = [
                {"type": "Breakfast", "recommendation": "Local Cafe", "cuisine": user_preferences["food"], "cost": daily_budget * 0.1},
                {"type": "Lunch", "recommendation": "Street Food", "cuisine": user_preferences["food"], "cost": daily_budget * 0.1},
                {"type": "Dinner", "recommendation": "Restaurant", "cuisine": user_preferences["food"], "cost": daily_budget * 0.15}
            ]
            meal_cost_total = sum(m["cost"] for m in meals)
            
            transportation = (
                [{"type": user_preferences["transportation_mode"].title(), "from": departure_city, "to": destination, "cost": daily_budget * 0.3}] if day == 1 else
                [{"type": user_preferences["transportation_mode"].title(), "from": destination, "to": departure_city, "cost": daily_budget * 0.3}] if day == num_days else
                [{"type": "Local Transport", "from": "Accommodation", "to": "Various Locations", "cost": daily_budget * 0.1}]
            )
            transportation_cost = sum(t["cost"] for t in transportation)
            
            daily_total = accommodation_cost + activity_cost_total + meal_cost_total + transportation_cost
            total_cost += daily_total
            
            itinerary["days"].append({
                "day": day,
                "date": current_date.strftime("%Y-%m-%d"),
                "transportation": transportation,
                "accommodation": {"name": f"{destination} Hotel", "description": "Standard stay", "cost": accommodation_cost},
                "activities": activities,
                "meals": meals,
                "daily_total": round(daily_total, 2)
            })
            current_date += timedelta(days=1)
        
        itinerary["total_cost"] = round(total_cost, 2)
        itinerary["remaining_budget"] = round(budget - total_cost, 2)
        
        return itinerary
    
    except Exception as e:
        print(f"Error in fallback itinerary: {str(e)}")
        return {
            "user_preferences": user_preferences,
            "destination": user_preferences.get("destination", "Unknown"),
            "dates": "N/A",
            "total_budget": 0,
            "days": [],
            "total_cost": 0.0,
            "remaining_budget": 0.0
        }