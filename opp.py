import streamlit as st
import pandas as pd

# Configuration
st.set_page_config(page_title="Gym AI Agent PRO", layout="centered")

st.title("🤖 Mon Gym AI Agent - COACH PRO")

# --- BASE DE DONNÉES EXERCICES ---
exercices_info = {
    "Pectoraux": {"ex": "Développé Couché", "desc": "Cible le milieu du torse. Garde les omoplates serrées.", "img": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJueWp3bmZ3bmZ3bmZ3bmZ3/3o7TKL3Y9ujUv8m/giphy.gif"},
    "Dos": {"ex": "Tirage Buste Penché", "desc": "Cible l'épaisseur du dos. Ne courbe pas le bas du dos.", "img": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJueWp3bmZ3bmZ3bmZ3bmZ3/3o7TKscxYyYyYyYy/giphy.gif"},
    "Jambes (Squat)": {"ex": "Squat Barre", "desc": "Cible les quadriceps. Attention à tes genoux qui craquent : descends lentement !", "img": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJueWp3bmZ3bmZ3bmZ3bmZ3/3o7TKunYyYyYyYy/giphy.gif"},
    "Épaules": {"ex": "Développé Militaire", "desc": "Cible les deltoïdes. Gainage abdominal maximum.", "img": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJueWp3bmZ3bmZ3bmZ3bmZ3/3o7TKvnYyYyYyYy/giphy.gif"},
    "Abdominaux": {"ex": "Sit-ups", "desc": "Garde les pieds au sol et ne tire pas sur ta nuque.", "img": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJueWp3bmZ3bmZ3bmZ3bmZ3/3o7TKwnYyYyYyYy/giphy.gif"}
}

# --- SECTION : EXPLORATEUR DE MUSCLES ---
st.header("👤 Anatomie & Exercices")
st.write("Clique sur un groupe musculaire pour voir l'exercice recommandé :")

# Création de boutons pour chaque muscle
cols = st.columns(3)
muscle_choisi = None

if cols[0].button("胸 Pectoraux"): muscle_choisi = "Pectoraux"
if cols[1].button("🐢 Dos"): muscle_choisi = "Dos"
if cols[2].button("🍗 Jambes"): muscle_choisi = "Jambes (Squat)"
if cols[0].button("🛡️ Épaules"): muscle_choisi = "Épaules"
if cols[1].button("🍫 Abdominaux"): muscle_choisi = "Abdominaux"

if muscle_choisi:
    st.subheader(f"Meilleur exercice pour : {muscle_choisi}")
    st.info(f"**{exercices_info[muscle_choisi]['ex']}**")
    st.write(exercices_info[muscle_choisi]['desc'])
    # Note : J'utilise des GIFs ici pour l'exemple
    st.write("*(Ici s'affichera l'animation de l'exercice)*")

st.divider()

# --- ANALYSE VIDÉO ---
st.header("🎥 Analyse de Forme IA")
uploaded_video = st.file_uploader("Prends une vidéo de ton mouvement...", type=["mp4", "mov"])
if uploaded_video:
    st.video(uploaded_video)
    st.success("Vidéo reçue. Analyse de la trajectoire en cours...")

# --- LOG DE SÉANCE ---
st.header("🏋️ Enregistrer ta Performance")
with st.form("workout"):
    ex_name = st.selectbox("Exercice", list(exercices_info.keys()))
    w = st.number_input("Poids (lbs)", value=205)
    r = st.number_input("Reps", value=8)
    submitted = st.form_submit_button("Sauvegarder")
    if submitted:
        st.balloons()
        st.success("Données enregistrées dans ton profil !")
