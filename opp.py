import streamlit as st
import pandas as pd
from datetime import date

# 1. CONFIGURATION
st.set_page_config(page_title="Gym AI Agent PRO", layout="centered", page_icon="🏋️")

# 2. DICTIONNAIRE DE TRADUCTION COMPLET
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
        "reps": "Répétitions",
        "date_label": "Date de la séance",
        "zone_label": "Zone musculaire",
        "ex_label": "Exercice spécifique"
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
        "reps": "Reps",
        "date_label": "Workout Date",
        "zone_label": "Muscle Zone",
        "ex_label": "Specific Exercise"
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

# 4. LISTE DES 15 EXERCICES PECTORAUX
chest_options = [
    "Développé couché", "Développé incliné", "Développé décliné", 
    "Développé haltères", "Écarté couché", "Écarté incliné", 
    "Pec deck (machine)", "Cross-over à la poulie", "Pompes", 
    "Pompes inclinées", "Pompes déclinées", "Dips (buste penché)", 
    "Pullover haltère", "Pullover à la poulie", "Machine chest press"
]

# Raccourci pour la langue
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
    col_m2.metric("Objectif", prof['objectif'])
    col_m3.metric("Âge", f"{prof['age']}")
    
    st.write(f"**Nom :** {prof['nom']} | **Grandeur :** {prof['grandeur']}")
    st.warning(f"🩹 **Blessures :** {prof['blessures']}")

    with st.expander(L["edit_prof"]):
        with st.form("edit_profile_final"):
            n = st.text_input("Nom", value=prof["nom"])
            p = st.number_input(L["weight"], value=prof["poids"])
            obj = st.selectbox("Objectif", ["Prise de masse", "Perte de gras", "Force"], index=0)
            b = st.text_area("Blessures", value=prof["blessures"])
            if st.form_submit_button(L["save"]):
                st.session_state.user_profile.update({"nom": n, "poids": p, "objectif": obj, "blessures": b})
                st.rerun()

    if st.session_state.logs:
        df_evol = pd.DataFrame(st.session_state.logs)
        st.line_chart(df_evol.set_index("Date")["Poids"])

# --- ONGLET 2 : SÉANCE (MULTI-SÉRIES + DATE + LISTE CHEST) ---
with tab2:
    st.header(L["workout_header"])
    date_seance = st.date_input(L["date_label"], date.today())
    
    with st.form("add_set_form_final", clear_on_submit=True):
        zone = st.selectbox(L["zone_label"], ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos"])
        
        if zone == "Pectoraux":
            ex = st.selectbox(L["ex_label"], chest_options)
        else:
            ex = st.text_input("Exercice")
            
        col_w, col_r = st.columns(2)
        w = col_w.number_input(L["weight"], value=135)
        r = col_r.number_input(L["reps"], value=8)
        
        if st.form_submit_button(L["add_set"]):
            st.session_state.temp_workout.append({
                "Date": str(date_seance), "Zone": zone, "Exercice": ex, "Poids": w, "Reps": r
            })

    if st.session_state.temp_workout:
        st.write("---")
        st.dataframe(pd.DataFrame(st.session_state.temp_workout), use_container_width=True)
        cb1, cb2 = st.columns(2)
        if cb1.button(L["validate"], type="primary"):
            st.session_state.logs.extend(st.session_state.temp_workout)
            st.session_state.temp_workout = []
            st.success("Enregistré !")
            st.balloons()
        if cb2.button(L["clear"]):
            st.session_state.temp_workout = []
            st.rerun()

# --- ONGLET 3 : GUIDE ---
with tab3:
    st.header("👤 Guide Technique")
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
    d_cal = st.date_input("Date", date.today(), key="cal_final_ver")
    n_cal = st.text_area("Note", value=st.session_state.notes_calendrier.get(str(d_cal), ""))
    if st.button(L["save"], key="save_note_cal"):
        st.session_state.notes_calendrier[str(d_cal)] = n_cal
        st.success("Note ok !")
