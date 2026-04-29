import streamlit as st
import pandas as pd
from datetime import date
from streamlit_mic_recorder import mic_recorder # Nouvelle importation

# 1. CONFIGURATION
st.set_page_config(page_title="Gym AI Agent PRO", layout="centered", page_icon="🏋️")

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
        "goals": ["Prise de masse", "Perte de gras", "Force", "Endurance"],
        "voice_btn": "🎤 Parler pour remplir (ex: Pectoraux Développé couché 100 kilos 10 reps)",
        "voice_success": "Commande vocale reçue !"
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
        "goals": ["Muscle Gain", "Fat Loss", "Strength", "Endurance"],
        "voice_btn": "🎤 Speak to fill (ex: Chest Bench Press 200 lbs 10 reps)",
        "voice_success": "Voice command received!"
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

# Variables temporaires pour le vocal
if 'voice_data' not in st.session_state:
    st.session_state.voice_data = {"zone": "Pectoraux", "ex": "", "w": 135, "r": 8}

chest_options = [
    "Développé couché", "Développé incliné", "Développé décliné", 
    "Développé haltères", "Écarté couché", "Écarté incliné", 
    "Pec deck (machine)", "Cross-over à la poulie", "Pompes", 
    "Pompes inclinées", "Pompes déclinées", "Dips (buste penché)", 
    "Pullover haltère", "Pullover à la poulie", "Machine chest press"
]

L = languages[st.session_state.lang]
st.title("🤖 Mon Gym AI Agent")
tab1, tab2, tab3, tab4, tab5 = st.tabs(L["tabs"])

# --- ONGLET 1 : PROFIL (Inchangé) ---
with tab1:
    st.header(L["prof_header"])
    new_lang = st.selectbox(L["lang_label"], ["Français", "English"], index=0 if st.session_state.lang == "Français" else 1)
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()
    prof = st.session_state.user_profile
    with st.expander(L["edit_prof"]):
        with st.form("edit_profile_form"):
            n = st.text_input(L["name_field"], value=prof["nom"])
            p = st.number_input(L["weight"], value=prof["poids"])
            if st.form_submit_button(L["save"]):
                st.session_state.user_profile.update({"nom": n, "poids": p})
                st.rerun()

# --- ONGLET 2 : SÉANCE DU JOUR (AVEC VOCAL) ---
with tab2:
    st.header(L["workout_header"])
    
    # --- SECTION VOCALE ---
    st.write(L["voice_btn"])
    audio = mic_recorder(start_prompt="⏺️ START", stop_prompt="⏹️ STOP", key='recorder')
    
    if audio:
        # Note: Dans une version réelle avec API, on enverrait l'audio ici. 
        # Pour cette version, nous activons l'interface de saisie.
        st.info("Analyse de la voix en cours... (Simulé)")
        # Ici, on pourrait intégrer OpenAI Whisper pour transformer l'audio en texte précis.

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
            st.success(L["voice_success"])
            st.balloons()
        if cb2.button(L["clear"]):
            st.session_state.temp_workout = []
            st.rerun()

# --- ONGLET 3 : GUIDE / 4 : VISION / 5 : CALENDRIER (Inchangés) ---
with tab3:
    st.header("👤 Guide")
    if st.button("Démonstration Pectoraux"):
        st.video("https://www.youtube.com/watch?v=gRVjAtPip0Y")

with tab4:
    st.header("🎥 Vision IA")
    up = st.file_uploader("Upload", type=["mp4", "mov"])
    if up: st.video(up)

with tab5:
    st.header("📅 Historique")
    d_cal = st.date_input("Choisir une date", date.today(), key="date_input_calendar")
    df_global = pd.DataFrame(st.session_state.logs)
    if not df_global.empty:
        seance_du_jour = df_global[df_global['Date'] == str(d_cal)]
        if not seance_du_jour.empty:
            st.table(seance_du_jour[["Zone", "Exercice", "Poids", "Reps"]])
    
    n_cal = st.text_area("Note du jour", value=st.session_state.notes_calendrier.get(str(d_cal), ""))
    if st.button(L["save"], key="save_note_cal"):
        st.session_state.notes_calendrier[str(d_cal)] = n_cal
        st.success("Note enregistrée !")
