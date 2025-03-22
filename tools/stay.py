from datetime import datetime
from langchain.chains import LLMChain
from langchain_mistralai import ChatMistralAI
from langchain.prompts import PromptTemplate
from config import MISTRAL_STAY_KEY

def get_accommodation_options(destination, check_in_date, check_out_date, preference, budget):
    """
    Get accommodation options using MistralAI for the specified destination and dates within budget.
    
    Args:
        destination (str): The destination city/country
        check_in_date (datetime): The check-in date
        check_out_date (datetime): The check-out date
        preference (str): Accommodation preference (Budget, Mid-range, Luxury)
        budget (float): The maximum budget for accommodation
        
    Returns:
        list: A list of accommodation options with details
    """
    try:
        delta = check_out_date - check_in_date
        num_nights = delta.days
        
        daily_accommodation_budget = (budget * 0.4) / num_nights
        
        llm = ChatMistralAI(
            model="mistral-large-latest",
            api_key=MISTRAL_STAY_KEY
        )
        
        template = """
        You are a travel expert providing realistic accommodation options in {destination}.
        
        Details:
        - Check-in: {check_in_date}
        - Check-out: {check_out_date}
        - Number of nights: {num_nights}
        - Preference: {preference} (Budget/Mid-range/Luxury)
        - Daily budget: ${daily_budget} USD

        Provide 5 realistic accommodation options with the following details for each:
        - Hotel/accommodation name
        - Rating (1-5 stars)
        - Number of reviews
        - Address
        - Price per night
        - Total price for the stay
        - Available amenities
        - Brief description

        Format the response as a JSON array of accommodation objects. Each object should have:
        - name: string
        - rating: number
        - reviews: number
        - address: string
        - price_per_night: number
        - total_price: number
        - amenities: array of strings
        - description: string

        Only return the JSON array, nothing else.
        Ensure prices are appropriate for the {preference} category and within budget.
        Use realistic hotel names and locations in {destination}.
        Descriptions should highlight key features and location benefits.
        """
        
        prompt = PromptTemplate(
            input_variables=[
                "destination", "check_in_date", "check_out_date", "num_nights",
                "preference", "daily_budget"
            ],
            template=template
        )
        
        chain = LLMChain(llm=llm, prompt=prompt)
        
        check_in_formatted = check_in_date.strftime("%Y-%m-%d")
        check_out_formatted = check_out_date.strftime("%Y-%m-%d")
        
        response = chain.run({
            "destination": destination,
            "check_in_date": check_in_formatted,
            "check_out_date": check_out_formatted,
            "num_nights": num_nights,
            "preference": preference,
            "daily_budget": daily_accommodation_budget
        })
        
        import json
        accommodations = json.loads(response)
        
        return accommodations
        
    except Exception as e:
        print(f"Error fetching accommodation options: {str(e)}")
        return [
            {
                "name": f"{preference} Hotel {destination}",
                "rating": 4.0,
                "reviews": 150,
                "address": f"123 Main St, {destination}",
                "price_per_night": round(daily_accommodation_budget * 0.8, 2),
                "total_price": round(daily_accommodation_budget * 0.8 * num_nights, 2),
                "amenities": ["WiFi", "Air conditioning", "TV"],
                "description": f"A comfortable {preference.lower()} accommodation in {destination}"
            }
        ]