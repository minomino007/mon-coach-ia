import streamlit as st
import pandas as pd
from datetime import date

# Configuration
st.set_page_config(page_title="Gym AI Agent PRO", layout="centered")

# --- INITIALISATION DE LA MÉMOIRE ---
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'selection_muscle' not in st.session_state:
    st.session_state.selection_muscle = "Pectoraux" # Par défaut
if 'notes_calendrier' not in st.session_state:
    st.session_state.notes_calendrier = {}

# --- BASE DE DONNÉES EXERCICES ENRICHIE (Vidéos + Images) ---
# J'ai ajouté des liens YouTube éducatifs pour chaque muscle
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
        "image": "https://Post.healthline.com/wp-content/uploads/2020/01/4211-Back-Squat-732x549-Thumbnail.jpg"
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

# --- ONGLET 3 : GUIDE MUSCULAIRE (Version Image & Vidéo) ---
with tab3:
    st.header("Guide des Mouvements")
    st.write("Sélectionnez un muscle pour voir la technique parfaite.")
    
    # Boutons de sélection
    m_cols = st.columns(5)
    muscles = list(exercices_info.keys())
    for i, m in enumerate(muscles):
        if m_cols[i].button(m):
            st.session_state.selection_muscle = m

    # Affichage du contenu
    target = st.session_state.selection_muscle
    info = exercices_info[target]

    st.divider()
    st.subheader(f"🎯 Exercice : {info['ex']}")
    
    col_text, col_img = st.columns([1, 1])
    
    with col_text:
        st.write(f"**Instructions :** {info['desc']}")
        st.info("💡 Conseil de l'IA : Respirez bien pendant l'effort.")
    
    with col_img:
        # Affiche une image d'exemple
        st.image(info['image'], use_container_width=True, caption=info['ex'])

    # Intégration de la vidéo YouTube
    st.write("---")
    st.write("📺 **Démonstration Vidéo :**")
    st.video(info['video'])

# --- ONGLET 1, 2, 4, 5 (Codes précédents maintenus pour que tout fonctionne) ---
with tab1:
    st.header("Profil")
    c1, c2 = st.columns(2); c1.metric("Poids", "205 lbs"); c2.metric("Bench", "205 lbs")

with tab2:
    st.header("Noter Séance")
    with st.form("workout"):
        ex = st.selectbox("Exercice", muscles)
        p = st.number_input("Poids", 135)
        if st.form_submit_button("Sauvegarder"):
            st.session_state.logs.append({"Date": str(date.today()), "1RM Est.": p*1.1})
            st.success("Enregistré !")

with tab4:
    st.header("Vision IA")
    v = st.file_uploader("Vidéo de ton squat", type=["mp4", "mov"])
    if v: st.video(v)

with tab5:
    st.header("Calendrier")
    d_choisie = st.date_input("Date :", date.today())
    note = st.text_area("Note", value=st
