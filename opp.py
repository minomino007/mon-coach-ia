import streamlit as st
import pandas as pd
from datetime import date

# Sécurité pour éviter le crash si le module vocal n'est pas installé
try:
    from streamlit_mic_recorder import mic_recorder
    vocal_disponible = True
except ImportError:
    vocal_disponible = False

# 1. CONFIGURATION
st.set_page_config(page_title="Gym AI Agent PRO", layout="centered", page_icon="🏋️")

# 2. DICTIONNAIRE
languages = {
    "Français": {
        "tabs": ["📊 Profil", "🏋️ Séance du jour", "👤 Guide", "🎥 Vision", "📅 Calendrier"],
        "prof_header": "👤 Ton Profil Sportif",
        "save": "Sauvegarder",
        "workout_header": "🏋️ Enregistrer une séance",
        "add_set": "➕ Ajouter la série",
        "validate": "✅ Enregistrer l'entraînement complet",
        "clear": "❌ Tout effacer",
        "weight": "Poids (lbs)",
        "reps": "Répétitions",
        "date_label": "Date",
        "zone_label": "Zone musculaire",
        "ex_label": "Exercice spécifique",
        "name_field": "Nom",
    }
}

# 3. INITIALISATION
if 'lang' not in st.session_state: st.session_state.lang = "Français"
if 'logs' not in st.session_state: st.session_state.logs = [] 
if 'notes_calendrier' not in st.session_state: st.session_state.notes_calendrier = {}
if 'temp_workout' not in st.session_state: st.session_state.temp_workout = []
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {"nom": "Athlète", "poids": 205}

chest_options = ["Développé couché", "Développé incliné", "Pec Deck", "Dips", "Pompes"]

L = languages[st.session_state.lang]
st.title("🤖 Mon Gym AI Agent")

tab1, tab2, tab3, tab4, tab5 = st.tabs(L["tabs"])

# --- ONGLET 1 : PROFIL ---
with tab1:
    st.header(L["prof_header"])
    st.write(f"**Nom**: {st.session_state.user_profile['nom']} | **Poids**: {st.session_state.user_profile['poids']} lbs")

# --- ONGLET 2 : SÉANCE DU JOUR ---
with tab2:
    st.header(L["workout_header"])
    
    # Affichage du micro seulement si installé
    if vocal_disponible:
        st.write("🎤 Utiliser la voix :")
        audio = mic_recorder(start_prompt="⏺️ DÉMARRER", stop_prompt="⏹️ ARRÊTER", key='recorder_gym')
    else:
        st.info("💡 Note : Installez 'streamlit-mic-recorder' pour activer le bouton micro.")

    d_seance = st.date_input(L["date_label"], date.today(), key="date_seance_key")
    
    with st.form("form_gym_principal", clear_on_submit=True):
        zone = st.selectbox(L["zone_label"], ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos"])
        ex = st.selectbox(L["ex_label"], chest_options) if zone == "Pectoraux" else st.text_input(L["ex_label"])
        c1, c2 = st.columns(2)
        w = c1.number_input(L["weight"], value=135)
        r = c2.number_input(L["reps"], value=8)
        
        # Ce bouton est obligatoire pour éviter l'erreur "Missing Submit Button"
        submit = st.form_submit_button(L["add_set"])
        if submit:
            st.session_state.temp_workout.append({
                "Date": str(d_seance), "Zone": zone, "Exercice": ex, "Poids": w, "Reps": r
            })

    if st.session_state.temp_workout:
        st.table(pd.DataFrame(st.session_state.temp_workout))
        if st.button(L["validate"], type="primary"):
            st.session_state.logs.extend(st.session_state.temp_workout)
            st.session_state.temp_workout = []
            st.success("Séance enregistrée !")

# --- ONGLET 5 : CALENDRIER ---
with tab5:
    st.header("📅 Historique")
    d_cal = st.date_input("Date à consulter", date.today(), key="date_cal_key")
    df = pd.DataFrame(st.session_state.logs)
    if not df.empty:
        resultat = df[df['Date'] == str(d_cal)]
        if not resultat.empty:
            st.table(resultat[["Zone", "Exercice", "Poids", "Reps"]])
