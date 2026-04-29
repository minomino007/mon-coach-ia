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

# Sécurité : Vérification de la clé API pour éviter l'erreur 401
try:
    api_key_val = st.secrets["OPENAI_API_KEY"]
    client = openai.OpenAI(api_key=api_key_val, base_url="https://openrouter.ai/api/v1")
except Exception:
    st.error("⚠️ Erreur de configuration : Clé API absente des Secrets.")

# ==========================================
# 2. SYSTÈME DE TRADUCTION COMPLET
# ==========================================
languages = {
    "Français": {
        "tabs": ["📊 Profil", "🏋️ Séance", "🤖 Coach AI", "👤 Guide", "🎥 Vision", "📅 Histo"],
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
        "sex_field": "Sexe",
        "sex_options": ["Homme", "Femme", "Autre"],
        "obj_field": "Objectif",
        "inj_field": "Blessures / Notes",
        "age_field": "Âge",
        "height_field": "Grandeur",
        "goals": ["Prise de masse", "Perte de gras", "Force", "Endurance"],
        "cal_title": "📅 Calendrier d'Activités",
        "detail_title": "🔎 Détail de la séance",
        "coach_header": "🤖 Ton Coach Personnel AI",
        "coach_placeholder": "Pose une question ou raconte ta séance...",
        "voice_instruction": "🎙️ Clique sur le bouton micro pour remplir les champs automatiquement."
    },
    "English": {
        "tabs": ["📊 Profile", "🏋️ Workout", "🤖 AI Coach", "👤 Guide", "🎥 Vision", "📅 History"],
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
        "sex_field": "Sex",
        "sex_options": ["Male", "Female", "Other"],
        "obj_field": "Goal",
        "inj_field": "Injuries / Notes",
        "age_field": "Age",
        "height_field": "Height",
        "goals": ["Muscle Gain", "Fat Loss", "Strength", "Endurance"],
        "cal_title": "📅 Activity Calendar",
        "detail_title": "🔎 Workout Details",
        "coach_header": "🤖 Your AI Coach",
        "coach_placeholder": "Ask a question...",
        "voice_instruction": "🎙️ Click the mic button to fill fields automatically."
    }
}

# ==========================================
# 3. INITIALISATION MÉMOIRE
# ==========================================
if 'lang' not in st.session_state: st.session_state.lang = "Français"
L = languages[st.session_state.lang]

if 'logs' not in st.session_state: st.session_state.logs = []
if 'temp_workout' not in st.session_state: st.session_state.temp_workout = []
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "nom": "Athlète", "sexe": "Homme", "age": 25, "grandeur": "5'10",
        "objectif": "Prise de masse", "poids": 205, "blessures": "Aucune"
    }

# Variables pour le remplissage auto
if 'v_zone' not in st.session_state: st.session_state.v_zone = "Pectoraux"
if 'v_exo' not in st.session_state: st.session_state.v_exo = ""
if 'v_poids' not in st.session_state: st.session_state.v_poids = 135
if 'v_reps' not in st.session_state: st.session_state.v_reps = 8

zones_disponibles = ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos", "Bras"]
chest_options = ["Développé couché", "Développé incliné", "Pec deck (machine)", "Cross-over", "Pompes", "Dips", "Pullover haltère"]

