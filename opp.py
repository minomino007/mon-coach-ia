import streamlit as st
import pandas as pd
from datetime import date

# Configuration
st.set_page_config(page_title="Gym AI Agent PRO", layout="centered")

st.title("🤖 Mon Gym AI Agent")

# --- MÉMOIRE DE L'APP ---
if 'notes_calendrier' not in st.session_state:
    st.session_state.notes_calendrier = {}

# --- SYSTÈME D'ONGLETS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Profil", "🏋️ Séance", "👤 Guide", "🎥 Vision", "📅 Calendrier"])

# On saute directement à l'onglet Calendrier pour la mise à jour
with tab5:
    st.header("📅 Agenda de l'Athlète")
    st.write("Sélectionne une date dans le calendrier pour ajouter ou lire une note.")

    # 1. LE CALENDRIER VISUEL (Style celui de ta photo)
    # On crée une colonne pour centrer le calendrier
    col_cal, col_note = st.columns([1, 1])
    
    with col_cal:
        date_choisie = st.date_input(
            "Clique sur une date :",
            date.today(),
            help="Sélectionne le jour que tu souhaites noter"
        )
    
    date_str = str(date_choisie)

    # 2. LA ZONE DE NOTE
    with col_note:
        st.subheader(f"Note du {date_choisie.strftime('%d/%m/%Y')}")
        
        # On récupère la note existante s'il y en a une
        note_actuelle = st.session_state.notes_calendrier.get(date_str, "")
        
        nouvelle_note = st.text_area(
            "Ecris tes détails (poids, exercices, ressenti...)", 
            value=note_actuelle,
            height=150,
            placeholder="Ex: Aujourd'hui séance jambes, genou stable."
        )
        
        if st.button("Enregistrer la note"):
            st.session_state.notes_calendrier[date_str] = nouvelle_note
            st.success("Note sauvegardée !")

    # 3. RÉCAPITULATIF RAPIDE
    st.divider()
    if st.session_state.notes_calendrier:
        with st.expander("📖 Voir toutes mes notes passées"):
            # On trie pour avoir les plus récentes en haut
            for d_key in sorted(st.session_state.notes_calendrier.keys(), reverse=True):
                if st.session_state.notes_calendrier[d_key].strip():
                    st.markdown(f"**Le {d_key} :**")
                    st.info(st.session_state.notes_calendrier[d_key])
    else:
        st.write("Aucune note pour le moment.")

# (Le reste du code pour les autres onglets reste identique à ton app précédente)
