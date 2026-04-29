import streamlit as st
import pandas as pd
from datetime import date

# Configuration
st.set_page_config(page_title="Gym AI Agent PRO", layout="centered")

# --- INITIALISATION MÉMOIRE (Pour sauvegarder le profil) ---
if 'logs' not in st.session_state: st.session_state.logs = []
if 'selection_muscle' not in st.session_state: st.session_state.selection_muscle = "Pectoraux"
if 'notes_calendrier' not in st.session_state: st.session_state.notes_calendrier = {}

# Initialisation des données du profil si elles n'existent pas
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "nom": "Athlète",
        "age": 25,
        "grandeur": "5'10",
        "objectif": "Prise de masse",
        "niveau": "Intermédiaire",
        "poids": 205,
        "blessures": "Aucune"
    }

st.title("🤖 Mon Gym AI Agent")

# --- ONGLETS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Profil", "🏋️ Séance", "👤 Guide", "🎥 Vision", "📅 Calendrier"])

# --- ONGLET 1 : CRÉATION ET AFFICHAGE DU PROFIL ---
with tab1:
    st.header("👤 Ton Profil Sportif")
    
    # Mode édition du profil
    with st.expander("Modifier mes informations personnelles"):
        with st.form("edit_profile"):
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom", value=st.session_state.user_profile["nom"])
            age = c2.number_input("Âge", value=st.session_state.user_profile["age"])
            grandeur = c1.text_input("Grandeur (ex: 5'11)", value=st.session_state.user_profile["grandeur"])
            objectif = c2.selectbox("Objectif", ["Prise de masse", "Perte de gras", "Force pure", "Endurance"], index=0)
            poids_actuel = c1.number_input("Poids actuel (lbs)", value=st.session_state.user_profile["poids"])
            niveau = c2.selectbox("Niveau", ["Débutant", "Intermédiaire", "Avancé"], index=1)
            blessures = st.text_area("Historique de blessures (ex: Genou gauche sensible)", value=st.session_state.user_profile["blessures"])
            
            if st.form_submit_button("Sauvegarder le profil"):
                st.session_state.user_profile = {
                    "nom": nom, "age": age, "grandeur": grandeur,
                    "objectif": objectif, "niveau": niveau, "poids": poids_actuel,
                    "blessures": blessures
                }
                st.success("Profil mis à jour !")

    # Affichage des informations
    prof = st.session_state.user_profile
    st.divider()
    col_a, col_b = st.columns(2)
    col_a.markdown(f"**Nom :** {prof['nom']}")
    col_a.markdown(f"**Âge :** {prof['age']} ans")
    col_a.markdown(f"**Grandeur :** {prof['grandeur']}")
    col_b.markdown(f"**Objectif :** {prof['objectif']}")
    col_b.markdown(f"**Niveau :** {prof['niveau']}")
    col_b.markdown(f"**Poids :** {prof['poids']} lbs")
    st.warning(f"⚠️ **Notes médicales/blessures :** {prof['blessures']}")

    if st.session_state.logs:
        st.subheader("Évolution du poids")
        df = pd.DataFrame(st.session_state.logs)
        st.line_chart(df.set_index("Date")["Poids"])

# --- LES AUTRES ONGLETS (RESTENT IDENTIQUES) ---
with tab2:
    st.header("Noter ta séance")
    with st.form("workout_form"):
        exer = st.selectbox("Muscle", ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos"])
        p = st.number_input("Poids (lbs)", value=135)
        if st.form_submit_button("Enregistrer"):
            st.session_state.logs.append({"Date": str(date.today()), "Poids": p})
            st.success("Enregistré !")

with tab3:
    st.header("Guide Muscles")
    c1, c2, c3 = st.columns(3)
    if c1.button("Pectoraux"): st.session_state.selection_muscle = "Pectoraux"
    if c2.button("Dos"): st.session_state.selection_muscle = "Dos"
    if c3.button("Jambes"): st.session_state.selection_muscle = "Jambes"
    st.info(f"Muscle sélectionné : {st.session_state.selection_muscle}")

with tab4:
    st.header("Vision IA")
    v = st.file_uploader("Vidéo", type=["mp4", "mov"])
    if v: st.video(v)

with tab5:
    st.header("📅 Calendrier")
    d = st.date_input("Date", date.today())
    note = st.text_area("Note", value=st.session_state.notes_calendrier.get(str(d), ""))
    if st.button("Enregistrer Note"):
        st.session_state.notes_calendrier[str(d)] = note
        st.success("Note ok !")
