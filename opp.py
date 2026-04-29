import streamlit as st
import pandas as pd
from datetime import date

# Configuration de l'application
st.set_page_config(page_title="Gym AI Agent PRO", layout="centered")

st.title("🤖 Mon Gym AI Agent")

# --- INITIALISATION DE LA MÉMOIRE ---
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'selection_muscle' not in st.session_state:
    st.session_state.selection_muscle = None
if 'notes_calendrier' not in st.session_state:
    st.session_state.notes_calendrier = {}

# --- BASE DE DONNÉES EXERCICES ---
exercices_info = {
    "Pectoraux": {"ex": "Développé Couché", "desc": "Cible le torse. Garde les omoplates serrées. Objectif : 225 lbs !"},
    "Dos": {"ex": "Tirage Buste Penché", "desc": "Cible l'épaisseur. Garde le dos droit."},
    "Jambes": {"ex": "Squat", "desc": "Cible les cuisses. ATTENTION : Contrôle la descente pour tes genoux."},
    "Épaules": {"ex": "Développé Militaire", "desc": "Cible les deltoïdes. Serre les abdos."},
    "Abdos": {"ex": "Sit-ups", "desc": "Ton favori. Ne tire pas sur la nuque."}
}

# --- CRÉATION DES ONGLETS (TABS) ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Profil", "🏋️ Séance", "👤 Guide", "🎥 Vision", "📅 Calendrier"])

# --- ONGLET 1 : PROFIL ---
with tab1:
    st.header("Tes Statistiques")
    col1, col2, col3 = st.columns(3)
    col1.metric("Poids", "205 lbs")
    col2.metric("Bench PR", "205 lbs")
    col3.metric("Squat PR", "225 lbs")
    if st.session_state.logs:
        df = pd.DataFrame(st.session_state.logs)
        st.line_chart(df.set_index("Date")["1RM Est."])

# --- ONGLET 2 : SÉANCE ---
with tab2:
    st.header("Noter ta séance")
    with st.form("workout_form"):
        exer = st.selectbox("Exercice", list(exercices_info.keys()))
        poids = st.number_input("Poids (lbs)", value=135)
        reps = st.number_input("Reps", value=8)
        rpe = st.slider("Difficulté (RPE)", 1, 10, 8)
        if st.form_submit_button("Enregistrer"):
            one_rm = poids * (1 + reps / 30)
            st.session_state.logs.append({"Date": pd.Timestamp.now().strftime("%Y-%m-%d"), "Exercice": exer, "Poids": poids, "1RM Est.": round(one_rm, 1)})
            st.balloons()

# --- ONGLET 3 : GUIDE ---
with tab3:
    st.header("Guide Muscles")
    c1, c2, c3 = st.columns(3)
    if c1.button("Pectoraux"): st.session_state.selection_muscle = "Pectoraux"
    if c2.button("Dos"): st.session_state.selection_muscle = "Dos"
    if c3.button("Jambes"): st.session_state.selection_muscle = "Jambes"
    if st.session_state.selection_muscle:
        m = st.session_state.selection_muscle
        st.info(f"**{exercices_info[m]['ex']}** : {exercices_info[m]['desc']}")

# --- ONGLET 4 : VISION ---
with tab4:
    st.header("Analyse IA")
    video_file = st.file_uploader("Vidéo de ton Squat", type=["mp4", "mov"])
    if video_file: st.video(video_file)

# --- ONGLET 5 : CALENDRIER ---
with tab5:
    st.header("📅 Agenda de l'athlète")
    
    # 1. Sélection de la date
    d = st.date_input("Sélectionne une date", date.today())
    date_str = str(d)
    
    # 2. Zone de texte pour la note
    note_existante = st.session_state.notes_calendrier.get(date_str, "")
    nouvelle_note = st.text_area("Notes pour ce jour (Séance prévue, poids, ressenti...)", value=note_existante)
    
    if st.button("Sauvegarder la note"):
        st.session_state.notes_calendrier[date_str] = nouvelle_note
        st.success(f"Note enregistrée pour le {d} !")

    # 3. Affichage de l'historique des notes
    if st.session_state.notes_calendrier:
        st.divider()
        st.subheader("Tes notes enregistrées")
        for date_key, contenu in sorted(st.session_state.notes_calendrier.items(), reverse=True):
            if contenu:
                with st.expander(f"🗓️ {date_key}"):
                    st.write(contenu)
