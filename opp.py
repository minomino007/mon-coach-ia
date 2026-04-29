import streamlit as st
import pandas as pd
from datetime import date
import openai
import json
import calendar

# ==========================================
# 1. CONFIGURATION DE LA PAGE & CLÉ API
# ==========================================
st.set_page_config(
    page_title="Gym AI Agent PRO",
    layout="centered",
    page_icon="🏋️",
    initial_sidebar_state="collapsed"
)

# Utilisation de la clé directe pour éviter les erreurs de connexion
api_key_val = "sk-proj-7_R7-BvF7H_OaE5G-iNqXm8G-1N4"
client = openai.OpenAI(api_key=api_key_val)

# ==========================================
# 2. SYSTÈME DE TRADUCTION INTÉGRAL (TOUT EST TRADUIT)
# ==========================================
languages = {
    "Français": {
        "tabs": ["📊 Profil", "🏋️ Séance du jour", "👤 Guide", "🎥 Vision", "📅 Calendrier"],
        "prof_header": "👤 Ton Profil Sportif",
        "edit_prof": "Modifier le profil",
        "save": "Sauvegarder",
        "workout_header": "🏋️ Enregistrer une séance",
        "add_set": "➕ Ajouter cette série",
        "validate": "✅ Enregistrer l'entraînement complet",
        "clear": "❌ Tout effacer",
        "lang_label": "Choisir la langue",
        "weight": "Poids (lbs)",
        "reps": "Répétitions",
        "date_label": "Date",
        "zone_label": "Zone musculaire",
        "ex_label": "Exercice spécifique",
        "name_field": "Nom",
        "obj_field": "Objectif",
        "inj_field": "Blessures / Notes",
        "age_field": "Âge",
        "height_field": "Grandeur",
        "goals": ["Prise de masse", "Perte de gras", "Force", "Endurance"],
        "voice_instruction": "🎙️ Clique sur le bouton micro, parle, et les champs se remplissent tout seuls !",
        "mic_btn": "🎙️ Parler",
        "mic_listening": "🔴 Écoute en cours...",
        "mic_waiting": "En attente...",
        "mic_success": "✅ Entendu : ",
        "manual_input_label": "**Ou écris ta séance directement ici :**",
        "analyze_btn": "🤖 Analyser",
        "step1": "📌 Étape 1 — Choisir l'exercice",
        "step2": "📋 Étape 2 — Ajouter tes séries",
        "set_label": "Série",
        "summary_header": "📊 Ta séance complète",
        "history_header": "📅 Historique",
        "history_view": "Consulter une date",
        "note_day": "Note du jour",
        "no_data": "Rien d'enregistré pour ce jour.",
        "zones": ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos"],
        "lang_code": "fr-FR",
        "cal_title": "📅 Calendrier d'Entraînement",
        "detail_title": "🔎 Détail de la séance"
    },
    "English": {
        "tabs": ["📊 Profile", "🏋️ Today's Workout", "👤 Guide", "🎥 Vision", "📅 Calendar"],
        "prof_header": "👤 Your Fitness Profile",
        "edit_prof": "Edit Profile",
        "save": "Save",
        "workout_header": "🏋️ Log a Workout",
        "add_set": "➕ Add This Set",
        "validate": "✅ Save Full Workout",
        "clear": "❌ Clear All",
        "lang_label": "Choose Language",
        "weight": "Weight (lbs)",
        "reps": "Reps",
        "date_label": "Date",
        "zone_label": "Muscle Zone",
        "ex_label": "Specific Exercise",
        "name_field": "Name",
        "obj_field": "Goal",
        "inj_field": "Injuries / Notes",
        "age_field": "Age",
        "height_field": "Height",
        "goals": ["Muscle Gain", "Fat Loss", "Strength", "Endurance"],
        "voice_instruction": "🎙️ Click the mic button, speak, and fields fill automatically!",
        "mic_btn": "🎙️ Speak",
        "mic_listening": "🔴 Listening...",
        "mic_waiting": "Waiting...",
        "mic_success": "✅ Heard: ",
        "manual_input_label": "**Or type your workout here:**",
        "analyze_btn": "🤖 Analyze",
        "step1": "📌 Step 1 — Choose Exercise",
        "step2": "📋 Step 2 — Add Your Sets",
        "set_label": "Set",
        "summary_header": "📊 Full Session Summary",
        "history_header": "📅 History",
        "history_view": "View a date",
        "note_day": "Daily Note",
        "no_data": "Nothing recorded for this day.",
        "zones": ["Chest", "Back", "Legs", "Shoulders", "Abs"],
        "lang_code": "en-US",
        "cal_title": "📅 Training Calendar",
        "detail_title": "🔎 Workout Details"
    }
}

