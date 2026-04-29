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

try:
    api_key_val = st.secrets["OPENAI_API_KEY"]
    client = openai.OpenAI(api_key=api_key_val, base_url="https://openrouter.ai/api/v1")
except:
    st.error("Clé API manquante dans les secrets.")

# ==========================================
# 2. SYSTÈME DE TRADUCTION COMPLET
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
        "sex_field": "Sexe",
        "sex_options": ["Homme", "Femme", "Autre"],
        "obj_field": "Objectif",
        "inj_field": "Blessures / Notes",
        "age_field": "Âge",
        "height_field": "Grandeur",
        "goals": ["Prise de masse", "Perte de gras", "Force", "Endurance"],
        "voice_instruction": "🎙️ Clique sur le bouton micro pour remplir les champs automatiquement.",
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
        "sex_field": "Sex",
        "sex_options": ["Male", "Female", "Other"],
        "obj_field": "Goal",
        "inj_field": "Injuries / Notes",
        "age_field": "Age",
        "height_field": "Height",
        "goals": ["Muscle Gain", "Fat Loss", "Strength", "Endurance"],
        "voice_instruction": "🎙️ Click the mic button to fill fields automatically.",
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
        "nom": "Athlète", "sexe": "Homme", "age": 25, "grandeur": "5'10",
        "objectif": "Prise de masse", "poids": 205, "blessures": "Aucune"
    }

# Variables temporaires séance
if 'serie_zone' not in st.session_state: st.session_state.serie_zone = "Pectoraux"
if 'serie_exercice' not in st.session_state: st.session_state.serie_exercice = ""
if 'voice_poids' not in st.session_state: st.session_state.voice_poids = 135
if 'voice_reps' not in st.session_state: st.session_state.voice_reps = 8

zones_disponibles = ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos", "Bras"]
L = languages[st.session_state.lang]

# ==========================================
# 4. FONCTIONS IA
# ==========================================
def analyser_texte_vocal(texte):
    prompt = f"Réponds uniquement en JSON (clés: zone, exercice, poids, reps) pour : '{texte}'."
    try:
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.choices[0].message.content.strip().replace("```json", "").replace("```", ""))
    except: return {}

def chat_avec_coach(message_user):
    prof = st.session_state.user_profile
    system_prompt = f"Tu es un coach expert. Athlète: {prof['nom']}, Objectif: {prof['objectif']}, Blessures: {prof['blessures']}."
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(st.session_state.chat_history[-6:])
    messages.append({"role": "user", "content": message_user})
    try:
        response = client.chat.completions.create(model="openai/gpt-3.5-turbo", messages=messages)
        return response.choices[0].message.content
    except: return "Désolé, je rencontre un problème de connexion."

# ==========================================
# 5. INTERFACE
# ==========================================
st.title("🤖 Mon Gym AI Agent")
tab1, tab2, tab_chat, tab3, tab4, tab5 = st.tabs(L["tabs"])

# --- ONGLET 1 : PROFIL & CALENDRIER ---
with tab1:
    st.header(L["prof_header"])
    prof = st.session_state.user_profile
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric(L["weight"], f"{prof['poids']} lbs")
    col_m2.metric(L["obj_field"], prof['objectif'])
    col_m3.metric(L["age_field"], f"{prof['age']}")

    st.write(f"**{L['name_field']} :** {prof['nom']} | **{L['sex_field']} :** {prof['sexe']} | **{L['height_field']} :** {prof['grandeur']}")
    st.divider()

    with st.expander(L["edit_prof"]):
        with st.form("edit_form"):
            n = st.text_input(L["name_field"], value=prof["nom"])
            c1, c2 = st.columns(2)
            s = c1.selectbox(L["sex_field"], L["sex_options"], index=L["sex_options"].index(prof["sexe"]))
            a = c2.number_input(L["age_field"], value=prof["age"])
            if st.form_submit_button(L["save"]):
                st.session_state.user_profile.update({"nom": n, "sexe": s, "age": a})
                st.rerun()

    st.subheader(L["cal_title"])
    today = date.today()
    cal_obj = calendar.Calendar(firstweekday=6)
    month_days = cal_obj.monthdatescalendar(today.year, today.month)
    df_logs = pd.DataFrame(st.session_state.logs)

    for week in month_days:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                st.write(f"{day.day}")
                if not df_logs.empty:
                    work_day = df_logs[df_logs['Date'] == str(day)]
                    for z in work_day['Zone'].unique():
                        if st.button(z, key=f"cal_{day}_{z}", use_container_width=True):
                            st.session_state.selected_date = str(day)

    if 'selected_date' in st.session_state:
        st.info(f"Séance du {st.session_state.selected_date}")
        st.table(df_logs[df_logs['Date'] == st.session_state.selected_date][["Exercice", "Poids", "Reps"]])

# --- ONGLET 2 : SÉANCE ---
with tab2:
    st.header(L["workout_header"])
    st.components.v1.html("""
        <button id="mic" style="background:#ff4b4b;color:white;border:none;padding:12px;border-radius:8px;width:100%;cursor:pointer;">🎙️ Parler</button>
        <script>
        const btn = document.getElementById('mic');
        btn.onclick = () => {
            const rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            rec.lang = 'fr-FR';
            rec.onresult = (e) => {
                const t = e.results[0][0].transcript;
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: t}, '*');
            };
            rec.start();
        };
        </script>
    """, height=70)
    
    t_vocal = st.text_input("Texte entendu", key="voice_input_field")
    if st.button("🤖 Analyser et remplir"):
        data = analyser_texte_vocal(t_vocal)
        st.session_state.serie_zone = data.get("zone", "Pectoraux")
        st.session_state.serie_exercice = data.get("exercice", "")
        st.session_state.voice_poids = int(data.get("poids", 135))
        st.session_state.voice_reps = int(data.get("reps", 8))
        st.rerun()

    with st.form("set_form"):
        d_seance = st.date_input(L["date_label"], date.today())
        z_seance = st.selectbox(L["zone_label"], zones_disponibles, index=zones_disponibles.index(st.session_state.serie_zone) if st.session_state.serie_zone in zones_disponibles else 0)
        e_seance = st.text_input(L["ex_label"], value=st.session_state.serie_exercice)
        c1, c2 = st.columns(2)
        p_val = c1.number_input(L["weight"], value=st.session_state.voice_poids)
        r_val = c2.number_input(L["reps"], value=st.session_state.voice_reps)
        if st.form_submit_button(L["add_set"]):
            st.session_state.temp_workout.append({"Date": str(d_seance), "Zone": z_seance, "Exercice": e_seance, "Poids": p_val, "Reps": r_val})
            st.rerun()

    if st.session_state.temp_workout:
        st.dataframe(pd.DataFrame(st.session_state.temp_workout))
        if st.button(L["validate"], type="primary"):
            st.session_state.logs.extend(st.session_state.temp_workout)
            st.session_state.temp_workout = []
            st.success("Enregistré !")

# --- ONGLET COACH AI ---
with tab_chat:
    st.header(L["coach_header"])
    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]): st.write(m["content"])
    
    prompt = st.chat_input(L["coach_placeholder"])
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        res = chat_avec_coach(prompt)
        st.session_state.chat_history.append({"role": "assistant", "content": res})
        with st.chat_message("assistant"): st.write(res)

# --- AUTRES ---
with tab3: st.header("👤 Guide"); st.video("https://www.youtube.com/watch?v=gRVjAtPip0Y")
with tab4: st.header("🎥 Vision"); st.file_uploader("Vidéo")
with tab5: st.header("📅 Historique"); st.dataframe(pd.DataFrame(st.session_state.logs))
