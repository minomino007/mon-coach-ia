import streamlit as st
import pandas as pd
from datetime import date
import openai
from streamlit_mic_recorder import mic_recorder
import json

# 1. CONFIGURATION & SECRETS
st.set_page_config(page_title="Gym AI Agent PRO", layout="centered", page_icon="🏋️")

if "OPENAI_API_KEY" in st.secrets:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 2. DICTIONNAIRE
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
        "lang_label": "Langue",
        "weight": "Poids (lbs)",
        "reps": "Répétitions",
        "date_label": "Date",
        "zone_label": "Zone musculaire",
        "ex_label": "Exercice",
        "name_field": "Nom",
        "obj_field": "Objectif",
        "inj_field": "Blessures / Notes",
        "age_field": "Âge",
        "height_field": "Grandeur",
        "goals": ["Prise de masse", "Perte de gras", "Force", "Endurance"]
    }
}

# 3. INITIALISATION
if 'lang' not in st.session_state: st.session_state.lang = "Français"
if 'logs' not in st.session_state: st.session_state.logs = [] 
if 'temp_workout' not in st.session_state: st.session_state.temp_workout = []
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {"nom": "Athlète", "age": 25, "grandeur": "5'10", "objectif": "Prise de masse", "poids": 205, "blessures": "Aucune"}

chest_options = ["Développé couché", "Développé incliné", "Pec deck", "Pompes", "Dips"]
L = languages[st.session_state.lang]

# --- FONCTION D'EXTRACTION IA ---
def extraire_donnees_seance(audio_bytes):
    # 1. Transcription
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_bytes)
    
    with open("temp_audio.wav", "rb") as audio_file:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        texte = transcript.text

    # 2. Analyse par GPT pour formater en JSON
    prompt = f"""Extraire les infos de musculation du texte suivant : "{texte}". 
    Répondre UNIQUEMENT en JSON avec ces clés : zone, exercice, poids (nombre), reps (nombre).
    Zones possibles : Pectoraux, Dos, Jambes, Épaules, Abdos."""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.choices[0].message.content), texte

# --- INTERFACE ---
st.title("🤖 Mon Gym AI Agent")
tab1, tab2, tab3, tab4, tab5 = st.tabs(L["tabs"])

# --- ONGLET 1 : PROFIL ---
with tab1:
    st.header(L["prof_header"])
    prof = st.session_state.user_profile
    st.write(f"**Nom :** {prof['nom']} | **Objectif :** {prof['objectif']}")
    with st.expander(L["edit_prof"]):
        with st.form("edit_profile"):
            n = st.text_input(L["name_field"], value=prof["nom"])
            p = st.number_input(L["weight"], value=prof["poids"])
            if st.form_submit_button(L["save"]):
                st.session_state.user_profile.update({"nom": n, "poids": p})
                st.rerun()

# --- ONGLET 2 : SÉANCE DU JOUR ---
with tab2:
    st.header(L["workout_header"])
    
    # MICRO INTELLIGENT
    st.write("🎙️ **Dit par exemple :** 'Pectoraux, développé couché, 150 livres, 12 répétitions'")
    audio_record = mic_recorder(start_prompt="🔴 Parler", stop_prompt="🟢 Analyser", key="gym_mic_pro")

    if audio_record:
        try:
            with st.spinner("L'IA analyse ta voix..."):
                data, texte_brut = extraire_donnees_seance(audio_record['bytes'])
                
                # Ajout automatique à la liste temporaire
                st.session_state.temp_workout.append({
                    "Date": str(date.today()), 
                    "Zone": data.get("zone", "Inconnue"), 
                    "Exercice": data.get("exercice", "Inconnu"), 
                    "Poids": data.get("poids", 0), 
                    "Reps": data.get("reps", 0)
                })
                st.success(f"Compris : {texte_brut}")
        except Exception as e:
            st.error(f"Erreur d'analyse : {e}")

    st.divider()
    
    # Formulaire manuel (toujours dispo)
    with st.form("manual_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        z = col1.selectbox(L["zone_label"], ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos"])
        ex = col2.text_input(L["ex_label"])
        w = col1.number_input(L["weight"], value=135)
        r = col2.number_input(L["reps"], value=8)
        if st.form_submit_button(L["add_set"]):
            st.session_state.temp_workout.append({"Date": str(date.today()), "Zone": z, "Exercice": ex, "Poids": w, "Reps": r})

    # Affichage de la liste
    if st.session_state.temp_workout:
        st.dataframe(pd.DataFrame(st.session_state.temp_workout), use_container_width=True)
        if st.button(L["validate"], type="primary"):
            st.session_state.logs.extend(st.session_state.temp_workout)
            st.session_state.temp_workout = []
            st.success("Séance enregistrée !")
            st.balloons()
