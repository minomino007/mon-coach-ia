import streamlit as st
import pandas as pd
from datetime import date
import openai
from streamlit_mic_recorder import mic_recorder
import json

# ==========================================
# CONFIGURATION DE LA PAGE
# ==========================================
st.set_page_config(
    page_title="Gym AI Agent PRO",
    layout="centered",
    page_icon="🏋️"
)

# Ta clé API est ici (ne pas modifier)
api_key_val = "sk-proj-7_R7-BvF7H_OaE5G-iNqXm8G-1N4"
client = openai.OpenAI(api_key=api_key_val)

# ==========================================
# MÉMOIRE DE L'APPLICATION
# ==========================================
if 'logs' not in st.session_state: st.session_state.logs = [] 
if 'notes_calendrier' not in st.session_state: st.session_state.notes_calendrier = {}
if 'temp_workout' not in st.session_state: st.session_state.temp_workout = []
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "nom": "Athlète", "age": 25, "grandeur": "5'10",
        "objectif": "Prise de masse", "poids": 205, "blessures": "Aucune"
    }

# ==========================================
# FONCTION VOCALE (INTÉLLIGENCE)
# ==========================================
def extraire_donnees_seance(audio_bytes):
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_bytes)
    with open("temp_audio.wav", "rb") as audio_file:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        texte = transcript.text
    prompt = f"Extrais JSON (zone, exercice, poids, reps) de : {texte}. Zones: Pectoraux, Dos, Jambes, Épaules, Abdos."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.choices[0].message.content), texte

# ==========================================
# CRÉATION DES 5 ONGLETS
# ==========================================
st.title("🤖 Mon Gym AI Agent")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Profil", "🏋️ Séance du jour", "👤 Guide", "🎥 Vision", "📅 Calendrier"])

# --- ONGLET 1 : PROFIL ---
with tab1:
    st.header("👤 Ton Profil Sportif")
    prof = st.session_state.user_profile
    st.metric("Poids actuel", f"{prof['poids']} lbs")
    st.write(f"**Nom :** {prof['nom']} | **Objectif :** {prof['objectif']}")
    
    with st.expander("Modifier mes informations"):
        with st.form("form_profil"):
            n = st.text_input("Nom", value=prof["nom"])
            p = st.number_input("Poids (lbs)", value=prof["poids"])
            obj = st.selectbox("Objectif", ["Prise de masse", "Perte de gras", "Force"])
            if st.form_submit_button("Sauvegarder le profil"):
                st.session_state.user_profile.update({"nom": n, "poids": p, "objectif": obj})
                st.rerun()

# --- ONGLET 2 : SÉANCE (MICRO) ---
with tab2:
    st.header("🏋️ Enregistrer une séance")
    st.write("Clique sur le micro et parle (ex: 'Pectoraux, développé couché, 150 lbs, 10 reps')")
    
    audio = mic_recorder(start_prompt="🔴 Parler", stop_prompt="🟢 Analyser", key="mic_v2")

    if audio:
        try:
            with st.spinner("L'IA analyse ta voix..."):
                data, texte = extraire_donnees_seance(audio['bytes'])
                st.session_state.temp_workout.append({
                    "Date": str(date.today()), 
                    "Zone": data.get("zone", "Pectoraux"), 
                    "Exercice": data.get("exercice", "Inconnu"), 
                    "Poids": data.get("poids", 0), 
                    "Reps": data.get("reps", 0)
                })
                st.success(f"Entendu : {texte}")
        except:
            st.error("Erreur avec la clé API OpenAI.")

    if st.session_state.temp_workout:
        st.table(pd.DataFrame(st.session_state.temp_workout))
        if st.button("✅ Enregistrer définitivement"):
            st.session_state.logs.extend(st.session_state.temp_workout)
            st.session_state.temp_workout = []
            st.success("Séance enregistrée dans l'historique !")

# --- ONGLET 3 : GUIDE ---
with tab3:
    st.header("👤 Guide Technique")
    st.video("https://www.youtube.com/watch?v=gRVjAtPip0Y")

# --- ONGLET 4 : VISION ---
with tab4:
    st.header("🎥 Vision IA")
    up = st.file_uploader("Télécharge ta vidéo", type=["mp4", "mov"])
    if up: st.video(up)

# --- ONGLET 5 : CALENDRIER ---
with tab5:
    st.header("📅 Historique & Calendrier")
    d_choisie = st.date_input("Choisir une date", date.today())
    df = pd.DataFrame(st.session_state.logs)
    if not df.empty:
        filtre = df[df['Date'] == str(d_choisie)]
        if not filtre.empty:
            st.table(filtre)
        else:
            st.info("Rien d'enregistré pour ce jour-là.")
    
    note = st.text_area("Notes pour ce jour", value=st.session_state.notes_calendrier.get(str(d_choisie), ""))
    if st.button("Sauvegarder la note"):
        st.session_state.notes_calendrier[str(d_choisie)] = note
        st.success("Note enregistrée !")
