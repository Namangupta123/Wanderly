import json
from datetime import datetime, timedelta
from fpdf import FPDF
from langchain.chains import LLMChain
from langchain.schema.runnable import RunnableSequence
from langchain_mistralai import ChatMistralAI
from langchain.prompts import PromptTemplate
from config import MISTRAL_ITINERARY_KEY

def generate_itinerary(user_preferences, transportation_options, accommodation_options, food_recommendations, attractions):
    """
    Generate a complete itinerary based on user preferences and gathered data.
    """
    try:
        llm = ChatMistralAI(
            model="mistral-large-latest",
            api_key=MISTRAL_ITINERARY_KEY,
            temperature=0.7,
            max_tokens=4096
        )
        
        template = """
        You are a travel expert creating a detailed itinerary for a trip.
        
        Route: {departure_city} to {destination}
        Travel dates: {start_date} to {end_date} ({num_days} days)
        Total Budget: ${budget} USD
        Transport Budget: ${transport_budget} USD
        Accommodation Budget: ${accommodation_budget} USD
        Food Budget: ${food_budget} USD
        Activities Budget: ${activities_budget} USD
        Accommodation preference: {accommodation_preference}
        Food preference: {food_preference}
        Special requirements: {special_requirements}
        Transportation mode: {transportation_mode}
        
        I have gathered the following information for you to use:
        
        TRANSPORTATION OPTIONS:
        {transportation_options}
        
        ACCOMMODATION OPTIONS:
        {accommodation_options}
        
        FOOD RECOMMENDATIONS:
        {food_recommendations}
        
        ATTRACTIONS:
        {attractions}
        
        Create a detailed day-by-day itinerary including:
        1. Transportation details for arrival and departure
        2. Recommended accommodations within budget
        3. Daily activities and attractions with approximate costs
        4. Restaurant recommendations for each meal
        5. Local transportation options between locations
        6. Estimated costs for each day
        
        Format the response as a JSON object with the following structure:
        {{
            "user_preferences": {{
                "departure_city": "Departure city name",
                "destination": "Destination name"
            }},
            "destination": "Full destination name",
            "dates": "Start date to end date",
            "total_budget": {budget},
            "days": [
                {{
                    "day": 1,
                    "date": "YYYY-MM-DD",
                    "accommodation": {{
                        "name": "Name of hotel/accommodation",
                        "description": "Brief description",
                        "cost": 0.0
                    }},
                    "activities": [
                        {{
                            "time": "Morning/Afternoon/Evening",
                            "activity": "Name of activity",
                            "description": "Brief description",
                            "location": "Location name",
                            "cost": 0.0
                        }}
                    ],
                    "meals": [
                        {{
                            "type": "Breakfast/Lunch/Dinner",
                            "recommendation": "Restaurant name",
                            "cuisine": "Type of cuisine",
                            "cost": 0.0
                        }}
                    ],
                    "transportation": [
                        {{
                            "type": "Type of transportation",
                            "from": "Starting point",
                            "to": "Destination",
                            "cost": 0.0
                        }}
                    ],
                    "daily_total": 0.0
                }}
            ],
            "total_cost": 0.0,
            "remaining_budget": 0.0
        }}
        
        Ensure all costs are realistic and within their respective budgets:
        - Transportation costs should not exceed ${transport_budget} USD
        - Accommodation costs should not exceed ${accommodation_budget} USD
        - Food costs should not exceed ${food_budget} USD
        - Activities costs should not exceed ${activities_budget} USD
        
        Only return the JSON object, nothing else.
        """
        
        prompt = PromptTemplate(
            input_variables=[
                "departure_city", "destination", "start_date", "end_date", "num_days",
                "budget", "transport_budget", "accommodation_budget", "food_budget", "activities_budget",
                "accommodation_preference", "food_preference", "special_requirements",
                "transportation_mode", "transportation_options", "accommodation_options",
                "food_recommendations", "attractions"
            ],
            template=template
        )
        
        chain = prompt | llm
        
        input_data = {
            "departure_city": user_preferences["departure_city"],
            "destination": user_preferences["destination"],
            "start_date": user_preferences["start_date"],
            "end_date": user_preferences["end_date"],
            "num_days": user_preferences["num_days"],
            "budget": user_preferences["budget"],
            "transport_budget": user_preferences["transport_budget"],
            "accommodation_budget": user_preferences["accommodation_budget"],
            "food_budget": user_preferences["food_budget"],
            "activities_budget": user_preferences["activities_budget"],
            "accommodation_preference": user_preferences["accommodation"],
            "food_preference": user_preferences["food"],
            "special_requirements": user_preferences.get("special_requirements", "None"),
            "transportation_mode": user_preferences["transportation_mode"],
            "transportation_options": json.dumps(transportation_options, indent=2),
            "accommodation_options": json.dumps(accommodation_options, indent=2),
            "food_recommendations": json.dumps(food_recommendations, indent=2),
            "attractions": json.dumps(attractions, indent=2)
        }
        
        response = chain.invoke(input_data)
        
        # Handle case where response might not be valid JSON
        try:
            itinerary = json.loads(response.content if hasattr(response, 'content') else str(response))
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON response from LLM")
        
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
        
        if day['day'] == 1 or day['day'] == len(itinerary['days']):
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
        
        if day['day'] != 1 and day['day'] != len(itinerary['days']):
            pdf.set_font("Arial", "B", 12)
            pdf.cell(190, 10, "Local Transportation", 0, 1)
            pdf.set_font("Arial", "", 12)
            for transport in day['transportation']:
                pdf.cell(190, 10, f"{transport['type']}: {transport['from']} to {transport['to']} - ${transport['cost']}", 0, 1)
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
        budget = float(user_preferences["budget"])  # Ensure budget is float
        
        if num_days <= 0:
            raise ValueError("Number of days must be positive")
            
        daily_budget = budget / num_days
        
        itinerary = {
            "user_preferences": {
                "departure_city": departure_city,
                "destination": destination
            },
            "destination": destination,
            "dates": f"{user_preferences['start_date']} to {user_preferences['end_date']}",
            "total_budget": budget,
            "days": [],
            "total_cost": 0.0,
            "remaining_budget": budget
        }
        
        current_date = start_date
        total_cost = 0.0
        
        for day in range(1, num_days + 1):
            accommodation_cost = daily_budget * 0.4
            
            activities = []
            activity_times = ["Morning", "Afternoon", "Evening"]
            activity_cost_total = 0.0
            
            for i, time in enumerate(activity_times):
                activity_cost = daily_budget * 0.1
                activity_cost_total += activity_cost
                activities.append({
                    "time": time,
                    "activity": f"Explore {destination} - Activity {i+1}",
                    "description": f"Enjoy the sights and experiences of {destination}",
                    "location": f"{destination} - Location {i+1}",
                    "cost": round(activity_cost, 2)
                })
            
            meals = []
            meal_types = ["Breakfast", "Lunch", "Dinner"]
            meal_cost_total = 0.0
            
            for i, meal_type in enumerate(meal_types):
                meal_cost = daily_budget * 0.1
                meal_cost_total += meal_cost
                meals.append({
                    "type": meal_type,
                    "recommendation": f"{destination} Restaurant {i+1}",
                    "cuisine": user_preferences["food"],
                    "cost": round(meal_cost, 2)
                })
            
            if day == 1:
                transportation = [{
                    "type": user_preferences["transportation_mode"].title(),
                    "from": departure_city,
                    "to": destination,
                    "cost": round(daily_budget * 0.3, 2)
                }]
            elif day == num_days:
                transportation = [{
                    "type": user_preferences["transportation_mode"].title(),
                    "from": destination,
                    "to": departure_city,
                    "cost": round(daily_budget * 0.3, 2)
                }]
            else:
                transportation = [{
                    "type": "Local Transport",
                    "from": "Accommodation",
                    "to": "Various Locations",
                    "cost": round(daily_budget * 0.1, 2)
                }]
            
            transportation_cost = sum(t["cost"] for t in transportation)
            
            daily_total = accommodation_cost + activity_cost_total + meal_cost_total + transportation_cost
            total_cost += daily_total
            
            itinerary["days"].append({
                "day": day,
                "date": current_date.strftime("%Y-%m-%d"),
                "accommodation": {
                    "name": f"{destination} Hotel",
                    "description": f"Standard accommodation in {destination}",
                    "cost": round(accommodation_cost, 2)
                },
                "activities": activities,
                "meals": meals,
                "transportation": transportation,
                "daily_total": round(daily_total, 2)
            })
            
            current_date += timedelta(days=1)
        
        itinerary["total_cost"] = round(total_cost, 2)
        itinerary["remaining_budget"] = round(budget - total_cost, 2)
        
        return itinerary
    
    except Exception as e:
        print(f"Error in fallback itinerary: {str(e)}")
        return {
            "user_preferences": {
                "departure_city": user_preferences.get("departure_city", "Unknown"),
                "destination": user_preferences.get("destination", "Unknown")
            },
            "destination": user_preferences.get("destination", "Unknown"),
            "dates": "N/A",
            "total_budget": 0,
            "days": [],
            "total_cost": 0.0,
            "remaining_budget": 0.0
        }