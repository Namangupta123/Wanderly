import os
import streamlit as st
'''
from dotenv import load_dotenv
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
'''

GROQ_API_KEY = st.secrets.GROQ_API_KEY
RAPIDAPI_KEY = st.secrets.RAPIDAPI_KEY