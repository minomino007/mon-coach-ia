import streamlit as st
import pandas as pd

# Configuration de l'application
st.set_page_config(page_title="Gym AI Agent PRO", layout="centered")

st.title("🤖 Mon Gym AI Agent")

# --- INITIALISATION DE LA MÉMOIRE ---
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'selection_muscle' not in st.session_state:
    st.session_state.selection_muscle = None

# --- BASE DE DONNÉES EXERCICES ---
exercices_info = {
    "Pectoraux": {"ex": "Développé Couché", "desc": "Cible le torse. Garde les omoplates serrées. Objectif : 225 lbs !"},
    "Dos": {"ex": "Tirage Buste Penché", "desc": "Cible l'épaisseur. Garde le dos droit comme un piquet."},
    "Jambes": {"ex": "Squat", "desc": "Cible les cuisses. ATTENTION : Pour ton genou, contrôle la descente sur 3 secondes."},
    "Épaules": {"ex": "Développé Militaire", "desc": "Cible les deltoïdes. Serre les abdos pour protéger ton dos."},
    "Abdos": {"ex": "Sit-ups", "desc": "Ton favori. Croise les mains sur les épaules, ne tire pas la nuque."}
}

# --- CRÉATION DES ONGLETS (TABS) ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Mon Profil", "🏋️ Séance", "👤 Guide Muscles", "🎥 Analyse IA"])

# --- ONGLET 1 : DASHBOARD & PROFIL ---
with tab1:
    st.header("Tes Statistiques")
    col1, col2, col3 = st.columns(3)
    col1.metric("Poids", "205 lbs")
    col2.metric("Bench PR", "205 lbs")
    col3.metric("Squat PR", "225 lbs")
    
    if st.session_state.logs:
        st.subheader("Progression de ta force")
        df = pd.DataFrame(st.session_state.logs)
        st.line_chart(df.set_index("Date")["1RM Est."])
    else:
        st.info("Fais ta première séance pour voir tes graphiques ici !")

# --- ONGLET 2 : LOG DE SÉANCE ---
with tab2:
    st.header("Noter tes séries")
    with st.form("workout_form"):
        exer = st.selectbox("Exercice", list(exercices_info.keys()))
        poids = st.number_input("Poids soulevé (lbs)", value=135)
        reps = st.number_input("Nombre de Reps", value=8)
        rpe = st.slider("Difficulté (RPE 1-10)", 1, 10, 8)
        
        if st.form_submit_button("Enregistrer la performance"):
            # Calcul IA
            one_rm = poids * (1 + reps / 30)
            next_goal = poids + 5 if rpe <= 7 else poids
            
            st.session_state.logs.append({
                "Date": pd.Timestamp.now().strftime("%Y-%m-%d"),
                "Exercice": exer,
                "Poids": poids,
                "Reps": reps,
                "1RM Est.": round(one_rm, 1)
            })
            st.balloons()
            st.success(f"Bravo ! Objectif prochaine séance : {next_goal} lbs")

# --- ONGLET 3 : GUIDE MUSCULAIRE ---
with tab3:
    st.header("Anatomie & Exercices")
    st.write("Sur quel muscle veux-tu te concentrer ?")
    
    c1, c2, c3 = st.columns(3)
    if c1.button("Pectoraux"): st.session_state.selection_muscle = "Pectoraux"
    if c2.button("Dos"): st.session_state.selection_muscle = "Dos"
    if c3.button("Jambes"): st.session_state.selection_muscle = "Jambes"
    if c1.button("Épaules"): st.session_state.selection_muscle = "Épaules"
    if c2.button("Abdos"): st.session_state.selection_muscle = "Abdos"

    if st.session_state.selection_muscle:
        m = st.session_state.selection_muscle
        st.markdown(f"### 🎯 {m}")
        st.info(f"**Exercice recommandé :** {exercices_info[m]['ex']}")
        st.write(exercices_info[m]['desc'])

# --- ONGLET 4 : ANALYSE VIDÉO ---
with tab4:
    st.header("Analyse de Forme IA")
    st.write("Télécharge ton Squat pour vérifier tes genoux.")
    video_file = st.file_uploader("Prends ou choisis une vidéo", type=["mp4", "mov"])
    if video_file:
        st.video(video_file)
        st.warning("Analyse IA : Assure-toi que tes talons ne décollent pas du sol.")
