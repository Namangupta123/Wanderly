from datetime import datetime
from langchain.chains import LLMChain
from langchain_mistralai import ChatMistralAI
from langchain.schema.runnable import RunnableSequence
from langchain.prompts import PromptTemplate
from config import MISTRAL_TRANSPORT_KEY

def get_flight_options(departure_city, destination, departure_date, budget):
    """
    Get flight options for the specified route and date within budget using MistralAI.
    
    Args:
        departure_city (str): The departure city
        destination (str): The destination city/country
        departure_date (datetime): The departure date
        budget (float): The maximum budget for flights
        
    Returns:
        list: A list of flight options with details
    """
    try:
        llm = ChatMistralAI(
            model="mistral-large-2411",
            api_key=MISTRAL_TRANSPORT_KEY,
            temperature=0.7
        )
        
        template = """
        You are a travel expert providing realistic flight options for a journey.
        
        Details:
        - Departure: {departure_city}
        - Destination: {destination}
        - Date: {departure_date}
        - Maximum Budget: ${budget} USD

        Provide 5 realistic flight options with the following details for each:
        - Airline name
        - Departure time
        - Arrival time
        - Flight duration
        - Price (within budget)
        - Number of stops

        Format the response as a JSON array of flight objects. Each object should have:
        - airline: string
        - departure_time: string (HH:MM format)
        - arrival_time: string (HH:MM format)
        - duration: string (e.g., "2h 30m")
        - price: string (e.g., "$450")
        - stops: string ("Nonstop" or "X stop(s)")

        Only return the JSON array, nothing else.
        Ensure all prices are within the specified budget.
        Use realistic airlines that operate in these locations.
        Consider the actual flight duration between these cities.
        """
        
        prompt = PromptTemplate(
            input_variables=["departure_city", "destination", "departure_date", "budget"],
            template=template
        )
        
        chain = prompt|llm
        formatted_date = departure_date.strftime("%Y-%m-%d")
        
        response = chain.invoke({
            "departure_city": departure_city,
            "destination": destination,
            "departure_date": formatted_date,
            "budget": budget
        })
        
        import json
        flight_options = json.loads(response)
        
        return flight_options
        
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