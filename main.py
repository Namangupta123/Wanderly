import streamlit as st
from datetime import datetime, timedelta

from tools.flights import get_flight_options
from tools.train import get_train_options
from tools.food import get_food_recommendations
from tools.places import get_attractions
from tools.stay import get_accommodation_options
from agents.itinerary import generate_itinerary, generate_pdf_itinerary

st.set_page_config(
    page_title="Wanderly - Smart Trip Planner",
    page_icon="✈️",
    layout="wide",
)

st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    h1, h2, h3 {
        color: #1e3a8a;
    }
    .stButton>button {
        background-color: #1e3a8a;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1e40af;
    }
    .highlight {
        background-color: #e0f2fe;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

if 'itinerary' not in st.session_state:
    st.session_state.itinerary = None
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'transportation_mode' not in st.session_state:
    st.session_state.transportation_mode = "flight"

st.title("✈️ Wanderly")
st.markdown("### Your AI-Powered Trip Planner")

if st.session_state.step == 1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("Plan Your Journey")
    
    col1, col2 = st.columns(2)
    
    with col1:
        departure_city = st.text_input("Departure City", placeholder="e.g., New York, USA")
        destination = st.text_input("Destination", placeholder="e.g., Paris, France")
        
        start_date = st.date_input(
            "Start Date",
            datetime.now() + timedelta(days=30)
        )
        
        end_date = st.date_input(
            "End Date",
            datetime.now() + timedelta(days=37)
        )
        
        budget = st.number_input("Budget (USD)", min_value=100, value=1500)
        
        transportation_mode = st.radio(
            "Transportation Mode",
            ["Flight", "Train"],
            horizontal=True
        )
        st.session_state.transportation_mode = transportation_mode.lower()
    
    with col2:
        accommodation_preference = st.selectbox(
            "Accommodation Preference",
            ["Budget", "Mid-range", "Luxury"]
        )
        
        food_preference = st.selectbox(
            "Food Preference",
            ["Local cuisine", "International", "Fine dining", "Street food"]
        )
        
        activity_preference = st.multiselect(
            "Activity Preferences",
            ["Historical sites", "Museums", "Nature", "Adventure", "Shopping", "Relaxation", "Nightlife"],
            default=["Historical sites", "Museums"]
        )
        
        special_requirements = st.text_area("Special Requirements or Interests", placeholder="e.g., Vegetarian food, accessibility needs, etc.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Generate Itinerary"):
        if not departure_city:
            st.error("Please enter your departure city")
        elif not destination:
            st.error("Please enter a destination")
        elif start_date >= end_date:
            st.error("End date must be after start date")
        else:
            with st.spinner("Generating your personalized itinerary... This may take a minute."):
                try:
                    delta = end_date - start_date
                    num_days = delta.days + 1
                    
                    user_preferences = {
                        "departure_city": departure_city,
                        "destination": destination,
                        "start_date": start_date.strftime("%Y-%m-%d"),
                        "end_date": end_date.strftime("%Y-%m-%d"),
                        "num_days": num_days,
                        "budget": budget,
                        "accommodation": accommodation_preference,
                        "food": food_preference,
                        "activities": activity_preference,
                        "special_requirements": special_requirements if special_requirements else "None",
                        "transportation_mode": st.session_state.transportation_mode
                    }
                    
                    if st.session_state.transportation_mode == "flight":
                        transportation_options = get_flight_options(departure_city, destination, start_date, budget)
                    else:
                        transportation_options = get_train_options(departure_city, destination, start_date, budget)
                    
                    accommodation_options = get_accommodation_options(
                        destination, 
                        start_date, 
                        end_date, 
                        accommodation_preference, 
                        budget
                    )
                    
                    food_recommendations = get_food_recommendations(
                        destination, 
                        food_preference, 
                        special_requirements
                    )
                    
                    attractions = get_attractions(
                        destination, 
                        activity_preference, 
                        special_requirements
                    )
                    
                    itinerary = generate_itinerary(
                        user_preferences,
                        transportation_options,
                        accommodation_options,
                        food_recommendations,
                        attractions
                    )
                    
                    st.session_state.itinerary = itinerary
                    st.session_state.step = 2
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

elif st.session_state.step == 2:
    itinerary = st.session_state.itinerary
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header(f"Your Itinerary: {itinerary['user_preferences']['departure_city']} to {itinerary['destination']}")
    st.subheader(f"{itinerary['dates']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Budget", f"${itinerary['total_budget']}")
    with col2:
        st.metric("Estimated Cost", f"${itinerary['total_cost']}")
    with col3:
        st.metric("Remaining Budget", f"${itinerary['remaining_budget']}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    for day in itinerary['days']:
        st.markdown(f'<div class="card">', unsafe_allow_html=True)
        st.subheader(f"Day {day['day']} - {day['date']}")
        
        if day['day'] == 1 or day['day'] == len(itinerary['days']):
            st.markdown("#### ✈️ Transportation")
            for transport in day['transportation']:
                st.markdown(f"**{transport['type']}**: {transport['from']} to {transport['to']} - ${transport['cost']}")
        
        st.markdown("#### 🏨 Accommodation")
        st.markdown(f"**{day['accommodation']['name']}** - ${day['accommodation']['cost']}")
        st.markdown(f"{day['accommodation']['description']}")
        
        st.markdown("#### 🎯 Activities")
        for activity in day['activities']:
            st.markdown(f"**{activity['time']}**: {activity['activity']} - ${activity['cost']}")
            st.markdown(f"*{activity['description']}* at {activity['location']}")
        
        st.markdown("#### 🍽️ Meals")
        for meal in day['meals']:
            st.markdown(f"**{meal['type']}**: {meal['recommendation']} ({meal['cuisine']}) - ${meal['cost']}")
        
        if day['day'] != 1 and day['day'] != len(itinerary['days']):
            st.markdown("#### 🚗 Local Transportation")
            for transport in day['transportation']:
                st.markdown(f"**{transport['type']}**: {transport['from']} to {transport['to']} - ${transport['cost']}")
        
        st.markdown(f"**Daily Total: ${day['daily_total']}**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Edit Preferences"):
            st.session_state.step = 1
            st.rerun()
    
    with col2:
        if st.button("Download PDF Itinerary"):
            pdf_content = generate_pdf_itinerary(itinerary)
            st.download_button(
                label="Download PDF",
                data=pdf_content,
                file_name=f"Wanderly_Itinerary_{itinerary['destination'].replace(' ', '_')}.pdf",
                mime="application/pdf"
            )