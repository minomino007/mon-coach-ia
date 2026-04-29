import streamlit as st
import pandas as pd
from datetime import date

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Gym AI Agent PRO", layout="centered", page_icon="🤖")

# 2. INITIALISATION DE LA MÉMOIRE (SESSION STATE)
# Cette section empêche l'app de "perdre" tes données quand tu changes d'onglet
if 'logs' not in st.session_state: 
    st.session_state.logs = []
if 'notes_calendrier' not in st.session_state: 
    st.session_state.notes_calendrier = {}
if 'selection_muscle' not in st.session_state: 
    st.session_state.selection_muscle = "Pectoraux"
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "nom": "Athlète", "age": 25, "grandeur": "5'10",
        "objectif": "Prise de masse", "niveau": "Intermédiaire",
        "poids": 205, "blessures": "Aucune"
    }

# 3. BASE DE DONNÉES DES 15 EXERCICES PECTORAUX
chest_options = [
    "Développé couché", "Développé incliné", "Développé décliné", 
    "Développé haltères", "Écarté couché", "Écarté incliné", 
    "Pec deck (machine)", "Cross-over à la poulie", "Pompes", 
    "Pompes inclinées", "Pompes déclinées", "Dips (buste penché)", 
    "Pullover haltère", "Pullover à la poulie", "Machine chest press"
]

st.title("🤖 Mon Gym AI Agent")

# 4. CRÉATION DES 5 ONGLETS
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Profil", "🏋️ Séance", "👤 Guide", "🎥 Vision", "📅 Calendrier"])

# --- ONGLET 1 : PROFIL (COMPLET) ---
with tab1:
    st.header("👤 Ton Profil Sportif")
    prof = st.session_state.user_profile
    
    # Affichage des stats rapides
    c_poids, c_age, c_lvl = st.columns(3)
    c_poids.metric("Poids", f"{prof['poids']} lbs")
    c_age.metric("Âge", f"{prof['age']} ans")
    c_lvl.metric("Niveau", prof['niveau'])

    st.subheader(f"Bienvenue, {prof['nom']}")
    col_i1, col_i2 = st.columns(2)
    col_i1.write(f"📏 **Grandeur :** {prof['grandeur']}")
    col_i1.write(f"🎯 **Objectif :** {prof['objectif']}")
    col_i2.write(f"🩹 **Blessures :** {prof['blessures']}")

    # Formulaire de modification caché dans un menu
    with st.expander("📝 Modifier mes informations"):
        with st.form("edit_profile_final"):
            new_nom = st.text_input("Nom", value=prof["nom"])
            f_c1, f_c2 = st.columns(2)
            new_age = f_c1.number_input("Âge", value=prof["age"])
            new_grandeur = f_c2.text_input("Grandeur", value=prof["grandeur"])
            new_poids = f_c1.number_input("Poids (lbs)", value=prof["poids"])
            new_obj = f_c2.selectbox("Objectif", ["Prise de masse", "Perte de gras", "Force", "Endurance"])
            new_blessures = st.text_area("Blessures", value=prof["blessures"])
            if st.form_submit_button("Sauvegarder"):
                st.session_state.user_profile.update({
                    "nom": new_nom, "age": new_age, "grandeur": new_grandeur,
                    "poids": new_poids, "objectif": new_obj, "blessures": new_blessures
                })
                st.success("Profil mis à jour !")
                st.rerun()

    if st.session_state.logs:
        st.divider()
        st.subheader("📈 Évolution")
        df_evol = pd.DataFrame(st.session_state.logs)
        st.line_chart(df_evol.set_index("Date")["Poids"])

# --- ONGLET 2 : SÉANCE (ZONE + EXERCICE + REPS + POIDS) ---
with tab2:
    st.header("🏋️ Nouvelle Série")
    with st.form("log_session_final"):
        zone_musc = st.selectbox("Zone", ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos"])
        if zone_musc == "Pectoraux":
            ex_musc = st.selectbox("Exercice", chest_options)
        else:
            ex_musc = st.text_input("Nom de l'exercice")
        
        s_col1, s_col2 = st.columns(2)
        w_val = s_col1.number_input("Poids (lbs)", value=135)
        r_val = s_col2.number_input("Répétitions", value=8)
        
        if st.form_submit_button("Enregistrer la série"):
            st.session_state.logs.append({
                "Date": str(date.today()), "Zone": zone_musc, 
                "Exercice": ex_musc, "Poids": w_val, "Reps": r_val
            })
            st.success("C'est noté !")

    if st.session_state.logs:
        st.subheader("Historique récent")
        st.table(pd.DataFrame(st.session_state.logs).tail(5))

# --- ONGLET 3 : GUIDE ---
with tab3:
    st.header("👤 Guide Technique")
    if st.button("Voir Démo Pectoraux"):
        st.video("https://www.youtube.com/watch?v=gRVjAtPip0Y")

# --- ONGLET 4 : VISION IA ---
with tab4:
    st.header("🎥 Analyse Vidéo")
    up_v = st.file_uploader("Upload", type=["mp4", "mov"])
    if up_v: st.video(up_v)

# --- ONGLET 5 : CALENDRIER ---
with tab5:
    st.header("📅 Calendrier & Notes")
    d_input = st.date_input("Date", date.today())
    note_txt = st.text_area("Notes", value=st.session_state.notes_calendrier.get(str(d_input), ""))
    if st.button("Sauvegarder Note"):
        st.session_state.notes_calendrier[str(d_input)] = note_txt
        st.success("Note enregistrée !")
