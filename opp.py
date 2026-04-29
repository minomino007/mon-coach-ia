import streamlit as st
import pandas as pd
from datetime import date

# Configuration
st.set_page_config(page_title="Gym AI Agent PRO", layout="centered")

# --- INITIALISATION MÉMOIRE ---
if 'logs' not in st.session_state: st.session_state.logs = []
if 'selection_muscle' not in st.session_state: st.session_state.selection_muscle = "Pectoraux"
if 'notes_calendrier' not in st.session_state: st.session_state.notes_calendrier = {}
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {"nom": "Athlète", "age": 25, "grandeur": "5'10", "objectif": "Prise de masse", "niveau": "Intermédiaire", "poids": 205, "blessures": "Aucune"}

# --- LISTE DES EXERCICES PECTORAUX ---
chest_options = [
    "Développé couché", "Développé incliné", "Développé décliné", 
    "Développé haltères", "Écarté couché", "Écarté incliné", 
    "Pec deck (machine)", "Cross-over à la poulie", "Pompes", 
    "Pompes inclinées", "Pompes déclinées", "Dips (buste penché)", 
    "Pullover haltère", "Pullover à la poulie", "Machine chest press"
]

st.title("🤖 Mon Gym AI Agent")

# --- ONGLETS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Profil", "🏋️ Séance", "👤 Guide", "🎥 Vision", "📅 Calendrier"])

# --- ONGLET 1 : PROFIL ---
with tab1:
    st.header("👤 Ton Profil")
    prof = st.session_state.user_profile
    st.write(f"**Nom :** {prof['nom']} | **Objectif :** {prof['objectif']}")
    st.write(f"**Poids :** {prof['poids']} lbs | **Blessures :** {prof['blessures']}")
    if st.session_state.logs:
        df = pd.DataFrame(st.session_state.logs)
        st.line_chart(df.set_index("Date")["Poids"])

# --- ONGLET 2 : SÉANCE (MISE À JOUR) ---
with tab2:
    st.header("🏋️ Enregistrer une série")
    
    with st.form("workout_detailed"):
        # 1. Choisir la zone
        zone = st.selectbox("Zone musculaire", ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos"])
        
        # 2. Choisir l'exercice (Dynamique pour les pectoraux)
        if zone == "Pectoraux":
            exercice = st.selectbox("Exercice spécifique", chest_options)
        else:
            exercice = st.text_input("Nom de l'exercice", placeholder="Ex: Tirage poulie")
        
        # 3. Noter les performances
        col_w, col_r = st.columns(2)
        poids_saisi = col_w.number_input("Poids (lbs)", min_value=0, value=135, step=5)
        reps_saisies = col_r.number_input("Répétitions", min_value=0, value=8, step=1)
        
        submit = st.form_submit_button("Sauvegarder la série")
        
        if submit:
            st.session_state.logs.append({
                "Date": str(date.today()),
                "Zone": zone,
                "Exercice": exercice,
                "Poids": poids_saisi,
                "Reps": reps_saisies
            })
            st.balloons()
            st.success(f"Série de {exercice} enregistrée !")

    # Affichage des dernières séries
    if st.session_state.logs:
        st.subheader("Dernières séries enregistrées")
        st.table(pd.DataFrame(st.session_state.logs).tail(5))

# --- ONGLET 3 : GUIDE ---
with tab3:
    st.header("Guide Muscles")
    c1, c2, c3 = st.columns(3)
    if c1.button("Pectoraux"): st.session_state.selection_muscle = "Pectoraux"
    if c2.button("Dos"): st.session_state.selection_muscle = "Dos"
    if c3.button("Jambes"): st.session_state.selection_muscle = "Jambes"
    
    if st.session_state.selection_muscle == "Pectoraux":
        st.info("Consulte la liste des 15 exercices dans l'onglet Séance pour tes pectoraux.")
        st.video("https://www.youtube.com/watch?v=gRVjAtPip0Y")

# --- ONGLET 4 : VISION ---
with tab4:
    st.header("Vision IA")
    v = st.file_uploader("Upload vidéo", type=["mp4", "mov"])
    if v: st.video(v)

# --- ONGLET 5 : CALENDRIER ---
with tab5:
    st.header("📅 Calendrier")
    d = st.date_input("Sélectionne une date", date.today())
    n = st.text_area("Note", value=st.session_state.notes_calendrier.get(str(d), ""))
    if st.button("Sauvegarder Note"):
        st.session_state.notes_calendrier[str(d)] = n
        st.success("Note ok !")
