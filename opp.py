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

# --- BASE DE DONNÉES PECTORAUX (15 EXERCICES) ---
chest_exercises = {
    "Développé couché": {"desc": "Le roi pour la masse. Garde les pieds ancrés et les omoplates serrées.", "vid": "https://www.youtube.com/watch?v=gRVjAtPip0Y"},
    "Développé incliné": {"desc": "Cible le haut des pec. Banc à 30-45 degrés.", "vid": "https://www.youtube.com/watch?v=SrqOu55lrYU"},
    "Développé décliné": {"desc": "Cible le bas des pectoraux. Réduit le stress sur les épaules.", "vid": "https://www.youtube.com/watch?v=LfyQFl7O-LI"},
    "Développé haltères": {"desc": "Meilleure amplitude et travail de stabilisation.", "vid": "https://www.youtube.com/watch?v=VmB1G1K7v94"},
    "Écarté couché": {"desc": "Isolation pour étirer les fibres. Ne descends pas trop bas pour protéger les épaules.", "vid": "https://www.youtube.com/watch?v=eGjt4lk6g34"},
    "Écarté incliné": {"desc": "Étirement ciblé sur la partie haute du torse.", "vid": "https://www.youtube.com/watch?v=8XpPAnR9jB8"},
    "Pec deck (machine)": {"desc": "Tension constante. Idéal pour finir la séance et sentir la contraction.", "vid": "https://www.youtube.com/watch?v=O-S6Yit5Miw"},
    "Cross-over à la poulie": {"desc": "Joue sur la hauteur des poulies pour varier l'angle.", "vid": "https://www.youtube.com/watch?v=taI4XduLpTk"},
    "Pompes": {"desc": "L'exercice de base. Garde le corps bien droit.", "vid": "https://www.youtube.com/watch?v=pSHjTRCQxIw"},
    "Pompes inclinées": {"desc": "Mains sur un banc. Plus facile, cible le bas des pec.", "vid": "https://www.youtube.com/watch?v=Z0bRiVHNn8Q"},
    "Pompes déclinées": {"desc": "Pieds sur un banc. Plus dur, cible le haut des pec.", "vid": "https://www.youtube.com/watch?v=SKPab2z8qhY"},
    "Dips (buste penché)": {"desc": "Penche-toi en avant pour engager les pectoraux plutôt que les triceps.", "vid": "https://www.youtube.com/watch?v=48SfsR2O3Rg"},
    "Pullover haltère": {"desc": "Ouvre la cage thoracique. Garde un léger flex dans les coudes.", "vid": "https://www.youtube.com/watch?v=FK4rkRh7XP4"},
    "Pullover à la poulie":
