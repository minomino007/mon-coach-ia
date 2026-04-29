import streamlit as st
import pandas as pd
from datetime import date
import openai
from streamlit_mic_recorder import mic_recorder
import json

# ==========================================
# CONFIGURATION SIMPLE
# ==========================================
st.set_page_config(
    page_title="Gym AI Agent PRO",
    layout="centered",
    page_icon="🏋️"
)

# Ta clé API (ton moteur)
api_key_val = "sk-proj-7_R7-BvF7H_OaE5G-iNqXm8G-1N4"
client = openai.OpenAI(api_key=api_key_val)

# ==========================================
# MÉMOIRE DE L'APPLICATION
# ==========================================
if 'lang' not in st.session_state: st.session_state.lang = "Français"
if 'logs' not in st.session_state: st.session_state.logs = [] 
if 'notes_calendrier' not in st.session_state: st.session_state.notes_calendrier = {}
if 'temp_workout' not in st.session_state: st.session_state.temp_workout = []
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "nom": "Athlète", "age": 25, "grandeur": "5'10",
        "objectif": "Prise de masse", "poids": 205, "blessures": "Aucune"
    }

# Liste des exercices
chest_options = ["Développé couché", "Développé incliné", "Pec deck", "Pompes", "Dips"]

# ==========================================
# FONCTION VOCALE (L'intelligence)
# ==========================================
def extraire_donnees_seance(audio_bytes):
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_bytes)
    with open("temp_audio.wav", "rb") as audio_file:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        texte = transcript.text
    prompt = f"Extrais JSON (zone, exercice, poids, reps) de : {texte}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.choices[0].message.content), texte

# ==========================================
# INTERFACE (TES ONGLETS)
# ==========================================
st.title("🤖 Mon Gym AI Agent")

t1, t2, t3, t4, t5 = st.tabs(["📊 Profil", "🏋️ Séance", "👤 Guide", "🎥 Vision", "📅 Calendrier"])

# --- ONGLET 1 : TON PROFIL ---
with t1:
    st.header("👤 Ton Profil")
    prof = st.session_state.user_profile
    st.metric("Poids actuel", f"{prof['poids']} lbs")
    with st.expander("Modifier mes infos"):
        n = st.text_input("Nom", value=prof["nom"])
        p = st.number_input("Poids (lbs)", value=prof["poids"])
        if st.button("Enregistrer le profil"):
            st.session_state.user_profile.update({"nom": n, "poids": p})
            st.rerun()

# --- ONGLET 2 : SÉANCE (LE MICRO) ---
with t2:
    st.header("🏋️ Enregistrer une séance")
    st.write("Clique sur le micro et dis par exemple : 'Pectoraux, développé couché, 150 lbs, 10 répétitions'")
    
    audio = mic_recorder(start_prompt="🔴 Appuie pour parler", stop_prompt="🟢 Analyse ma voix", key="mic_v1")

    if audio:
        try:
            with st.spinner("L'IA travaille..."):
                data, texte = extraire_donnees_seance(audio['bytes'])
                st.session_state.temp_workout.append({
                    "Date": str(date.today()), 
                    "Zone": data.get("zone", "Pectoraux"), 
                    "Exercice": data.get("exercice", "Inconnu"), 
                    "Poids": data.get("poids", 0), 
                    "Reps": data.get("reps", 0)
                })
                st.success(f"Compris : {texte}")
        except:
            st.error("Problème de clé API. Vérifie ton compte OpenAI.")

    if st.session_state.temp_workout:
        st.table(pd.DataFrame(st.session_state.temp_workout))
        if st.button("✅ Valider l'entraînement"):
            st.session_state.logs.extend(st.session_state.temp_workout)
            st.session_state.temp_workout = []
            st.success("C'est enregistré !")

# --- ONGLET 3 : GUIDE ---
with t3:
    st.header("👤 Guide Technique")
    st.video("https://www.youtube.com/watch?v=gRVjAtPip0Y")

# --- ONGLET 4 : VISION ---
with t4:
    st.header("🎥 Vision IA")
    up = st.file_uploader("Envoie ta vidéo ici", type=["mp4", "mov"])
    if up: st.video(up)

# --- ONGLET 5 : CALENDRIER ---
with t5:
    st.header("📅 Historique")
    choix_date = st.date_input("Quelle date ?", date.today())
    df = pd.DataFrame(st.session_state.logs)
    if not df.empty:
        st.table(df[df['Date'] == str(choix_date)])
    
    note = st.text_area("Notes du jour", value=st.session_state.notes_calendrier.get(str(choix_date), ""))
    if st.button("Sauvegarder la note"):
        st.session_state.notes_calendrier[str(choix_date)] = note
        st.success("Note enregistrée !")
