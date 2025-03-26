from datetime import datetime
from langchain.chains import LLMChain
from langchain_mistralai import ChatMistralAI
from langchain.schema.runnable import RunnableSequence
from langchain.prompts import PromptTemplate
from config import MISTRAL_TRANSPORT_KEY

def get_train_options(departure_city, destination, departure_date, budget):
    """
    Get train options for the specified route and date within budget using MistralAI.
    
    Args:
        departure_city (str): The departure city
        destination (str): The destination city/country
        departure_date (datetime): The departure date
        budget (float): The maximum budget for train tickets
        
    Returns:
        list: A list of train options with details
    """
    try:
        llm = ChatMistralAI(
            model="mistral-large-2411",
            api_key=MISTRAL_TRANSPORT_KEY
        )
        
        template = """
        You are a travel expert providing realistic train options for a journey.
        
        Details:
        - Departure: {departure_city}
        - Destination: {destination}
        - Date: {departure_date}
        - Maximum Budget: ${budget} USD

        Provide 5 realistic train options with the following details for each:
        - Train company/operator
        - Departure time
        - Arrival time
        - Journey duration
        - Price (within budget)
        - Class (Economy/Business/First)
        - Number of transfers

        Format the response as a JSON array of train objects. Each object should have:
        - company: string
        - departure_time: string (HH:MM format)
        - arrival_time: string (HH:MM format)
        - duration: string (e.g., "3h 15m")
        - price: string (e.g., "$120")
        - class: string
        - transfers: number

        Only return the JSON array, nothing else.
        Ensure all prices are within the specified budget.
        Use realistic train operators that service these locations.
        Consider the actual train journey duration between these cities.
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
        train_options = json.loads(response)
        
        return train_options
        
    except Exception as e:
        print(f"Error fetching train options: {str(e)}")
        return [
            {
                "company": "Sample Train Company",
                "departure_time": "09:00",
                "arrival_time": "13:00",
                "duration": "4h 00m",
                "price": f"${round(budget * 0.25)}",
                "class": "Economy",
                "transfers": 0
            }
        ]