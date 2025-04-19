import json
from datetime import datetime, timedelta
from groq import Groq
import os
from fpdf import FPDF
from config import GROQ_API_KEY
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def generate_itinerary(user_preferences, transportation_options, accommodation_options, food_recommendations, attractions):
    """
    Generate a detailed travel itinerary based on user preferences and available options.
    """
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        
        system_prompt = """
        You are a travel expert creating a detailed itinerary in markdown format. Create a comprehensive day-by-day itinerary that includes all necessary details while maintaining a clear, organized structure.

        **Important Instructions**:
        - Use only ASCII characters (Latin encoding) in the response.
        - Do not use emojis or non-ASCII characters (e.g., no 🚗, 🏨, etc.).
        - Use ASCII-friendly placeholders for section headers (e.g., [Transport], [Accommodation], [Activities], [Meals], [Daily Total]).
        - Ensure all text is compatible with Latin-1 encoding to avoid encoding issues.

        Use the following markdown structure:
        # Trip Itinerary: [Departure] to [Destination]

        ## Trip Summary
        - **Total Budget**: $[amount]
        - **Dates**: [start] to [end]
        - **Duration**: [X] days

        ## Day 1 - [Date]
        ### [Transport]
        - **Type**: [Mode]
        - **From**: [Location]
        - **To**: [Location]
        - **Cost**: $[amount]

        ### [Accommodation]
        - **Hotel**: [Name]
        - **Cost**: $[amount]
        - **Details**: [Description]

        ### [Activities]
        #### Morning
        - **Activity**: [Name]
        - **Location**: [Place]
        - **Cost**: $[amount]
        - **Details**: [Description]

        ### [Meals]
        - **Breakfast**: [Place] - $[amount]
        - **Lunch**: [Place] - $[amount]
        - **Dinner**: [Place] - $[amount]

        ### [Daily Total]: $[amount]

        [Repeat for each day]

        ## Budget Summary
        - **Total Spent**: $[amount]
        - **Remaining**: $[amount]

        Rules:
        1. Keep the budget within limits.
        2. Always ensure the number of days is correct. Double-check the duration.
        3. Use only ASCII characters (no emojis or special characters).
        4. Provide detailed descriptions for activities.
        5. Include realistic travel times and logistics.
        """
        
        user_prompt = f"""
        Create a detailed itinerary with the following information:

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
        
        TRANSPORTATION OPTIONS:
        {json.dumps(transportation_options, indent=2, ensure_ascii=True)}
        
        ACCOMMODATION OPTIONS:
        {json.dumps(accommodation_options, indent=2, ensure_ascii=True)}
        
        FOOD RECOMMENDATIONS:
        {json.dumps(food_recommendations, indent=2, ensure_ascii=True)}
        
        ATTRACTIONS:
        {json.dumps(attractions, indent=2, ensure_ascii=True)}

        Please provide the itinerary in the specified markdown format. Make sure to:
        1. Use only ASCII characters (no emojis or non-ASCII characters).
        2. Use bold text for important information.
        3. Keep costs within budget constraints.
        4. Provide detailed descriptions for activities.
        5. Include realistic travel times and logistics.
        6. Ensure the number of days is correct; double-check before returning the response.
        """

        logger.debug("Sending request to Groq API")
        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        itinerary = response.choices[0].message.content
        logger.debug(f"Received itinerary: {itinerary[:200]}...")
        
        try:
            itinerary.encode('ascii')
        except UnicodeEncodeError as e:
            logger.error(f"Itinerary contains non-ASCII characters: {str(e)}")
            itinerary = itinerary.encode('ascii', errors='ignore').decode('ascii')
        
        logger.info("Itinerary generated successfully")
        print(itinerary)
        return itinerary

    except Exception as e:
        logger.error(f"Error generating itinerary: {str(e)}", exc_info=True)
        error_msg = f"Error generating itinerary: {str(e)}"
        print(error_msg)
        return error_msg