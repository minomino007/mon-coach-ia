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

# Récupération sécurisée de la clé API
try:
    api_key_val = st.secrets["OPENAI_API_KEY"]
    client = openai.OpenAI(api_key=api_key_val)
except:
    st.error("Clé API manquante dans les secrets de Streamlit.")

# ==========================================
# 2. SYSTÈME DE TRADUCTION
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
        "voice_instruction": "🎙️ Dis : 'Pectoraux, développé couché, 180 lbs, 10 reps'",
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
        "voice_instruction": "🎙️ Say: 'Chest, bench press, 180 lbs, 10 reps'",
        "cal_title": "📅 Training Calendar",
        "detail_title": "🔎 Workout Details"
    }
}

# ==========================================
# 3. INITIALISATION MÉMOIRE
# ==========================================
if 'lang' not in st.session_state: st.session_state.lang = "Français"
if 'logs' not in st.session_state: st.session_state.logs = []
if 'notes_calendrier' not in st.session_state: st.session_state.notes_calendrier = {}
if 'temp_workout' not in st.session_state: st.session_state.temp_workout = []
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "nom": "Athlète", "age": 25, "grandeur": "5'10",
        "objectif": "Prise de masse", "poids": 205, "blessures": "Aucune"
    }
if 'serie_zone' not in st.session_state: st.session_state.serie_zone = "Pectoraux"
if 'serie_exercice' not in st.session_state: st.session_state.serie_exercice = ""
if 'voice_poids' not in st.session_state: st.session_state.voice_poids = 135
if 'voice_reps' not in st.session_state: st.session_state.voice_reps = 8

zones_disponibles = ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos"]
L = languages[st.session_state.lang]

# ==========================================
# 4. FONCTION ANALYSE IA
# ==========================================
def analyser_texte_vocal(texte):
    prompt = f"Extraire infos muscu JSON (zone, exercice, poids, reps) de : '{texte}'. Zones: {zones_disponibles}"
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(resp.choices[0].message.content)

# ==========================================
# 5. INTERFACE
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(L["tabs"])

# --- PROFIL ---
with tab1:
    st.header(L["prof_header"])
    prof = st.session_state.user_profile
    col1, col2, col3 = st.columns(3)
    col1.metric(L["weight"], f"{prof['poids']} lbs")
    col2.metric(L["obj_field"], prof['objectif'])
    col3.metric(L["age_field"], f"{prof['age']}")

    # Calendrier Visuel
    st.divider()
    st.subheader(L["cal_title"])
    today = date.today()
    c_obj = calendar.Calendar(firstweekday=6)
    for week in c_obj.monthdatescalendar(today.year, today.month):
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                st.write(f"**{day.day}**")
                logs_df = pd.DataFrame(st.session_state.logs)
                if not logs_df.empty:
                    day_logs = logs_df[logs_df['Date'] == str(day)]
                    if not day_logs.empty:
                        for z in day_logs['Zone'].unique():
                            if st.button(z, key=f"p_{day}_{z}", use_container_width=True):
                                st.session_state.view_date = str(day)

    if 'view_date' in st.session_state:
        st.info(f"{L['detail_title']} : {st.session_state.view_date}")
        all_logs = pd.DataFrame(st.session_state.logs)
        st.table(all_logs[all_logs['Date'] == st.session_state.view_date][["Exercice", "Poids", "Reps"]])

    with st.expander(L["edit_prof"]):
        lang = st.selectbox(L["lang_label"], ["Français", "English"], index=0 if st.session_state.lang == "Français" else 1)
        if lang != st.session_state.lang:
            st.session_state.lang = lang
            st.rerun()

# --- SÉANCE DU JOUR ---
with tab2:
    st.header(L["workout_header"])
    st.write(L["voice_instruction"])

    val_vocal = st.components.v1.html("""
        <button id="mic" style="background:#ff4b4b;color:white;border:none;padding:10px;border-radius:5px;width:100%;cursor:pointer;">🎙️ Commencer l'enregistrement</button>
        <div id="out" style="color:#00ff88;margin-top:5px;"></div>
        <script>
        const btn = document.getElementById('mic');
        btn.onclick = () => {
            const rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            rec.onresult = (e) => {
                const t = e.results[0][0].transcript;
                document.getElementById('out').innerText = "✅ " + t;
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: t}, '*');
            };
            rec.start();
        };
        </script>
    """, height=100)

    t_in = st.text_input("Texte analysé", key="v_input")
    if st.button("🤖 Analyser"):
        data = analyser_texte_vocal(t_in)
        st.session_state.serie_zone = data.get("zone", "Pectoraux")
        st.session_state.serie_exercice = data.get("exercice", "")
        st.session_state.voice_poids = int(data.get("poids", 135))
        st.session_state.voice_reps = int(data.get("reps", 8))
        st.rerun()

    st.divider()
    dt = st.date_input(L["date_label"], date.today())
    sz = st.selectbox(L["zone_label"], zones_disponibles, index=zones_disponibles.index(st.session_state.serie_zone))
    se = st.text_input(L["ex_label"], value=st.session_state.serie_exercice)

    with st.form("set_form"):
        c1, c2 = st.columns(2)
        p = c1.number_input(L["weight"], value=st.session_state.voice_poids)
        r = c2.number_input(L["reps"], value=st.session_state.voice_reps)
        if st.form_submit_button(L["add_set"]):
            st.session_state.temp_workout.append({"Date": str(dt), "Zone": sz, "Exercice": se, "Poids": p, "Reps": r})
            st.rerun()

    if st.session_state.temp_workout:
        st.dataframe(pd.DataFrame(st.session_state.temp_workout))
        if st.button(L["validate"], type="primary"):
            st.session_state.logs.extend(st.session_state.temp_workout)
            st.session_state.temp_workout = []
            st.success("Sauvegardé !")

# --- AUTRES ---
with tab3: st.video("https://www.youtube.com/watch?v=gRVjAtPip0Y")
with tab4: st.file_uploader("Upload")
with tab5:
    d_sel = st.date_input("Historique", date.today())
    df = pd.DataFrame(st.session_state.logs)
    if not df.empty: st.table(df[df['Date'] == str(d_sel)])
