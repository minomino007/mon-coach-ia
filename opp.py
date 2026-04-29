import streamlit as st
import pandas as pd
from datetime import date

# Configuration de la page
st.set_page_config(page_title="Gym AI Agent PRO", layout="centered")

# --- INITIALISATION MÉMOIRE ---
if 'logs' not in st.session_state: st.session_state.logs = []
if 'selection_muscle' not in st.session_state: st.session_state.selection_muscle = "Pectoraux"
if 'notes_calendrier' not in st.session_state: st.session_state.notes_calendrier = {}

# --- LA LISTE DES 15 EXERCICES PECTORAUX ---
chest_list = {
    "Développé couché": "https://www.youtube.com/watch?v=gRVjAtPip0Y",
    "Développé incliné": "https://www.youtube.com/watch?v=SrqOu55lrYU",
    "Développé décliné": "https://www.youtube.com/watch?v=LfyQFl7O-LI",
    "Développé haltères": "https://www.youtube.com/watch?v=VmB1G1K7v94",
    "Écarté couché": "https://www.youtube.com/watch?v=eGjt4lk6g34",
    "Écarté incliné": "https://www.youtube.com/watch?v=8XpPAnR9jB8",
    "Pec deck (machine)": "https://www.youtube.com/watch?v=O-S6Yit5Miw",
    "Cross-over à la poulie": "https://www.youtube.com/watch?v=taI4XduLpTk",
    "Pompes": "https://www.youtube.com/watch?v=pSHjTRCQxIw",
    "Pompes inclinées": "https://www.youtube.com/watch?v=Z0bRiVHNn8Q",
    "Pompes déclinées": "https://www.youtube.com/watch?v=SKPab2z8qhY",
    "Dips (buste penché)": "https://www.youtube.com/watch?v=48SfsR2O3Rg",
    "Pullover haltère": "https://www.youtube.com/watch?v=FK4rkRh7XP4",
    "Pullover à la poulie": "https://www.youtube.com/watch?v=vV7InVn7C0c",
    "Machine chest press": "https://www.youtube.com/watch?v=xZ9onwG36Yw"
}

st.title("🤖 Mon Gym AI Agent")

# --- LES ONGLETS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Profil", "🏋️ Séance", "👤 Guide", "🎥 Vision", "📅 Calendrier"])

# --- ONGLET 3 : LE GUIDE (C'est là que l'erreur était) ---
with tab3:
    st.header("Guide des Pectoraux")
    selection = st.selectbox("Choisis ton exercice :", list(chest_list.keys()))
    
    st.info(f"**Exercice :** {selection}")
    st.video(chest_list[selection])

# --- RESTE DE L'APP (Sécurisé) ---
with tab1:
    st.header("Statistiques")
    st.metric("Poids actuel", "205 lbs")
    if st.session_state.logs:
        df = pd.DataFrame(st.session_state.logs)
        st.line_chart(df.set_index("Date")["Poids"])

with tab2:
    st.header("Nouvelle Série")
    with st.form("workout"):
        ex = st.selectbox("Muscle", ["Pectoraux", "Dos", "Jambes"])
        p = st.number_input("Poids (lbs)", 135)
        if st.form_submit_button("Enregistrer"):
            st.session_state.logs.append({"Date": str(date.today()), "Poids": p})
            st.success("Sauvegardé !")

with tab4:
    st.header("Vision IA")
    v = st.file_uploader("Vidéo", type=["mp4", "mov"])
    if v: st.video(v)

with tab5:
    st.header("Calendrier")
    d = st.date_input("Date", date.today())
    memo = st.text_area("Note", value=st.session_state.notes_calendrier.get(str(d), ""))
    if st.button("Enregistrer Note"):
        st.session_state.notes_calendrier[str(d)] = memo
        st.success("Note ok !")
