import streamlit as st
import pandas as pd
from datetime import date

# 1. CONFIGURATION
st.set_page_config(page_title="Gym AI Agent PRO", layout="centered", page_icon="🏋️")

# 2. INITIALISATION MÉMOIRE
if 'logs' not in st.session_state: st.session_state.logs = []
if 'notes_calendrier' not in st.session_state: st.session_state.notes_calendrier = {}
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "nom": "Athlète", "age": 25, "grandeur": "5'10",
        "objectif": "Prise de masse", "niveau": "Intermédiaire",
        "poids": 205, "blessures": "Aucune"
    }

# Panier temporaire pour ajouter plusieurs séries avant de sauvegarder la séance
if 'temp_workout' not in st.session_state:
    st.session_state.temp_workout = []

# 3. OPTIONS
chest_options = [
    "Développé couché", "Développé incliné", "Développé décliné", 
    "Développé haltères", "Écarté couché", "Écarté incliné", 
    "Pec deck (machine)", "Cross-over à la poulie", "Pompes", 
    "Pompes inclinées", "Pompes déclinées", "Dips (buste penché)", 
    "Pullover haltère", "Pullover à la poulie", "Machine chest press"
]

st.title("🤖 Mon Gym AI Agent")

# 4. ONGLETS
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Profil", "🏋️ Séance", "👤 Guide", "🎥 Vision", "📅 Calendrier"])

# --- ONGLET 1 : PROFIL ---
with tab1:
    st.header("👤 Ton Profil")
    prof = st.session_state.user_profile
    c1, c2, c3 = st.columns(3)
    c1.metric("Poids", f"{prof['poids']} lbs")
    c2.metric("Objectif", prof['objectif'])
    c3.metric("Niveau", prof['niveau'])
    
    with st.expander("📝 Modifier le profil"):
        with st.form("edit_prof"):
            n = st.text_input("Nom", value=prof["nom"])
            p = st.number_input("Poids (lbs)", value=prof["poids"])
            b = st.text_area("Blessures", value=prof["blessures"])
            if st.form_submit_button("Sauvegarder"):
                st.session_state.user_profile.update({"nom": n, "poids": p, "blessures": b})
                st.rerun()

    if st.session_state.logs:
        st.subheader("📈 Progression")
        df_evol = pd.DataFrame(st.session_state.logs)
        st.line_chart(df_evol.set_index("Date")["Poids"])

# --- ONGLET 2 : SÉANCE (MULTI-SÉRIES ET DATE) ---
with tab2:
    st.header("🏋️ Enregistrer un entraînement")
    
    # 1. Choisir la date de la séance
    date_seance = st.date_input("Date de la séance", date.today())
    
    st.divider()
    st.subheader("Ajouter une série")
    
    # Formulaire pour ajouter UNE série au panier
    with st.form("add_set_form", clear_on_submit=True):
        zone = st.selectbox("Zone", ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos"])
        ex = st.selectbox("Exercice", chest_options) if zone == "Pectoraux" else st.text_input("Exercice")
        
        col_w, col_r = st.columns(2)
        w = col_w.number_input("Poids (lbs)", value=135, step=5)
        r = col_r.number_input("Reps", value=8, step=1)
        
        if st.form_submit_button("➕ Ajouter la série"):
            st.session_state.temp_workout.append({
                "Date": str(date_seance),
                "Zone": zone,
                "Exercice": ex,
                "Poids": w,
                "Reps": r
            })

    # 2. Affichage du panier actuel
    if st.session_state.temp_workout:
        st.write("### 📝 Séries à enregistrer :")
        df_temp = pd.DataFrame(st.session_state.temp_workout)
        st.dataframe(df_temp, use_container_width=True)
        
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.button("✅ Valider toute la séance", type="primary"):
            st.session_state.logs.extend(st.session_state.temp_workout)
            st.session_state.temp_workout = [] # Vider le panier
            st.success("Séance complète enregistrée dans l'historique !")
            st.balloons()
            
        if col_btn2.button("❌ Tout effacer"):
            st.session_state.temp_workout = []
            st.rerun()

# --- ONGLET 3 : GUIDE ---
with tab3:
    st.header("👤 Guide Technique")
    if st.button("Démo Pectoraux"):
        st.video("https://www.youtube.com/watch?v=gRVjAtPip0Y")

# --- ONGLET 4 : VISION ---
with tab4:
    st.header("🎥 Analyse Vidéo")
    up = st.file_uploader("Upload", type=["mp4", "mov"])
    if up: st.video(up)

# --- ONGLET 5 : CALENDRIER ---
with tab5:
    st.header("📅 Calendrier & Notes")
    d_cal = st.date_input("Date", date.today(), key="cal_date")
    n_cal = st.text_area("Note", value=st.session_state.notes_calendrier.get(str(d_cal), ""))
    if st.button("Enregistrer Note"):
        st.session_state.notes_calendrier[str(d_cal)] = n_cal
        st.success("Note enregistrée !")