# ==========================================
# 3. INITIALISATION MÉMOIRE (SESSION STATE)
# ==========================================
if 'lang' not in st.session_state: st.session_state.lang = "Français"
L = languages[st.session_state.lang]

if 'logs' not in st.session_state: st.session_state.logs = []
if 'notes_calendrier' not in st.session_state: st.session_state.notes_calendrier = {}
if 'temp_workout' not in st.session_state: st.session_state.temp_workout = []
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "nom": "Athlète", "age": 25, "grandeur": "5'10",
        "objectif": L["goals"][0], "poids": 205, "blessures": "Aucune"
    }

# Initialisation des états pour l'analyse vocale
if 'serie_zone' not in st.session_state: st.session_state.serie_zone = L["zones"][0]
if 'serie_exercice' not in st.session_state: st.session_state.serie_exercice = ""
if 'voice_poids' not in st.session_state: st.session_state.voice_poids = 135
if 'voice_reps' not in st.session_state: st.session_state.voice_reps = 8
if 'texte_vocal' not in st.session_state: st.session_state.texte_vocal = ""

# Liste d'exercices référence
chest_options = [
    "Développé couché", "Développé incliné", "Développé décliné",
    "Développé haltères", "Écarté couché", "Écarté incliné",
    "Pec deck (machine)", "Cross-over à la poulie", "Pompes",
    "Machine chest press"
]

# ==========================================
# 4. FONCTION ANALYSE TEXTE VOCAL
# ==========================================
def analyser_texte_vocal(texte):
    prompt = f"""Extraire les infos de musculation du texte suivant : "{texte}". 
    Répondre UNIQUEMENT en JSON valide avec ces clés : zone, exercice, poids (nombre entier), reps (nombre entier).
    Zones possibles : {L['zones']}.
    Si l'exercice est pour les pectoraux, utilise un nom de cette liste : {chest_options}"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    contenu = response.choices[0].message.content
    return json.loads(contenu.strip().replace("```json", "").replace("```", ""))

# ==========================================
# 5. INTERFACE UTILISATEUR
# ==========================================
st.title("🤖 Mon Gym AI Agent")

tab1, tab2, tab3, tab4, tab5 = st.tabs(L["tabs"])

# --- ONGLET 1 : PROFIL + CALENDRIER INTERACTIF ---
with tab1:
    st.header(L["prof_header"])
    prof = st.session_state.user_profile
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric(L["weight"], f"{prof['poids']} lbs")
    col_m2.metric(L["obj_field"], prof['objectif'])
    col_m3.metric(L["age_field"], f"{prof['age']}")

    st.write(f"**{L['name_field']} :** {prof['nom']} | **{L['height_field']} :** {prof['grandeur']}")
    st.warning(f"🩹 **{L['inj_field']} :** {prof['blessures']}")

    st.divider()
    st.subheader(L["cal_title"])

    # Logique du calendrier
    today = date.today()
    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdatescalendar(today.year, today.month)
    
    # Affichage de la grille
    for week in month_days:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                st.write(f"**{day.day}**")
                df_logs = pd.DataFrame(st.session_state.logs)
                if not df_logs.empty:
                    day_str = str(day)
                    work_day = df_logs[df_logs['Date'] == day_str]
                    if not work_day.empty:
                        zones = work_day['Zone'].unique()
                        for z in zones:
                            if st.button(z, key=f"cal_{day}_{z}", use_container_width=True):
                                st.session_state.selected_date_detail = day_str

    # Affichage du détail au clic
    if 'selected_date_detail' in st.session_state:
        st.info(f"{L['detail_title']} : {st.session_state.selected_date_detail}")
        det_df = pd.DataFrame(st.session_state.logs)
        st.table(det_df[det_df['Date'] == st.session_state.selected_date_detail][["Exercice", "Poids", "Reps"]])

    with st.expander(L["edit_prof"]):
        new_lang = st.selectbox(L["lang_label"], ["Français", "English"], index=0 if st.session_state.lang == "Français" else 1)
        if new_lang != st.session_state.lang:
            st.session_state.lang = new_lang
