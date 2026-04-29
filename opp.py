import streamlit as st
import pandas as pd
from datetime import date

# 1. CONFIGURATION
st.set_page_config(page_title="Gym AI Agent PRO", layout="centered", page_icon="🏋️")

# 2. DICTIONNAIRE DE TRADUCTION
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
        "inj_field": "Blessures",
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
        "lang_label": "Language",
        "weight": "Weight (lbs)",
        "reps": "Reps",
        "date_label": "Date",
        "zone_label": "Muscle Zone",
        "ex_label": "Exercise",
        "name_field": "Name",
        "obj_field": "Goal",
        "inj_field": "Injuries",
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
        "objectif": "Prise de masse", "poids": 205, "blessures": "Aucune"
    }

# Liste simple pour les pectoraux
chest_options = ["Développé couché", "Développé incliné", "Développé décliné", "Développé haltères", "Écarté couché", "Pompes", "Dips", "Pec Deck"]

L = languages[st.session_state.lang]
st.title("🤖 Mon Gym AI Agent")

tab1, tab2, tab3, tab4, tab5 = st.tabs(L["tabs"])

# --- ONGLET 1 : PROFIL ---
with tab1:
    st.header(L["prof_header"])
    st.session_state.lang = st.selectbox(L["lang_label"], ["Français", "English"], index=0 if st.session_state.lang == "Français" else 1)
    
    prof = st.session_state.user_profile
    st.write(f"**{L['name_field']}**: {prof['nom']} | **{L['weight']}**: {prof['poids']} lbs")
    
    with st.expander(L["edit_prof"]):
        with st.form("edit_form"):
            n = st.text_input(L["name_field"], value=prof["nom"])
            p = st.number_input(L["weight"], value=prof["poids"])
            if st.form_submit_button(L["save"]):
                st.session_state.user_profile.update({"nom": n, "poids": p})
                st.rerun()

# --- ONGLET 2 : SÉANCE DU JOUR ---
with tab2:
    st.header(L["workout_header"])
    d_seance = st.date_input(L["date_label"], date.today())
    
    with st.form("workout_form"):
        zone = st.selectbox(L["zone_label"], ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos"])
        if zone == "Pectoraux":
            ex = st.selectbox(L["ex_label"], chest_options)
        else:
            ex = st.text_input(L["ex_label"])
            
        c1, c2 = st.columns(2)
        w = c1.number_input(L["weight"], value=135)
        r = c2.number_input(L["reps"], value=8)
        
        if st.form_submit_button(L["add_set"]):
            st.session_state.temp_workout.append({"Date": str(d_seance), "Zone": zone, "Exercice": ex, "Poids": w, "Reps": r})

    if st.session_state.temp_workout:
        st.table(pd.DataFrame(st.session_state.temp_workout))
        if st.button(L["validate"], type="primary"):
            st.session_state.logs.extend(st.session_state.temp_workout)
            st.session_state.temp_workout = []
            st.success("Enregistré !")

# --- ONGLET 3 : GUIDE ---
with tab3:
    st.header("👤 Guide")
    if st.button("Démonstration Pectoraux"):
        st.video("https://www.youtube.com/watch?v=gRVjAtPip0Y")

# --- ONGLET 4 : VISION ---
with tab4:
    st.header("🎥 Vision IA")
    up = st.file_uploader("Upload", type=["mp4", "mov"])
    if up: st.video(up)

# --- ONGLET 5 : CALENDRIER ---
with tab5:
    st.header("📅 Calendrier")
    d_view = st.date_input("Date", date.today())
    df_history = pd.DataFrame(st.session_state.logs)
    if not df_history.empty:
        seance = df_history[df_history['Date'] == str(d_view)]
        if not seance.empty:
            st.table(seance[["Zone", "Exercice", "Poids", "Reps"]])
    
    n_txt = st.text_area("Note", value=st.session_state.notes_calendrier.get(str(d_view), ""))
    if st.button(L["save"]):
        st.session_state.notes_calendrier[str(d_view)] = n_txt
        st.success("OK")
