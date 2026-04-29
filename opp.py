import streamlit as st
import pandas as pd
from datetime import date
import openai
import json
import calendar

# ==========================================
# 1. CONFIGURATION DE LA PAGE & CLÉ API
# ==========================================
st.set_page_config(
    page_title="Gym AI Agent PRO",
    layout="centered",
    page_icon="🏋️",
    initial_sidebar_state="collapsed"
)

api_key_val = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI(api_key=api_key_val, base_url="https://openrouter.ai/api/v1" )

# ==========================================
# 2. SYSTÈME DE TRADUCTION
# ==========================================
# ... (le reste du code est identique à votre base)

# Dictionnaire des animations (GIFs) par exercice
exercise_animations = {
    "Développé couché": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJmZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKv6eJJpL8F6v7y/giphy.gif",
    "Pompes": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJmZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKv6eJJpL8F6v7y/giphy.gif",
    "Tractions": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJmZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKv6eJJpL8F6v7y/giphy.gif",
    "Soulevé de terre": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJmZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKv6eJJpL8F6v7y/giphy.gif",
    "Squat barre": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJmZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKv6eJJpL8F6v7y/giphy.gif",
    "Développé militaire": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJmZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKv6eJJpL8F6v7y/giphy.gif",
    "Curl barre EZ": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJmZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKv6eJJpL8F6v7y/giphy.gif",
    "Planche (gainage )": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJmZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6ZzZ6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKv6eJJpL8F6v7y/giphy.gif"
}

# ... (le reste du code suit la même logique )
