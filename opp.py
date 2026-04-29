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
        "objectif": "Prise de masse", "poids": 205, "blessures": "Aucune"
    }

# 4. LISTE DES EXERCICES PAR ZONE
exercises_db = {
    "Pectoraux": [
        "Développé couché", "Développé incliné", "Développé décliné", 
        "Développé haltères", "Écarté couché", "Écarté incliné", 
        "Pec deck (machine)", "Cross-over à la poulie", "Pompes", 
        "Pompes inclinées", "Pompes déclinées", "Dips (buste penché)", 
        "Pullover haltère", "Pullover à la poulie", "Machine chest press"
    ],
    "Dos": ["Tirage poitrine", "Rowing barre", "Tractions", "Deadlift", "Rowing haltère"],
    "Jambes": ["Squat", "Presse à cuisses", "Fentes", "Leg Extension", "Leg Curl"],
    "Épaules": ["Développé militaire", "Élévations latérales", "Oiseau", "Face pull"],
    "Abdos": ["Crunch", "Planche", "Levé de jambes", "Roulette"]
}

L = languages[st.session_state.lang]
st.title("🤖 Mon Gym AI Agent")

tab1, tab2, tab3, tab4, tab5 = st.tabs(L["tabs"])

# --- ONGLET 1 : PROFIL ---
with tab1:
    st.header(L["prof_header"])
    new_lang = st.selectbox(L["lang_label"], ["Français", "English"], index=0 if st.session_state.lang == "Français" else 1)
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()
    prof = st.session_state.user_profile
    with st.expander(L["edit_prof"]):
        with st.form("edit_prof"):
            n = st.text_input(L["name_field"], value=prof["nom"])
            p = st.number_input(L["weight"], value=prof["poids"])
            obj = st.selectbox(L["obj_field"], L["goals"])
            if st.form_submit_button(L["save"]):
                st.session_state.user_profile.update({"nom": n, "poids": p, "objectif": obj})
                st.rerun()

# --- ONGLET 2 : SÉANCE DU JOUR (MULTI-ZONES) ---
with tab2:
    st.header(L["workout_header"])
    date_seance = st.date_input(L["date_label"], date.today())
    
    # Formulaire pour ajouter une série
    with st.form("add_set_form", clear_on_submit=True):
        # Choix de la zone
        zone_choisie = st.selectbox(L["zone_label"], list(exercises_db.keys()))
        
        # Choix de l'exercice dynamique selon la zone
        liste_ex = exercises_db[zone_choisie]
        ex_choisi = st.selectbox(L["ex_label"], liste_ex)
        
        c1, c2 = st.columns(2)
        w = c1.number_input(L["weight"], value=135, step=5)
        r = c2.number_input(L["reps"], value=8, step=1)
        
        if st.form_submit_button(L["add_set"]):
            st.session_state.temp_workout.append({
                "Date": str(date_seance), "Zone": zone_choisie, 
                "Exercice": ex_choisi, "Poids": w, "Reps": r
            })

    # Affichage du panier
    if st.session_state.temp_workout:
        st.subheader("Séries ajoutées à cette séance :")
        st.table(pd.DataFrame(st.session_state.temp_workout)[["Zone", "Exercice", "Poids", "Reps"]])
        
        col_v, col_c = st.columns(2)
        if col_v.button(L["validate"], type="primary"):
            st.session_state.logs.extend(st.session_state.temp_workout)
            st.session_state.temp_workout = []
            st.success("Séance complète enregistrée !")
            st.balloons()
        if col_c.button(L["clear"]):
            st.session_state.temp_workout = []
            st.rerun()

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
    st.header("📅 Historique")
    d_view = st.date_input("Consulter une date", date.today())
    df_history = pd.DataFrame(st.session_state.logs)
    if not df_history.empty:
        seance = df_history[df_history['Date'] == str(d_view)]
        if not seance.empty:
            st.table(seance[["Zone", "Exercice", "Poids", "Reps"]])
        else:
            st.info("Rien pour cette date.")
    
    st.divider()
    n_txt = st.text_area("Note du jour", value=st.session_state.notes_calendrier.get(str(d_view), ""))
    if st.button(L["save"]):
        st.session_state.notes_calendrier[str(d_view)] = n_txt
        st.success("Note ok")
