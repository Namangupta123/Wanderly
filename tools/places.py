from datetime import datetime
from langchain.chains import LLMChain
from langchain_mistralai import ChatMistralAI
from langchain.schema.runnable import RunnableSequence
from langchain.prompts import PromptTemplate
from config import MISTRAL_PLACES_KEY

def get_attractions(destination, activity_preferences, special_requirements=None):
    """
    Get attractions and places to visit using MistralAI for the specified destination based on preferences.
    
    Args:
        destination (str): The destination city/country
        activity_preferences (list): List of preferred activity types
        special_requirements (str, optional): Any special requirements or interests
        
    Returns:
        dict: A dictionary of attractions categorized by type
    """
    try:
        llm = ChatMistralAI(
            model="mistral-large-2411",
            api_key=MISTRAL_PLACES_KEY
        )
        
        template = """
        You are a local tourism expert providing attraction recommendations in {destination}.
        
        Details:
        - Location: {destination}
        - Activity preferences: {activity_preferences}
        - Special requirements: {special_requirements}

        For each activity type, provide 3-5 attractions with the following details:
        - Name
        - Rating (1-5 stars)
        - Number of reviews
        - Address
        - Description
        - Type of activity
        - Estimated cost range
        - Estimated duration
        - Best time to visit

        Format the response as a JSON object with activity types as keys, each containing an array of attraction objects:
        {
            "activity_type": [
                {
                    "name": string,
                    "rating": number,
                    "reviews": number,
                    "address": string,
                    "description": string,
                    "type": string,
                    "estimated_cost": {"min": number, "max": number},
                    "estimated_duration": string,
                    "best_time": string
                }
            ]
        }

        Only return the JSON object, nothing else.
        Use realistic attraction names and locations in {destination}.
        Consider local weather patterns and seasonal events for best visit times.
        Provide accurate cost estimates in USD.
        """
        
        prompt = PromptTemplate(
            input_variables=["destination", "activity_preferences", "special_requirements"],
            template=template
        )
        
        chain = prompt|llm
        
        response = chain.invoke({
            "destination": destination,
            "activity_preferences": ", ".join(activity_preferences),
            "special_requirements": special_requirements if special_requirements else "None"
        })
        
        import json
        attractions = json.loads(response)
        
        return attractions
        
    except Exception as e:
        print(f"Error fetching attractions: {str(e)}")
        fallback_attractions = {}
        for preference in activity_preferences:
            fallback_attractions[preference] = [
                {
                    "name": f"{destination} {preference}",
                    "rating": 4.5,
                    "reviews": 200,
                    "address": f"123 Tourist St, {destination}",
                    "description": f"A popular {preference.lower()} attraction in {destination}",
                    "type": preference,
                    "estimated_cost": {"min": 10, "max": 30},
                    "estimated_duration": "2-3 hours",
                    "best_time": "Morning"
                }
            ]
        return fallback_attractions