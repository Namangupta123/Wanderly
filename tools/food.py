from datetime import datetime
from langchain.chains import LLMChain
from langchain_mistralai import ChatMistralAI
from langchain.prompts import PromptTemplate
from config import MISTRAL_FOOD_KEY

def get_food_recommendations(destination, food_preference, special_requirements=None):
    """
    Get food recommendations using MistralAI for the specified destination based on preferences.
    
    Args:
        destination (str): The destination city/country
        food_preference (str): The type of food preferred (e.g., "Local cuisine", "Fine dining")
        special_requirements (str, optional): Any special dietary requirements
        
    Returns:
        dict: A dictionary of food recommendations categorized by meal type
    """
    try:
        llm = ChatMistralAI(
            model="mistral-large-latest",
            api_key=MISTRAL_FOOD_KEY
        )
        
        template = """
        You are a local food expert providing restaurant recommendations in {destination}.
        
        Details:
        - Location: {destination}
        - Food preference: {food_preference}
        - Special requirements: {special_requirements}

        Provide restaurant recommendations for each meal type (Breakfast, Lunch, Dinner).
        For each meal type, suggest 3-4 restaurants with the following details:
        - Restaurant name
        - Rating (1-5 stars)
        - Number of reviews
        - Address
        - Price level ($, $$, $$$, $$$$)
        - Cuisine type
        - Brief description

        Format the response as a JSON object with meal types as keys, each containing an array of restaurant objects:
        {
            "Breakfast": [
                {
                    "name": string,
                    "rating": number,
                    "reviews": number,
                    "address": string,
                    "price_level": string,
                    "cuisine": string,
                    "description": string
                }
            ],
            "Lunch": [...],
            "Dinner": [...]
        }

        Only return the JSON object, nothing else.
        Consider the specified food preference and any dietary requirements.
        Use realistic restaurant names and locations in {destination}.
        Ensure recommendations match the local food scene and culture.
        """
        
        prompt = PromptTemplate(
            input_variables=["destination", "food_preference", "special_requirements"],
            template=template
        )
        
        chain = LLMChain(llm=llm, prompt=prompt)
        
        response = chain.run({
            "destination": destination,
            "food_preference": food_preference,
            "special_requirements": special_requirements if special_requirements else "None"
        })
        
        import json
        recommendations = json.loads(response)
        
        return recommendations
        
    except Exception as e:
        print(f"Error fetching food recommendations: {str(e)}")
        return {
            "Breakfast": [
                {
                    "name": f"{destination} Morning Café",
                    "rating": 4.3,
                    "reviews": 120,
                    "address": f"123 Main St, {destination}",
                    "price_level": "$",
                    "cuisine": food_preference,
                    "description": f"A cozy breakfast spot serving {food_preference.lower()} morning favorites"
                }
            ],
            "Lunch": [
                {
                    "name": f"Midday Bistro",
                    "rating": 4.5,
                    "reviews": 250,
                    "address": f"456 Center Ave, {destination}",
                    "price_level": "$$",
                    "cuisine": food_preference,
                    "description": f"Popular lunch destination with {food_preference.lower()} options"
                }
            ],
            "Dinner": [
                {
                    "name": f"Evening Delights",
                    "rating": 4.7,
                    "reviews": 350,
                    "address": f"789 Plaza Rd, {destination}",
                    "price_level": "$$$",
                    "cuisine": food_preference,
                    "description": f"Elegant dinner venue featuring the best of {food_preference.lower()}"
                }
            ]
        }