# ==========================================
# 4. FONCTIONS INTELLIGENTES
# ==========================================
def ia_analyse(texte):
    try:
        prompt = f"JSON (zone, exercice, poids, reps) pour : '{texte}'. Liste exo : {chest_options}"
        res = client.chat.completions.create(model="openai/gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
        return json.loads(res.choices[0].message.content.strip().replace("```json", "").replace("```", ""))
    except: return {}

def ia_coach(msg):
    prof = st.session_state.user_profile
    system_p = f"Tu es un coach expert. Athlète: {prof['nom']}, Objectif: {prof['objectif']}, Blessures: {prof['blessures']}."
    msgs = [{"role": "system", "content": system_p}]
    msgs.extend(st.session_state.chat_history[-4:])
    msgs.append({"role": "user", "content": msg})
    try:
        res = client.chat.completions.create(model="openai/gpt-3.5-turbo", messages=msgs)
        return res.choices[0].message.content
    except: return "Désolé, problème de connexion avec le coach."

# ==========================================
# 5. INTERFACE UTILISATEUR
# ==========================================
st.title("🤖 Mon Gym AI Agent")
tabs = st.tabs(L["tabs"])

# --- TAB 1 : PROFIL & CALENDRIER ---
with tabs[0]:
    prof = st.session_state.user_profile
    col1, col2, col3 = st.columns(3)
    col1.metric(L["weight"], f"{prof['poids']} lbs")
    col2.metric(L["obj_field"], prof['objectif'])
    col3.metric(L["age_field"], f"{prof['age']}")

    with st.expander(L["edit_prof"]):
        with st.form("edit_profile"):
            n = st.text_input(L["name_field"], prof["nom"])
            s = st.selectbox(L["sex_field"], L["sex_options"], index=L["sex_options"].index(prof["sexe"]))
            a = st.number_input(L["age_field"], value=prof["age"])
            if st.form_submit_button(L["save"]):
                st.session_state.user_profile.update({"nom": n, "sexe": s, "age": a})
                st.rerun()

    st.subheader(L["cal_title"])
    today = date.today()
    cal = calendar.Calendar(firstweekday=6)
    df_logs = pd.DataFrame(st.session_state.logs)
    
    for week in cal.monthdatescalendar(today.year, today.month):
        cols = st.columns(7)
        for i, d in enumerate(week):
            with cols[i]:
                st.write(f"{d.day}")
                if not df_logs.empty:
                    day_data = df_logs[df_logs['Date'] == str(d)]
                    for z in day_data['Zone'].unique():
                        if st.button(z, key=f"cal_{d}_{z}", use_container_width=True):
                            st.session_state.sel_d = str(d)

    if 'sel_d' in st.session_state:
        st.table(df_logs[df_logs['Date'] == st.session_state.sel_d][["Exercice", "Poids", "Reps"]])

# --- TAB 2 : SÉANCE ---
with tabs[1]:
    st.header(L["workout_header"])
    st.components.v1.html("""
        <button id="mic" style="background:#ff4b4b;color:white;border:none;padding:12px;border-radius:8px;width:100%;cursor:pointer;font-weight:bold;">🎙️ Parler</button>
        <script>
        const btn = document.getElementById('mic');
        btn.onclick = () => {
            const rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            rec.lang = 'fr-FR';
            rec.onresult = (e) => {
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: e.results[0][0].transcript}, '*');
            };
            rec.start();
        };
        </script>
    """, height=70)
    
    v_input = st.text_input("Vérification vocale", key="voice_input")
    if st.button("🤖 Analyser"):
        data = ia_analyse(v_input)
        st.session_state.v_zone = data.get("zone", "Pectoraux")
        st.session_state.v_exo = data.get("exercice", "")
        st.session_state.v_poids = int(data.get("poids", 135))
        st.session_state.v_reps = int(data.get("reps", 8))
        st.rerun()

    with st.form("set_form"):
        dt = st.date_input(L["date_label"], date.today())
        sz = st.selectbox(L["zone_label"], zones_disponibles, index=zones_disponibles.index(st.session_state.v_zone) if st.session_state.v_zone in zones_disponibles else 0)
        ex = st.text_input(L["ex_label"], value=st.session_state.v_exo)
        c1, c2 = st.columns(2)
        pw = c1.number_input(L["weight"], value=st.session_state.v_poids)
        rp = c2.number_input(L["reps"], value=st.session_state.v_reps)
        if st.form_submit_button(L["add_set"]):
            st.session_state.temp_workout.append({"Date": str(dt), "Zone": sz, "Exercice": ex, "Poids": pw, "Reps": rp})
            st.rerun()

    if st.session_state.temp_workout:
        st.dataframe(pd.DataFrame(st.session_state.temp_workout))
        if st.button(L["validate"], type="primary"):
            st.session_state.logs.extend(st.session_state.temp_workout)
            st.session_state.temp_workout = []
            st.success("Séance enregistrée !")

# --- TAB 3 : COACH AI ---
with tabs[2]:
    st.header(L["coach_header"])
    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]): st.write(m["content"])
    
    p = st.chat_input(L["coach_placeholder"])
    if p:
        st.session_state.chat_history.append({"role": "user", "content": p})
        with st.chat_message("user"): st.write(p)
        r = ia_coach(p)
        st.session_state.chat_history.append({"role": "assistant", "content": r})
        with st.chat_message("assistant"): st.write(r)

# --- TABS 4, 5, 6 : AUTRES ---
with tabs[3]: st.video("https://www.youtube.com/watch?v=gRVjAtPip0Y")
with tabs[4]: st.file_uploader("Upload Vision")
with tabs[5]: st.dataframe(pd.DataFrame(st.session_state.logs))
