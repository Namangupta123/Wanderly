import json
from datetime import datetime, timedelta
from groq import Groq
import os
from fpdf import FPDF
from config import GROQ_API_KEY

def generate_itinerary(user_preferences, transportation_options, accommodation_options, food_recommendations, attractions):
    """
    Generate a detailed travel itinerary based on user preferences and available options.
    """
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        
        system_prompt = """
        You are a travel expert creating a detailed itinerary in markdown format. Create a comprehensive day-by-day itinerary that includes all necessary details while maintaining a clear, organized structure.

        Use the following markdown structure:
        # Trip Itinerary: [Departure] to [Destination]

        ## Trip Summary
        - **Total Budget**: $[amount]
        - **Dates**: [start] to [end]
        - **Duration**: [X] days

        ## Day 1 - [Date]
        ### 🚗 Transportation
        - **Type**: [Mode]
        - **From**: [Location]
        - **To**: [Location]
        - **Cost**: $[amount]

        ### 🏨 Accommodation
        - **Hotel**: [Name]
        - **Cost**: $[amount]
        - **Details**: [Description]

        ### 🎯 Activities
        #### Morning
        - **Activity**: [Name]
        - **Location**: [Place]
        - **Cost**: $[amount]
        - **Details**: [Description]

        ### 🍽️ Meals
        - **Breakfast**: [Place] - $[amount]
        - **Lunch**: [Place] - $[amount]
        - **Dinner**: [Place] - $[amount]

        ### 💰 Daily Total: $[amount]

        [Repeat for each day]

        ## Budget Summary
        - **Total Spent**: $[amount]
        - **Remaining**: $[amount]
        Rules:
        1- keep the budget in limits
        2- Always ensure the numbers of days are correct
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
        {json.dumps(transportation_options, indent=2)}
        
        ACCOMMODATION OPTIONS:
        {json.dumps(accommodation_options, indent=2)}
        
        FOOD RECOMMENDATIONS:
        {json.dumps(food_recommendations, indent=2)}
        
        ATTRACTIONS:
        {json.dumps(attractions, indent=2)}

        Please provide the itinerary in the specified markdown format. Make sure to:
        1. Include emojis for better visual organization
        2. Use bold text for important information
        3. Keep costs within budget constraints
        4. Provide detailed descriptions for activities
        5. Include realistic travel times and logistics
        """

        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        itinerary = response.choices[0].message.content
        return itinerary

    except Exception as e:
        print(f"Error generating itinerary: {str(e)}")
        return f"Error generating itinerary: {str(e)}"

def generate_pdf_itinerary(markdown_content):
    """
    Generate a PDF from markdown content using FPDF
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Set font
        pdf.set_font("Arial", size=12)
        
        # Simple markdown to PDF conversion
        lines = markdown_content.split('\n')
        for line in lines:
            # Handle headers
            if line.startswith('# '):
                pdf.set_font("Arial", 'B', 24)
                pdf.cell(0, 10, line[2:], ln=True)
                pdf.set_font("Arial", size=12)
            elif line.startswith('## '):
                pdf.set_font("Arial", 'B', 20)
                pdf.cell(0, 10, line[3:], ln=True)
                pdf.set_font("Arial", size=12)
            elif line.startswith('### '):
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, line[4:], ln=True)
                pdf.set_font("Arial", size=12)
            # Handle bullet points
            elif line.startswith('- '):
                pdf.cell(0, 10, '• ' + line[2:], ln=True)
            # Handle regular text
            elif line.strip():
                pdf.cell(0, 10, line, ln=True)
        
        return pdf.output(dest='S').encode('latin-1')
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        raise Exception(f"Failed to generate PDF: {str(e)}")