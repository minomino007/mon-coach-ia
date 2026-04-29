import streamlit as st
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="Gym AI Agent", layout="centered")

# --- STYLE & DESIGN ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff4b4b; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 Mon Gym AI Agent")
st.write("Coach Personnel | Performance | Statistiques")

# --- INITIALISATION DES DONNÉES ---
if 'logs' not in st.session_state:
    st.session_state.logs = []

# --- DASHBOARD DE L'UTILISATEUR ---
col1, col2, col3 = st.columns(3)
col1.metric("Poids", "205 lbs")
col2.metric("Bench PR", "205 lbs")
col3.metric("Squat PR", "225 lbs")

# --- ENREGISTREMENT D'UNE SÉANCE ---
st.header("🏋️ Enregistrer une séance")
with st.form("workout_form"):
    muscle = st.selectbox("Zone travaillée", ["Chest & Abs", "Dos", "Jambes", "Épaules", "Bras"])
    exer = st.text_input("Exercice (ex: Bench Press)")
    weight = st.number_input("Poids (lbs)", min_value=0, value=135)
    reps = st.number_input("Répétitions", min_value=0, value=8)
    rpe = st.slider("Difficulté (RPE) - 10 est l'échec total", 1, 10, 8)
    
    submitted = st.form_submit_button("Calculer & Enregistrer")
    
    if submitted:
        # LOGIQUE DE L'AGENT IA
        one_rm = weight * (1 + reps / 30)
        next_goal = weight + 5 if rpe <= 8 else weight
        
        new_data = {
            "Date": pd.Timestamp.now().strftime("%Y-%m-%d"),
            "Muscle": muscle,
            "Exercice": exer,
            "Poids": weight,
            "Reps": reps,
            "RPE": rpe,
            "1RM Est.": round(one_rm, 1),
            "Objectif Suivant": next_goal
        }
        st.session_state.logs.append(new_data)
        st.success(f"Objectif séance suivante : {next_goal} lbs ! 🚀")

# --- STATISTIQUES & HISTORIQUE ---
if st.session_state.logs:
    st.header("📈 Tes Statistiques")
    df = pd.DataFrame(st.session_state.logs)
    st.dataframe(df)
    
    # Graphique de progression
    st.line_chart(df.set_index("Date")["1RM Est."])
else:
    st.info("Aucune donnée enregistrée pour le moment. Fais ta première séance !")

st.sidebar.warning("⚠️ Attention au genou gauche lors du Squat ! Contrôle la descente.")
