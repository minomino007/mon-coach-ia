import streamlit as st
import pandas as pd
from datetime import date

# Configuration
st.set_page_config(page_title="Gym AI Agent PRO", layout="centered")

# --- INITIALISATION DE LA MÉMOIRE ---
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'selection_muscle' not in st.session_state:
    st.session_state.selection_muscle = "Pectoraux"
if 'notes_calendrier' not in st.session_state:
    st.session_state.notes_calendrier = {}

# --- BASE DE DONNÉES EXERCICES ---
exercices_info = {
    "Pectoraux": {
        "ex": "Développé Couché (Bench Press)",
        "desc": "Allongé sur le banc, descendez la barre au niveau des pectoraux puis poussez. Gardez les pieds au sol.",
        "video": "https://www.youtube.com/watch?v=gRVjAtPip0Y",
        "image": "https://www.fitness-superstore.co.uk/blog/wp-content/uploads/2021/04/Bench-Press-Form.jpg"
    },
    "Dos": {
        "ex": "Tirage Vertical (Lat Pulldown)",
        "desc": "Tirez la barre vers le haut de votre poitrine en serrant les omoplates. Ne vous balanciez pas.",
        "video": "https://www.youtube.com/watch?v=CAwf7n6Luuc",
        "image": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Lat-Pulldown_600x600.jpg"
    },
    "Jambes": {
        "ex": "Squat à la barre",
        "desc": "Gardez le dos droit, descendez les fesses en arrière. Contrôlez bien pour vos genoux !",
        "video": "https://www.youtube.com/watch?v=gcNh17Ckjgg",
        "image": "https://post.healthline.com/wp-content/uploads/2020/01/4211-Back-Squat-732x549-Thumbnail.jpg"
    },
    "Épaules": {
        "ex": "Développé Militaire",
        "desc": "Poussez les haltères ou la barre au-dessus de la tête sans cambrer le dos.",
        "video": "https://www.youtube.com/watch?v=2yjwHe457lI",
        "image": "https://www.muscleandfitness.com/wp-content/uploads/2018/05/1109-overhead-press.jpg"
    },
    "Abdos": {
        "ex": "La Planche (Plank)",
        "desc": "Maintenez le corps droit comme une planche sur les avant-bras. Ne levez pas trop les fesses.",
        "video": "https://www.youtube.com/watch?v=pSHjTRCQxIw",
        "image": "https://www.verywellfit.com/thmb/9fI9i6lqf_M_m4O0w_Xn6_0m6_I=/1500x1000/filters:no_upscale():max_bytes(150000):strip_icc()/Verywell-14-3120071-Plank01-1497-598cc068396e4949a2636a04297a760c.jpg"
    }
}

st.title("🤖 Mon Gym AI Agent")

# --- ONGLETS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Profil", "🏋️ Séance", "👤 Guide Muscles", "🎥 Vision", "📅 Calendrier"])

with tab1:
    st.header("Profil")
    c1, c2, c3 = st.columns(3)
    c1.metric("Poids", "205 lbs")
    c2.metric("Bench PR", "205 lbs")
    c3.metric("Squat PR", "225 lbs")
    if st.session_state.logs:
        df = pd.DataFrame(st.session_state.logs)
        st.line_chart(df.set_index("Date")["Poids"])

with tab2:
    st.header("Noter ta séance")
    with st.form("workout_form"):
        ex_choice = st.selectbox("Exercice", list(exercices_info.keys()))
        weight_input = st.number_input("Poids (lbs)", value=135)
        reps_input = st.number_input("Répétitions", value=8)
        if st.form_submit_button("Sauvegarder"):
            st.session_state.logs.append({"Date": str(date.today()), "Exercice": ex_choice, "Poids": weight_input})
            st.success("Séance enregistrée !")

with tab3:
    st.header("Guide des Mouvements")
    m_cols = st.columns(5)
    for i, m in enumerate(exercices_info.keys()):
        if m_cols[i].button(m):
            st.session_state.selection_muscle = m
    
    target = st.session_state.selection_muscle
    info = exercices_info[target]
    st.divider()
    st.subheader(f"🎯 {info['ex']}")
    col_t, col_i = st.columns([1, 1])
    with col_t:
        st.write(info['desc'])
    with col_i:
        st.image(info['image'], use_container_width=True)
    st.video(info['video'])

with tab4:
    st.header("Vision IA")
    v_file = st.file_uploader("Upload ta vidéo", type=["mp4", "mov"])
    if v_file:
        st.video(v_file)

with tab5:
    st.header("📅 Calendrier")
    d_input = st.date_input("Sélectionne une date", date.today())
    d_str = str(d_input)
    
    # Récupération sécurisée de la note
    note_val = st.session_state.notes_calendrier.get(d_str, "")
    
    note_txt = st.text_area("Notes pour ce jour", value=note_val)
    
    if st.button("Sauvegarder la note"):
        st.session_state.notes_calendrier[d_str] = note_txt
        st.success("Note enregistrée !")
