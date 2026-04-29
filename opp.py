import streamlit as st
import pandas as pd
from datetime import date

# 1. CONFIGURATION
st.set_page_config(page_title="Gym AI Agent PRO", layout="centered", page_icon="🏋️")

# 2. DICTIONNAIRE DE TRADUCTION
languages = {
    "Français": {
        "tabs": ["📊 Profil", "🏋️ Séance", "👤 Guide", "🎥 Vision", "📅 Calendrier"],
        "prof_header": "👤 Ton Profil Sportif",
        "edit_prof": "Modifier le profil",
        "save": "Sauvegarder",
        "workout_header": "🏋️ Enregistrer un entraînement",
        "add_set": "➕ Ajouter la série",
        "validate": "✅ Valider toute la séance",
        "clear": "❌ Tout effacer",
        "lang_label": "Choisir la langue",
        "weight": "Poids (lbs)",
        "reps": "Répétitions"
    },
    "English": {
        "tabs": ["📊 Profile", "🏋️ Workout", "👤 Guide", "🎥 Vision", "📅 Calendar"],
        "prof_header": "👤 Your Fitness Profile",
        "edit_prof": "Edit Profile",
        "save": "Save",
        "workout_header": "🏋️ Log a Workout",
        "add_set": "➕ Add Set",
        "validate": "✅ Save Full Workout",
        "clear": "❌ Clear All",
        "lang_label": "Choose Language",
        "weight": "Weight (lbs)",
        "reps": "Reps"
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
        "objectif": "Prise de masse", "poids": 205, "blessures": "Aucune"
    }

# Raccourci pour la langue choisie
L = languages[st.session_state.lang]

st.title("🤖 Mon Gym AI Agent")

# 4. ONGLETS DYNAMIQUES
tab1, tab2, tab3, tab4, tab5 = st.tabs(L["tabs"])

# --- ONGLET 1 : PROFIL (AJOUT LANGUE) ---
with tab1:
    st.header(L["prof_header"])
    
    # Sélecteur de langue en haut du profil
    new_lang = st.selectbox(L["lang_label"], ["Français", "English"], index=0 if st.session_state.lang == "Français" else 1)
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

    prof = st.session_state.user_profile
    c1, c2 = st.columns(2)
    c1.metric(L["weight"], f"{prof['poids']} lbs")
    c2.metric("Objectif / Goal", prof['objectif'])
    
    with st.expander(L["edit_prof"]):
        with st.form("edit_prof_form"):
            n = st.text_input("Nom / Name", value=prof["nom"])
            p = st.number_input(L["weight"], value=prof["poids"])
            b = st.text_area("Blessures / Injuries", value=prof["blessures"])
            if st.form_submit_button(L["save"]):
                st.session_state.user_profile.update({"nom": n, "poids": p, "blessures": b})
                st.rerun()

    if st.session_state.logs:
        df_evol = pd.DataFrame(st.session_state.logs)
        st.line_chart(df_evol.set_index("Date")["Poids"])

# --- ONGLET 2 : SÉANCE ---
with tab2:
    st.header(L["workout_header"])
    date_seance = st.date_input("Date", date.today())
    
    with st.form("add_set_multi", clear_on_submit=True):
        zone = st.selectbox("Zone", ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos"])
        ex = st.text_input("Exercice")
        col_w, col_r = st.columns(2)
        w = col_w.number_input(L["weight"], value=135)
        r = col_r.number_input(L["reps"], value=8)
        if st.form_submit_button(L["add_set"]):
            st.session_state.temp_workout.append({"Date": str(date_seance), "Zone": zone, "Exercice": ex, "Poids": w, "Reps": r})

    if st.session_state.temp_workout:
        st.dataframe(pd.DataFrame(st.session_state.temp_workout), use_container_width=True)
        c_b1, c_b2 = st.columns(2)
        if c_b1.button(L["validate"], type="primary"):
            st.session_state.logs.extend(st.session_state.temp_workout)
            st.session_state.temp_workout = []
            st.success("OK!")
        if c_
