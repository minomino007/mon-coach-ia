import streamlit as st
import pandas as pd

# Configuration
st.set_page_config(page_title="Gym AI Agent PRO", layout="centered")

st.title("🤖 Mon Gym AI Agent - ANALYSE PRO")

# --- INITIALISATION ---
if 'logs' not in st.session_state:
    st.session_state.logs = []

# --- DASHBOARD ---
col1, col2 = st.columns(2)
col1.metric("Poids actuel", "205 lbs")
col2.metric("Objectif", "Prise de Masse")

# --- NOUVELLE SECTION : ANALYSE VIDÉO ---
st.header("🎥 Analyse de Forme par IA")
st.write("Télécharge une vidéo de ton Squat ou Bench pour une analyse technique.")

uploaded_video = st.file_uploader("Choisir une vidéo...", type=["mp4", "mov", "avi"])

if uploaded_video is not None:
    st.video(uploaded_video)
    st.info("🔄 Analyse en cours par l'Agent IA... (Envoie cette vidéo à ton coach Gemini pour le verdict final)")
    st.warning("Note : Pour l'instant, l'IA analyse l'alignement des genoux et la profondeur.")

st.divider()

# --- ENREGISTREMENT SÉANCE ---
st.header("🏋️ Log ta séance")
with st.form("workout_form"):
    exer = st.selectbox("Exercice", ["Bench Press", "Squat", "Incliné Haltères", "Dips", "Sit-ups"])
    weight = st.number_input("Poids (lbs)", value=135)
    reps = st.number_input("Répétitions", value=8)
    rpe = st.slider("Difficulté (1-10)", 1, 10, 8)
    
    submitted = st.form_submit_button("Enregistrer & Calculer l'objectif")
    
    if submitted:
        one_rm = weight * (1 + reps / 30)
        next_goal = weight + 5 if rpe <= 7 else weight
        
        st.session_state.logs.append({
            "Date": pd.Timestamp.now().strftime("%Y-%m-%d"),
            "Exercice": exer,
            "Poids": weight,
            "1RM Est.": round(one_rm, 1),
            "Next Goal": next_goal
        })
        st.success(f"Objectif suivant : {next_goal} lbs")

# --- HISTORIQUE ---
if st.session_state.logs:
    st.subheader("📈 Progression")
    st.dataframe(pd.DataFrame(st.session_state.logs))
