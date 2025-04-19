import streamlit as st
from datetime import datetime, timedelta
import geocoder

st.set_page_config(
    page_title="Wanderly - Smart Trip Planner",
    page_icon="✈️",
    layout="wide"
)

from tools.flights import get_flight_options
from tools.train import get_train_options
from tools.food import get_food_recommendations
from tools.places import get_attractions
from tools.stay import get_accommodation_options
from agents.itinerary import generate_itinerary

st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
        padding: 20px;
        border-radius: 10px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .header {
        color: #2c3e50;
        font-size: 36px;
        text-align: center;
        margin-bottom: 20px;
    }
    .subheader {
        color: #34495e;
        font-size: 24px;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

def init_session_state():
    defaults = {
        'itinerary_markdown': None,
        'step': 1,
        'transportation_mode': 'flight'
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

with st.container():
    st.markdown('<h1 class="header">Wanderly - Smart Trip Planner</h1>', unsafe_allow_html=True)

    if st.session_state.step == 1:
        st.markdown('<h2 class="subheader">Plan Your Journey</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            departure_city = st.text_input("Departure City", placeholder="e.g., New York, USA", 
                                        help="Enter your starting city")
            destination = st.text_input("Destination", placeholder="e.g., Paris, France",
                                      help="Enter your destination city")
            
            today = datetime.now()
            start_date = st.date_input(
                "Start Date",
                min_value=today,
                value=today + timedelta(days=30),
                help="Select your trip start date"
            )
            
            end_date = st.date_input(
                "End Date",
                min_value=start_date + timedelta(days=1),
                value=start_date + timedelta(days=7),
                help="Select your trip end date"
            )
            
            total_budget = st.number_input(
                "Total Budget (USD)", 
                min_value=100.0, 
                value=1500.0, 
                step=50.0,
                help="Set your total trip budget"
            )
            
            st.markdown('<p class="subheader">Budget Breakdown</p>', unsafe_allow_html=True)
            with st.container():
                transport_percent = st.slider("Transportation (%)", 5.0, 50.0, 15.0, step=1.0,
                                            help="Percentage of budget for transportation")
                accommodation_percent = st.slider("Accommodation (%)", 20.0, 60.0, 40.0, step=1.0,
                                               help="Percentage of budget for accommodation")
                food_percent = st.slider("Food & Dining (%)", 10.0, 40.0, 25.0, step=1.0,
                                       help="Percentage of budget for food")
                
                total_percent = transport_percent + accommodation_percent + food_percent
                if total_percent > 100:
                    st.error("Budget percentages exceed 100%")
                    activities_percent = 0.0
                else:
                    activities_percent = 100.0 - total_percent
                
                transport_budget = total_budget * (transport_percent / 100)
                accommodation_budget = total_budget * (accommodation_percent / 100)
                food_budget = total_budget * (food_percent / 100)
                activities_budget = total_budget * (activities_percent / 100)
                
                # Simplified budget display without custom styling
                st.write(f"Transportation: ${transport_budget:.2f}")
                st.write(f"Accommodation: ${accommodation_budget:.2f}")
                st.write(f"Food & Dining: ${food_budget:.2f}")
                st.write(f"Activities: ${activities_budget:.2f}")
            
            transportation_mode = st.radio(
                "Transportation Mode",
                ["Flight", "Train"],
                horizontal=True,
                help="Choose your preferred transportation"
            )
            st.session_state.transportation_mode = transportation_mode.lower()
        
        with col2:
            accommodation_preference = st.selectbox(
                "Accommodation Preference",
                ["Budget", "Mid-range", "Luxury"],
                help="Select your accommodation style"
            )
            
            food_preference = st.selectbox(
                "Food Preference",
                ["Local cuisine", "International", "Fine dining", "Street food"],
                help="Select your dining preference"
            )
            
            activity_preference = st.multiselect(
                "Activity Preferences",
                ["Historical sites", "Museums", "Nature", "Adventure", "Shopping", "Relaxation", "Nightlife"],
                default=["Historical sites", "Museums"],
                help="Choose your preferred activities"
            )
            
            special_requirements = st.text_area(
                "Special Requirements",
                placeholder="e.g., Vegetarian food, accessibility needs, etc.",
                help="Add any special requirements"
            )
        
        if st.button("Generate Itinerary", key="generate"):
            if not departure_city or not destination:
                st.error("Please enter both departure city and destination")
            elif start_date >= end_date:
                st.error("End date must be after start date")
            elif total_percent > 100:
                st.error("Please adjust budget percentages to sum to 100% or less")
            else:
                with st.spinner("Generating your personalized itinerary..."):
                    try:
                        delta = end_date - start_date
                        num_days = delta.days + 1
                        
                        user_preferences = {
                            "departure_city": departure_city.strip(),
                            "destination": destination.strip(),
                            "start_date": start_date.strftime("%Y-%m-%d"),
                            "end_date": end_date.strftime("%Y-%m-%d"),
                            "num_days": num_days,
                            "budget": float(total_budget),
                            "transport_budget": float(transport_budget),
                            "accommodation_budget": float(accommodation_budget),
                            "food_budget": float(food_budget),
                            "activities_budget": float(activities_budget),
                            "accommodation": accommodation_preference,
                            "food": food_preference,
                            "activities": activity_preference,
                            "special_requirements": special_requirements.strip(),
                            "transportation_mode": st.session_state.transportation_mode
                        }
                        
                        transportation_options = (
                            get_flight_options if st.session_state.transportation_mode == "flight"
                            else get_train_options
                        )(departure_city, destination, start_date, transport_budget)
                        
                        accommodation_options = get_accommodation_options(
                            destination, start_date, end_date, accommodation_preference, accommodation_budget
                        )
                        
                        food_recommendations = get_food_recommendations(
                            destination, food_preference, special_requirements
                        )
                        
                        attractions = get_attractions(
                            destination, activity_preference, special_requirements
                        )
                        
                        markdown_content = generate_itinerary(
                            user_preferences, transportation_options, accommodation_options,
                            food_recommendations, attractions
                        )
                        
                        st.session_state.itinerary_markdown = markdown_content
                        st.session_state.step = 2
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

    elif st.session_state.step == 2:
        markdown_content = st.session_state.itinerary_markdown
        if not markdown_content:
            st.error("No itinerary found. Please start over.")
            st.session_state.step = 1
            st.rerun()
        
        st.warning(
            f"⚠️ The following itinerary is generated by an AI. Please double-check all details, including travel, stay, and activities, as the information may not be 100% accurate or up-to-date."
        )
        
        st.markdown(markdown_content)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Start Over", key="start_over"):
                st.session_state.step = 1
                st.session_state.itinerary_markdown = None
                st.rerun()
        
        with col2:
            if st.button("Download Itinerary", key="download"):
                try:
                    with st.spinner("Generating Text file..."):
                        st.download_button(
                            label="Download PDF Now",
                            data=markdown_content,
                            file_name=f"Wanderly_Itinerary_{datetime.now().strftime('%Y%m%d')}.txt",
                            mime="text/plain",
                            key="download_button"
                        )
                except Exception as e:
                    st.error(f"Failed to generate PDF: {str(e)}")