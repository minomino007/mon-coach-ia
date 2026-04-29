import streamlit as st
import pandas as pd
from datetime import date
import openai  # Ajouté pour l'IA
from streamlit_mic_recorder import mic_recorder  # Ajouté pour le micro

# 1. CONFIGURATION & SECRETS
st.set_page_config(page_title="Gym AI Agent PRO", layout="centered", page_icon="🏋️")

# Connexion à ta clé API cachée dans les Secrets de Streamlit
if "OPENAI_API_KEY" in st.secrets:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
else:
    st.error("⚠️ La clé API est manquante dans les Secrets de Streamlit.")

# 2. DICTIONNAIRE DE TRADUCTION COMPLET
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
    },
    "English": {
        "tabs": ["📊 Profile", "🏋️ Today's Workout", "👤 Guide", "🎥 Vision", "📅 Calendar"],
        "prof_header": "👤 Your Fitness Profile",
        "edit_prof": "Edit Profile",
        "save": "Save",
        "workout_header": "🏋️ Log a Workout",
        "add_set": "➕ Add Set",
        "validate": "✅ Save Full Workout",
        "clear": "❌ Clear All",
        "lang_label": "Choose Language",
        "weight": "Weight (lbs)",
        "reps": "Reps",
        "date_label": "Date",
        "zone_label": "Muscle Zone",
        "ex_label": "Specific Exercise",
        "name_field": "Name",
        "obj_field": "Goal",
        "inj_field": "Injuries / Notes",
        "age_field": "Age",
        "height_field": "Height",
        "goals": ["Muscle Gain", "Fat Loss", "Strength", "Endurance"]
    }
}

# 3. INITIALISATION MÉMOIRE
if 'lang' not in st.session_state: st.session_state.lang = "Français"
if 'logs' not in st.session_state: st.session_state.logs = [] 
if 'notes_calendrier' not in st.session_state: st.session_state.notes_calendrier = {}
if 'temp_workout' not in st.session_state: st.session_state.temp_workout = []
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "nom": "Athlète", "age": 25, "grandeur": "5'10",
        "objectif": "Prise de masse", "poids": 205, "blessures": "Aucune", "niveau": "Intermédiaire"
    }

# 4. LISTE DES EXERCICES
chest_options = [
    "Développé couché", "Développé incliné", "Développé décliné", 
    "Développé haltères", "Écarté couché", "Écarté incliné", 
    "Pec deck (machine)", "Cross-over à la poulie", "Pompes", 
    "Pompes inclinées", "Pompes déclinées", "Dips (buste penché)", 
    "Pullover haltère", "Pullover à la poulie", "Machine chest press"
]

L = languages[st.session_state.lang]
st.title("🤖 Mon Gym AI Agent")

# 5. ONGLETS
tab1, tab2, tab3, tab4, tab5 = st.tabs(L["tabs"])

# --- ONGLET 1 : PROFIL ---
with tab1:
    st.header(L["prof_header"])
    new_lang = st.selectbox(L["lang_label"], ["Français", "English"], index=0 if st.session_state.lang == "Français" else 1)
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

    prof = st.session_state.user_profile
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric(L["weight"], f"{prof['poids']} lbs")
    col_m2.metric(L["obj_field"], prof['objectif'])
    col_m3.metric(L["age_field"], f"{prof['age']}")

# --- ONGLET 2 : SÉANCE DU JOUR ---
with tab2:
    st.header(L["workout_header"])
    
    # --- AJOUT DU MICRO ---
    st.write("🎙️ **Commande Vocale** : Appuie, dis ton exercice, et relâche.")
    audio_record = mic_recorder(
        start_prompt="🔴 Commencer l'enregistrement",
        stop_prompt="🟢 Terminer (Analyse en cours...)",
        key="gym_mic"
    )

    if audio_record:
        st.audio(audio_record['bytes']) # Affiche l'audio pour vérification
        # Ici, dans la prochaine étape, nous ajouterons l'extraction automatique des données
        st.info("Audio capturé ! (La transcription sera active dès que la clé API sera validée)")

    st.divider()
    date_seance = st.date_input(L["date_label"], date.today(), key="date_input_workout")
    
    with st.form("add_set_form_final", clear_on_submit=True):
        zone = st.selectbox(L["zone_label"], ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos"])
        ex = st.selectbox(L["ex_label"], chest_options) if zone == "Pectoraux" else st.text_input(L["ex_label"])
        col_w, col_r = st.columns(2)
        w_input = col_w.number_input(L["weight"], value=135)
        r_input = col_r.number_input(L["reps"], value=8)
        
        if st.form_submit_button(L["add_set"]):
            st.session_state.temp_workout.append({
                "Date": str(date_seance), "Zone": zone, "Exercice": ex, "Poids": w_input, "Reps": r_input
            })

    if st.session_state.temp_workout:
        st.subheader("Séries temporaires")
        st.dataframe(pd.DataFrame(st.session_state.temp_workout), use_container_width=True)
        cb1, cb2 = st.columns(2)
        if cb1.button(L["validate"], type="primary"):
            st.session_state.logs.extend(st.session_state.temp_workout)
            st.session_state.temp_workout = []
            st.success("Entraînement enregistré !")
            st.balloons()
        if cb2.button(L["clear"]):
            st.session_state.temp_workout = []
            st.rerun()

# --- ONGLET 5 : CALENDRIER ---
with tab5:
    st.header("📅 Historique")
    d_cal = st.date_input("Date", date.today(), key="date_input_calendar")
    df_global = pd.DataFrame(st.session_state.logs)
    if not df_global.empty:
        seance_du_jour = df_global[df_global['Date'] == str(d_cal)]
        if not seance_du_jour.empty:
            st.table(seance_du_jour[["Zone", "Exercice", "Poids", "Reps"]])
