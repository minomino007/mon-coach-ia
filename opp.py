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

# Utilisation de ta clé API via les secrets
try:
    api_key_val = st.secrets["OPENAI_API_KEY"]
    client = openai.OpenAI(api_key=api_key_val, base_url="https://openrouter.ai/api/v1")
except:
    st.error("Clé API manquante dans les secrets.")

# ==========================================
# 2. SYSTÈME DE TRADUCTION
# ==========================================
languages = {
    "Français": {
        "tabs": ["📊 Profil", "🏋️ Séance du jour", "🤖 Coach AI", "👤 Guide", "🎥 Vision", "📅 Calendrier"],
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
        "goals": ["Prise de masse", "Perte de gras", "Force", "Endurance"],
        "voice_instruction": "🎙️ Clique sur le bouton micro, parle, et les champs se remplissent tout seuls !",
        "cal_title": "📅 Calendrier d'Activités",
        "detail_title": "🔎 Détail de la séance",
        "coach_header": "🤖 Ton Coach Personnel AI",
        "coach_placeholder": "Pose une question ou raconte ta séance...",
        "coach_btn": "Envoyer au coach"
    },
    "English": {
        "tabs": ["📊 Profile", "🏋️ Today's Workout", "🤖 AI Coach", "👤 Guide", "🎥 Vision", "📅 Calendar"],
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
        "goals": ["Muscle Gain", "Fat Loss", "Strength", "Endurance"],
        "voice_instruction": "🎙️ Click the mic button, speak, and fields fill automatically!",
        "cal_title": "📅 Activity Calendar",
        "detail_title": "🔎 Workout Details",
        "coach_header": "🤖 Your AI Personal Coach",
        "coach_placeholder": "Ask a question or tell me about your workout...",
        "coach_btn": "Send to Coach"
    }
}

# ==========================================
# 3. INITIALISATION MÉMOIRE
# ==========================================
if 'lang' not in st.session_state: st.session_state.lang = "Français"
if 'logs' not in st.session_state: st.session_state.logs = []
if 'notes_calendrier' not in st.session_state: st.session_state.notes_calendrier = {}
if 'temp_workout' not in st.session_state: st.session_state.temp_workout = []
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "nom": "Athlète", "age": 25, "grandeur": "5'10",
        "objectif": "Prise de masse", "poids": 205, "blessures": "Aucune"
    }
# Variables pour la séance
if 'serie_zone' not in st.session_state: st.session_state.serie_zone = "Pectoraux"
if 'serie_exercice' not in st.session_state: st.session_state.serie_exercice = ""
if 'voice_poids' not in st.session_state: st.session_state.voice_poids = 135
if 'voice_reps' not in st.session_state: st.session_state.voice_reps = 8
if 'texte_vocal' not in st.session_state: st.session_state.texte_vocal = ""

zones_disponibles = ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos"]
L = languages[st.session_state.lang]

# ==========================================
# 4. FONCTION ANALYSE & CHATBOT
# ==========================================
def analyser_texte_vocal(texte):
    prompt = f"Extrais JSON (zone, exercice, poids, reps) de : '{texte}'."
    response = client.chat.completions.create(
        model="openai/gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.choices[0].message.content.strip().replace("```json", "").replace("```", ""))

def chat_avec_coach(message_user):
    prof = st.session_state.user_profile
    logs = st.session_state.logs[-5:] # Donne les 5 dernières séances au coach pour contexte
    
    system_prompt = f"""Tu es un coach expert en musculation. 
    L'athlète est {prof['nom']}, objectif: {prof['objectif']}, blessures: {prof['blessures']}.
    Voici ses dernières séances : {logs}.
    Réponds de façon motivante, courte et technique. Si l'utilisateur veut enregistrer une séance, explique-lui d'aller dans l'onglet 'Séance'."""
    
    messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.chat_history[-6:]: # Mémoire de conversation
        messages.append(msg)
    messages.append({"role": "user", "content": message_user})
    
    response = client.chat.completions.create(
        model="openai/gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message.content

# ==========================================
# 5. INTERFACE UTILISATEUR
# ==========================================
st.title("🤖 Mon Gym AI Agent")

tab1, tab2, tab_chat, tab3, tab4, tab5 = st.tabs(L["tabs"])

# --- ONGLET 1 : PROFIL ---
with tab1:
    st.header(L["prof_header"])
    prof = st.session_state.user_profile
    c1, c2, c3 = st.columns(3)
    c1.metric(L["weight"], f"{prof['poids']} lbs")
    c2.metric(L["obj_field"], prof['objectif'])
    c3.metric(L["age_field"], f"{prof['age']}")

    st.divider()
    with st.expander(L["edit_prof"]):
        new_lang = st.selectbox(L["lang_label"], ["Français", "English"], index=0 if st.session_state.lang == "Français" else 1)
        if new_lang != st.session_state.lang:
            st.session_state.lang = new_lang
            st.rerun()
        with st.form("edit_form"):
            n = st.text_input(L["name_field"], value=prof["nom"])
            a = st.number_input(L["age_field"], value=prof["age"])
            p = st.number_input(L["weight"], value=prof["poids"])
            obj = st.selectbox(L["obj_field"], L["goals"], index=L["goals"].index(prof["objectif"]))
            if st.form_submit_button(L["save"]):
                st.session_state.user_profile.update({"nom": n, "age": a, "poids": p, "objectif": obj})
                st.rerun()

    # CALENDRIER VISUEL
    st.subheader(L["cal_title"])
    today = date.today()
    c_obj = calendar.Calendar(firstweekday=6)
    for week in c_obj.monthdatescalendar(today.year, today.month):
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                st.write(f"**{day.day}**")
                df_logs = pd.DataFrame(st.session_state.logs)
                if not df_logs.empty:
                    day_logs = df_logs[df_logs['Date'] == str(day)]
                    for z in day_logs['Zone'].unique():
                        if st.button(z, key=f"p_{day}_{z}", use_container_width=True):
                            st.session_state.sel_date = str(day)
    if 'sel_date' in st.session_state:
        st.table(df_logs[df_logs['Date'] == st.session_state.sel_date][["Exercice", "Poids", "Reps"]])

# --- ONGLET 2 : SÉANCE DU JOUR ---
with tab2:
    st.header(L["workout_header"])
    st.components.v1.html("""
        <button id="mic" style="background:#ff4b4b;color:white;border:none;padding:12px;border-radius:8px;width:100%;cursor:pointer;">🎙️ Parler pour remplir les champs</button>
        <script>
        const btn = document.getElementById('mic');
        btn.onclick = () => {
            const rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            rec.onresult = (e) => {
                const t = e.results[0][0].transcript;
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: t}, '*');
            };
            rec.start();
        };
        </script>
    """, height=70)
    
    t_in = st.text_input("Vérification vocale", key="v_input")
    if st.button("🤖 Remplir via IA"):
        data = analyser_texte_vocal(t_in)
        st.session_state.serie_zone = data.get("zone", "Pectoraux")
        st.session_state.serie_exercice = data.get("exercice", "")
        st.session_state.voice_poids = int(data.get("poids", 135))
        st.session_state.voice_reps = int(data.get("reps", 8))
        st.rerun()

    with st.form("work_form"):
        dt = st.date_input(L["date_label"], date.today())
        sz = st.selectbox(L["zone_label"], zones_disponibles, index=zones_disponibles.index(st.session_state.serie_zone))
        ex = st.text_input(L["ex_label"], value=st.session_state.serie_exercice)
        c_w, c_r = st.columns(2)
        win = c_w.number_input(L["weight"], value=st.session_state.voice_p
