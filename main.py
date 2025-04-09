import streamlit as st
from datetime import datetime, timedelta
import geocoder

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
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
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
    st.header("Plan Your Journey")
    
    col1, col2 = st.columns(2)
    
    with col1:
        departure_city = st.text_input("Departure City", placeholder="e.g., New York, USA")
        destination = st.text_input("Destination", placeholder="e.g., Paris, France")
        
        start_date = st.date_input(
            "Start Date",
            min_value=datetime.now(),
            value=datetime.now() + timedelta(days=30)
        )
        
        end_date = st.date_input(
            "End Date",
            min_value=start_date + timedelta(days=1),
            value=start_date + timedelta(days=7)
        )
        
        total_budget = st.number_input("Total Budget (USD)", min_value=100.0, value=1500.0, step=50.0)
        st.markdown("### Budget Breakdown")
        if 'budget_percentages' not in st.session_state:
            st.session_state.budget_percentages = {
                "transport": 15.0,
                "accommodation": 40.0,
                "food": 25.0,
                "activities": 20.0
            }
        
        transport_percent = st.slider("🚗 Transportation (%)", 5.0, 50.0, 
                                    st.session_state.budget_percentages["transport"], 
                                    step=1.0, key="transport_slider")
        
        accommodation_percent = st.slider("🏨 Accommodation (%)", 20.0, 60.0, 
                                        st.session_state.budget_percentages["accommodation"], 
                                        step=1.0, key="accommodation_slider")
        
        food_percent = st.slider("🍽️ Food & Dining (%)", 10.0, 40.0, 
                               st.session_state.budget_percentages["food"], 
                               step=1.0, key="food_slider")
        
        remaining_percent = 100.0 - (transport_percent + accommodation_percent + food_percent)
        if remaining_percent < 5.0:
            excess = 5.0 - remaining_percent
            transport_percent -= excess / 3
            accommodation_percent -= excess / 3
            food_percent -= excess / 3
            remaining_percent = 5.0
        
        activities_percent = remaining_percent
        st.session_state.budget_percentages = {
            "transport": transport_percent,
            "accommodation": accommodation_percent,
            "food": food_percent,
            "activities": activities_percent
        }
        
        transport_budget = total_budget * (transport_percent / 100)
        accommodation_budget = total_budget * (accommodation_percent / 100)
        food_budget = total_budget * (food_percent / 100)
        activities_budget = total_budget * (activities_percent / 100)
        
        st.markdown(f"🚗 Transportation: ${transport_budget:.2f} ({transport_percent:.1f}%)")
        st.markdown(f"🏨 Accommodation: ${accommodation_budget:.2f} ({accommodation_percent:.1f}%)")
        st.markdown(f"🍽️ Food & Dining: ${food_budget:.2f} ({food_percent:.1f}%)")
        st.markdown(f"🎯 Activities & Others: ${activities_budget:.2f} ({activities_percent:.1f}%)")
        
        if abs(transport_percent + accommodation_percent + food_percent + activities_percent - 100.0) > 0.1:
            st.warning("Budget percentages must add up to 100%. Activities adjusted automatically.")
        
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
        
        special_requirements = st.text_area("Special Requirements or Interests", 
                                          placeholder="e.g., Vegetarian food, accessibility needs, etc.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Generate Itinerary"):
        if not departure_city.strip():
            st.error("Please enter your departure city")
        elif not destination.strip():
            st.error("Please enter a destination")
        elif start_date >= end_date:
            st.error("End date must be after start date")
        elif total_budget < 100:
            st.error("Budget must be at least $100")
        else:
            with st.spinner("Generating your personalized itinerary... This may take a minute."):
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
                        "special_requirements": special_requirements.strip() if special_requirements.strip() else "None",
                        "transportation_mode": st.session_state.transportation_mode
                    }
                    
                    if st.session_state.transportation_mode == "flight":
                        transportation_options = get_flight_options(departure_city, destination, start_date, transport_budget)
                    else:
                        transportation_options = get_train_options(departure_city, destination, start_date, transport_budget)
                    
                    accommodation_options = get_accommodation_options(
                        destination, 
                        start_date, 
                        end_date, 
                        accommodation_preference, 
                        accommodation_budget
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
                    st.error(f"An error occurred: {str(e)}. Please try again or adjust your preferences.")

elif st.session_state.step == 2:
    itinerary = st.session_state.itinerary
    if not itinerary:
        st.error("No itinerary found. Please start over.")
        st.session_state.step = 1
        st.rerun()
        st.stop()
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header(f"Your Itinerary: {itinerary['user_preferences']['departure_city']} to {itinerary['destination']}")
    st.subheader(f"{itinerary['dates']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Budget", f"${itinerary['total_budget']:.2f}")
    with col2:
        st.metric("Estimated Cost", f"${itinerary['total_cost']:.2f}")
    with col3:
        st.metric("Remaining Budget", f"${itinerary['remaining_budget']:.2f}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    for day in itinerary['days']:
        st.markdown(f'<div class="card">', unsafe_allow_html=True)
        st.subheader(f"Day {day['day']} - {day['date']}")
        
        if day['day'] == 1 or day['day'] == len(itinerary['days']):
            st.markdown("#### ✈️ Transportation")
            for transport in day.get('transportation', []):
                st.markdown(f"**{transport['type']}**: {transport['from']} to {transport['to']} - ${transport['cost']:.2f}")
        
        st.markdown("#### 🏨 Accommodation")
        accommodation = day.get('accommodation', {})
        st.markdown(f"**{accommodation.get('name', 'N/A')}** - ${accommodation.get('cost', 0):.2f}")
        st.markdown(f"{accommodation.get('description', 'No description available')}")
        
        st.markdown("#### 🎯 Activities")
        for activity in day.get('activities', []):
            st.markdown(f"**{activity.get('time', 'N/A')}**: {activity.get('activity', 'N/A')} - ${activity.get('cost', 0):.2f}")
            st.markdown(f"*{activity.get('description', 'No description')}* at {activity.get('location', 'N/A')}")
        
        st.markdown("#### 🍽️ Meals")
        for meal in day.get('meals', []):
            st.markdown(f"**{meal.get('type', 'N/A')}**: {meal.get('recommendation', 'N/A')} ({meal.get('cuisine', 'N/A')}) - ${meal.get('cost', 0):.2f}")
        
        if day['day'] != 1 and day['day'] != len(itinerary['days']):
            st.markdown("#### 🚗 Local Transportation")
            for transport in day.get('transportation', []):
                st.markdown(f"**{transport['type']}**: {transport['from']} to {transport['to']} - ${transport['cost']:.2f}")
        
        st.markdown(f"**Daily Total: ${day.get('daily_total', 0):.2f}**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Edit Preferences"):
            st.session_state.step = 1
            st.session_state.itinerary = None
            st.rerun()
    
    with col2:
        if st.button("Download PDF Itinerary"):
            try:
                pdf_content = generate_pdf_itinerary(itinerary)
                st.download_button(
                    label="Download PDF",
                    data=pdf_content,
                    file_name=f"Wanderly_Itinerary_{itinerary['destination'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    key="download-pdf"
                )
            except Exception as e:
                st.error(f"Failed to generate PDF: {str(e)}")