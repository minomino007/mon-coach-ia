import streamlit as st
import pandas as pd
from datetime import date

# Configuration
st.set_page_config(page_title="Gym AI Agent PRO", layout="centered")

# --- MÉMOIRE ---
if 'logs' not in st.session_state: st.session_state.logs = []
if 'selection_muscle' not in st.session_state: st.session_state.selection_muscle = "Pectoraux"
if 'notes_calendrier' not in st.session_state: st.session_state.notes_calendrier = {}

st.title("🤖 Mon Gym AI Agent")

# --- ONGLETS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Profil", "🏋️ Séance", "👤 Guide", "🎥 Vision", "📅 Calendrier"])

# --- ONGLET 1 : PROFIL ---
with tab1:
    st.header("Tes Statistiques")
    col1, col2 = st.columns(2)
    col1.metric("Poids", "205 lbs")
    col2.metric("Objectif", "Prise de Masse")
    if st.session_state.logs:
        df = pd.DataFrame(st.session_state.logs)
        st.line_chart(df.set_index("Date")["Poids"])

# --- ONGLET 2 : SÉANCE ---
with tab2:
    st.header("Noter ta séance")
    with st.form("workout_form"):
        exer = st.selectbox("Muscle", ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos"])
        poids = st.number_input("Poids (lbs)", value=135)
        reps = st.number_input("Reps", value=8)
        if st.form_submit_button("Enregistrer"):
            st.session_state.logs.append({"Date": str(date.today()), "Poids": poids})
            st.balloons()
            st.success("Enregistré !")

# --- ONGLET 3 : GUIDE (Retour aux boutons) ---
with tab3:
    st.header("Guide Muscles")
    st.write("Clique sur un muscle :")
    
    c1, c2, c3 = st.columns(3)
    if c1.button("Pectoraux"): st.session_state.selection_muscle = "Pectoraux"
    if c2.button("Dos"): st.session_state.selection_muscle = "Dos"
    if c3.button("Jambes"): st.session_state.selection_muscle = "Jambes"
    
    muscle = st.session_state.selection_muscle
    st.divider()
    
    if muscle == "Pectoraux":
        st.subheader("🔥 Top Exercices Pectoraux")
        st.write("- Développé couché\n- Développé incliné\n- Dips\n- Pompes\n- Écartés haltères")
        st.video("https://www.youtube.com/watch?v=gRVjAtPip0Y")
    else:
        st.info(f"Section {muscle} sélectionnée. Prêt pour l'entraînement !")

# --- ONGLET 4 : VISION ---
with tab4:
    st.header("Vision IA")
    v = st.file_uploader("Upload ta vidéo", type=["mp4", "mov"])
    if v: st.video(v)

# --- ONGLET 5 : CALENDRIER ---
with tab5:
    st.header("📅 Calendrier")
    d_choisie = st.date_input("Sélectionne une date :", date.today())
    d_str = str(d_choisie)
    
    note_existante = st.session_state.notes_calendrier.get(d_str, "")
    nouvelle_note = st.text_area("Note du jour :", value=note_existante)
    
    if st.button("Sauvegarder"):
        st.session_state.notes_calendrier[d_str] = nouvelle_note
        st.success("Note enregistrée !")
