import streamlit as st
import pandas as pd
from datetime import date, timedelta
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

# Correction de l'erreur 401 : On utilise la clé directe
api_key_val = "sk-proj-7_R7-BvF7H_OaE5G-iNqXm8G-1N4"
client = openai.OpenAI(api_key=api_key_val)

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
        "no_data": "Rien d'enregistré.",
        "zones": ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos"],
        "lang_code": "fr-FR",
        "cal_title": "📅 Calendrier d'Entraînement"
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
        "no_data": "Nothing recorded.",
        "zones": ["Chest", "Back", "Legs", "Shoulders", "Abs"],
        "lang_code": "en-US",
        "cal_title": "📅 Training Calendar"
    }
}

# ==========================================
# 3. INITIALISATION MÉMOIRE
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

# Initialisation des variables vocales pour éviter les erreurs
for key in ['voice_zone', 'serie_zone']:
    if key not in st.session_state: st.session_state[key] = L["zones"][0]
for key in ['voice_exercice', 'serie_exercice', 'texte_vocal']:
    if key not in st.session_state: st.session_state[key] = ""
if 'voice_poids' not in st.session_state: st.session_state.voice_poids = 135
if 'voice_reps' not in st.session_state: st.session_state.voice_reps = 8

# ==========================================
# 4. FONCTION ANALYSE TEXTE VOCAL
# ==========================================
def analyser_texte_vocal(texte):
    prompt = f"""Extraire les infos de musculation : "{texte}". 
    Répondre UNIQUEMENT en JSON : zone, exercice, poids (int), reps (int).
    Zones : {L['zones']}.
    Exemple : {{"zone": "{L['zones'][0]}", "exercice": "Bench press", "poids": 180, "reps": 10}}"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.choices[0].message.content.strip())

# ==========================================
# 5. INTERFACE UTILISATEUR
# ==========================================
st.title("🤖 Mon Gym AI Agent")
tab1, tab2, tab3, tab4, tab5 = st.tabs(L["tabs"])

# --- ONGLET 1 : PROFIL AVEC CALENDRIER VISUEL ---
with tab1:
    st.header(L["prof_header"])
    prof = st.session_state.user_profile
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric(L["weight"], f"{prof['poids']} lbs")
    col_m2.metric(L["obj_field"], prof['objectif'])
    col_m3.metric(L["age_field"], f"{prof['age']}")

    # --- NOUVEAU CALENDRIER VISUEL (Comme ton image) ---
    st.divider()
    st.subheader(L["cal_title"])
    
    today = date.today()
    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdatescalendar(today.year, today.month)
    
    # Affichage de la grille du mois
    for week in month_days:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                # On affiche le numéro du jour
                is_today = "⭐" if day == today else ""
                st.write(f"**{day.day}** {is_today}")
                
                # Vérifier si on a travaillé ce jour-là
                df_logs = pd.DataFrame(st.session_state.logs)
                if not df_logs.empty:
                    day_str = str(day)
                    work_this_day = df_logs[df_logs['Date'] == day_str]
                    if not work_this_day.empty:
                        # On affiche les zones travaillées en bleu (comme ton image)
                        zones_faites = work_this_day['Zone'].unique()
                        for z in zones_faites:
                            if st.button(z, key=f"btn_{day}_{z}", use_container_width=True):
                                # Si on clique, on montre le détail en bas
                                st.session_state.detail_date = day_str

    # Affichage du détail quand on clique
    if 'detail_date' in st.session_state:
        st.info(f"🔎 Détail du {st.session_state.detail_date}")
        det = pd.DataFrame(st.session_state.logs)
        st.table(det[det['Date'] == st.session_state.detail_date][["Exercice", "Poids", "Reps"]])

    with st.expander(L["edit_prof"]):
        lang_choice = st.selectbox(L["lang_label"], ["Français", "English"], index=0 if st.session_state.lang == "Français" else 1)
        if lang_choice != st.session_state.lang:
            st.session_state.lang = lang_choice
            st.rerun()

# --- ONGLET 2 : SÉANCE (AVEC FIX ERREUR 401) ---
with tab2:
    st.header(L["workout_header"])
    
    # Bouton Micro HTML
    st.components.v1.html(f"""
        <button id="mic-btn" style="background:#ff4b4b;color:white;border:none;padding:12px;border-radius:8px;width:100%;cursor:pointer;">{L['mic_btn']}</button>
        <div id="res" style="color:#00ff88;margin-top:10px;">{L['mic_waiting']}</div>
        <script>
        const btn = document.getElementById('mic-btn');
        btn.onclick = () => {{
            const rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            rec.lang = '{L['lang_code']}';
            rec.onresult = (e) => {{
                const t = e.results[0][0].transcript;
                document.getElementById('res').innerText = '{L['mic_success']}' + t;
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: t}}, '*');
            }};
            rec.start();
        }};
        </script>
    """, height=100)

    st.write(L["manual_input_label"])
    txt_vocal = st.text_input("...", value=st.session_state.texte_vocal)

    if st.button(L["analyze_btn"], type="primary"):
        if txt_vocal:
            data = analyser_texte_vocal(txt_vocal)
            st.session_state.serie_zone = data.get("zone", L["zones"][0])
            st.session_state.serie_exercice = data.get("exercice", "")
            st.session_state.voice_poids = int(data.get("poids", 135))
            st.session_state.voice_reps = int(data.get("reps", 8))
            st.rerun()

    st.divider()
    dt = st.date_input(L["date_label"], date.today())
    
    col1, col2 = st.columns(2)
    with col1: sz = st.selectbox(L["zone_label"], L["zones"], index=L["zones"].index(st.session_state.serie_zone) if st.session_state.serie_zone in L["zones"] else 0)
    with col2: se = st.text_input(L["ex_label"], value=st.session_state.serie_exercice)
    
    with st.form("set_form"):
        cw, cr = st.columns(2)
        win = cw.number_input(L["weight"], value=st.session_state.voice_poids)
        rin = cr.number_input(L["reps"], value=st.session_state.voice_reps)
        if st.form_submit_button(L["add_set"]):
            st.session_state.temp_workout.append({"Date": str(dt), "Zone": sz, "Exercice": se, "Poids": win, "Reps": rin})
            st.rerun()

    if st.session_state.temp_workout:
        st.subheader(L["summary_header"])
        st.dataframe(pd.DataFrame(st.session_state.temp_workout))
        if st.button(L["validate"]):
            st.session_state.logs.extend(st.session_state.temp_workout)
            st.session_state.temp_workout = []
            st.success("Enregistré !")
            st.balloons()

# --- AUTRES ONGLETS (STANDARDS) ---
with tab3: st.video("https://www.youtube.com/watch?v=gRVjAtPip0Y")
with tab4: st.file_uploader("Upload", type=["mp4", "mov"])
with tab5:
    st.header(L["history_header"])
    d_view = st.date_input(L["history_view"], date.today())
    df_h = pd.DataFrame(st.session_state.logs)
    if not df_h.empty:
        st.table(df_h[df_h['Date'] == str(d_view)])
