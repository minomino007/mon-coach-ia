import streamlit as st
import pandas as pd
from datetime import date
import openai
from streamlit_mic_recorder import mic_recorder
import json

# ==========================================
# 1. CONFIGURATION DE LA PAGE & CLÉ API
# ==========================================
st.set_page_config(
    page_title="Gym AI Agent PRO",
    layout="centered",
    page_icon="🏋️"
)

# Utilisation de la clé que tu as fournie
api_key_val = "sk-proj-7_R7-BvF7H_OaE5G-iNqXm8G-1N4"
client = openai.OpenAI(api_key=api_key_val)

# ==========================================
# 2. SYSTÈME DE TRADUCTION
# ==========================================
languages = {
    "Français": {
        "tabs": ["📊 Profil", "🏋️ Séance du jour", "👤 Guide", "🎥 Vision", "📅 Calendrier"],
        "prof_header": "👤 Ton Profil Sportif",
        "edit_prof": "Modifier le profil",
        "save": "Sauvegarder",
        "workout_header": "🏋️ Enregistrer une séance",
        "add_set": "➕ Ajouter la série",
        "validate": "✅ Enregistrer l'entraînement complet",
        "clear": "❌ Tout effacer",
        "lang_label": "Choisir la langue",
        "weight": "Poids (lbs)",
        "reps": "Répétitions",
        "date_label": "Date",
        "zone_label": "Zone musculaire",
        "ex_label": "Exercice spécifique",
        "name_field": "Nom",
        "obj_field": "Objectif",
        "inj_field": "Blessures / Notes",
        "age_field": "Âge",
        "height_field": "Grandeur",
        "goals": ["Prise de masse", "Perte de gras", "Force", "Endurance"]
    }
}

# ==========================================
# 3. INITIALISATION MÉMOIRE
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

chest_options = ["Développé couché", "Développé incliné", "Pec deck", "Pompes", "Dips"]

# ==========================================
# 4. FONCTION INTELLIGENTE (VOCAL -> DONNÉES)
# ==========================================
def extraire_donnees_seance(audio_bytes):
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_bytes)
    
    with open("temp_audio.wav", "rb") as audio_file:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        texte = transcript.text

    prompt = f"""Extraire les infos du texte : "{texte}". 
    Répondre en JSON : {{"zone": "string", "exercice": "string", "poids": nombre, "reps": nombre}}
    Zones : Pectoraux, Dos, Jambes, Épaules, Abdos."""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.choices[0].message.content), texte

L = languages[st.session_state.lang]

# ==========================================
# 5. INTERFACE (ONGLETS)
# ==========================================
st.title("🤖 Mon Gym AI Agent")
tab1, tab2, tab3, tab4, tab5 = st.tabs(L["tabs"])

# --- ONGLET 1 : PROFIL ---
with tab1:
    st.header(L["prof_header"])
    prof = st.session_state.user_profile
    st.metric(L["weight"], f"{prof['poids']} lbs")
    with st.expander(L["edit_prof"]):
        with st.form("edit_profil"):
            n = st.text_input(L["name_field"], value=prof["nom"])
            p = st.number_input(L["weight"], value=prof["poids"])
            if st.form_submit_button(L["save"]):
                st.session_state.user_profile.update({"nom": n, "poids": p})
                st.rerun()

# --- ONGLET 2 : SÉANCE (VOCAL INTELLIGENT) ---
with tab2:
    st.header(L["workout_header"])
    st.write("🎙️ **Dit ta séance** (ex: 'Pectoraux, développé couché, 150 lbs, 10 reps')")
    
    audio_record = mic_recorder(start_prompt="🔴 Parler", stop_prompt="🟢 Analyser", key="mic_final")

    if audio_record:
        try:
            with st.spinner("Analyse en cours..."):
                data, raw_text = extraire_donnees_seance(audio_record['bytes'])
                st.session_state.temp_workout.append({
                    "Date": str(date.today()), 
                    "Zone": data.get("zone", "Pectoraux"), 
                    "Exercice": data.get("exercice", "Inconnu"), 
                    "Poids": data.get("poids", 0), 
                    "Reps": data.get("reps", 0)
                })
                st.success(f"Entendu : {raw_text}")
        except Exception as e:
            st.error(f"Erreur : {e}")

    st.divider()
    with st.form("manual_entry", clear_on_submit=True):
        z = st.selectbox(L["zone_label"], ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos"])
        ex = st.text_input(L["ex_label"])
        w = st.number_input(L["weight"], value=135)
        r = st.number_input(L["reps"], value=8)
        if st.form_submit_button(L["add_set"]):
            st.session_state.temp_workout.append({"Date": str(date.today()), "Zone": z, "Exercice": ex, "Poids": w, "Reps": r})

    if st.session_state.temp_workout:
        st.dataframe(pd.DataFrame(st.session_state.temp_workout), use_container_width=True)
        if st.button(L["validate"], type="primary"):
            st.session_state.logs.extend(st.session_state.temp_workout)
            st.session_state.temp_workout = []
            st.success("Enregistré !")

# --- ONGLET 3 : GUIDE ---
with tab3:
    st.header("👤 Guide")
    st.video("https://www.youtube.com/watch?v=gRVjAtPip0Y")

# --- ONGLET 4 : VISION ---
with tab4:
    st.header("🎥 Vision IA")
    st.file_uploader("Upload vidéo", type=["mp4", "mov"])

# --- ONGLET 5 : CALENDRIER ---
with tab5:
    st.header("📅 Historique")
    d_cal = st.date_input("Date", date.today())
    df_logs = pd.DataFrame(st.session_state.logs)
    if not df_logs.empty:
        st.table(df_logs[df_logs['Date'] == str(d_cal)])
