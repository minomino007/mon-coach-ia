import streamlit as st
import pandas as pd

# Configuration
st.set_page_config(page_title="Gym AI Agent PRO", layout="centered")

st.title("🤖 Mon Gym AI Agent")

# --- BASE DE DONNÉES ---
exercices_info = {
    "Pectoraux": {"ex": "Développé Couché", "desc": "Cible le milieu du torse. Garde les omoplates serrées contre le banc."},
    "Dos": {"ex": "Tirage Buste Penché", "desc": "Cible l'épaisseur du dos. Garde le dos droit, ne force pas avec tes lombaires."},
    "Jambes": {"ex": "Squat Barre", "desc": "Cible les cuisses. Pour ton genou : descends doucement et remonte de façon explosive."},
    "Épaules": {"ex": "Développé Militaire", "desc": "Cible les épaules. Garde tes abdos bien serrés (gainage)."},
    "Abdominaux": {"ex": "Sit-ups", "desc": "Ton exercice favori. Ne tire pas sur ta nuque, croise les bras sur ton torse."}
}

# --- LOGIQUE DE MÉMOIRE (STATE) ---
if 'selection' not in st.session_state:
    st.session_state.selection = None

# --- SECTION : ANATOMIE ---
st.header("👤 Choisis ton muscle")

col1, col2, col3 = st.columns(3)

# Quand on clique, on enregistre le choix dans la mémoire de l'app
if col1.button("Pectoraux"): st.session_state.selection = "Pectoraux"
if col2.button("Dos"): st.session_state.selection = "Dos"
if col3.button("Jambes"): st.session_state.selection = "Jambes"
if col1.button("Épaules"): st.session_state.selection = "Épaules"
if col2.button("Abdos"): st.session_state.selection = "Abdominaux"

# AFFICHAGE DU RÉSULTAT
if st.session_state.selection:
    choix = st.session_state.selection
    st.markdown(f"### 🎯 Focus : {choix}")
    st.success(f"**Exercice recommandé :** {exercices_info[choix]['ex']}")
    st.write(exercices_info[choix]['desc'])
    
st.divider()

# --- ANALYSE VIDÉO ---
st.header("🎥 Analyse Vidéo")
up_vid = st.file_uploader("Upload ton Squat", type=["mp4", "mov"])
if up_vid:
    st.video(up_vid)

# --- LOG SÉANCE ---
st.header("🏋️ Log Séance")
with st.form("log"):
    poids = st.number_input("Poids (lbs)", value=205)
    reps = st.number_input("Répétitions", value=8)
    if st.form_submit_button("Sauvegarder"):
        st.balloons()
