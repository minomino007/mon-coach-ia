import streamlit as st
import pandas as pd
from datetime import date
import openai
import json

# ==========================================
# 1. CONFIGURATION DE LA PAGE & CLÉ API
# ==========================================
st.set_page_config(
    page_title="Gym AI Agent PRO",
    layout="centered",
    page_icon="🏋️",
    initial_sidebar_state="collapsed"
)

# Récupération de la clé API via les secrets
api_key_val = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI(api_key=api_key_val, base_url="https://openrouter.ai/api/v1")

# ==========================================
# 2. SYSTÈME DE TRADUCTION INTÉGRAL
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
        "no_data": "Rien d'enregistré pour ce jour-là.",
        "zones": ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos"],
        "lang_code": "fr-FR"
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
        "lang_code": "en-US"
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
        "objectif": L["goals"][0], "poids": 205, "blessures": "Aucune", "niveau": "Intermédiaire"
    }

if 'voice_zone' not in st.session_state: st.session_state.voice_zone = L["zones"][0]
if 'voice_exercice' not in st.session_state: st.session_state.voice_exercice = ""
if 'voice_poids' not in st.session_state: st.session_state.voice_poids = 135
if 'voice_reps' not in st.session_state: st.session_state.voice_reps = 8
if 'texte_vocal' not in st.session_state: st.session_state.texte_vocal = ""
if 'serie_zone' not in st.session_state: st.session_state.serie_zone = L["zones"][0]
if 'serie_exercice' not in st.session_state: st.session_state.serie_exercice = ""

chest_options = [
    "Développé couché", "Développé incliné", "Développé décliné",
    "Développé haltères", "Écarté couché", "Écarté incliné",
    "Pec deck (machine)", "Cross-over à la poulie", "Pompes",
    "Pompes inclinées", "Pompes déclinées", "Dips (buste penché)",
    "Pullover haltère", "Pullover à la poulie", "Machine chest press"
]

# ==========================================
# 4. FONCTION ANALYSE TEXTE VOCAL
# ==========================================
def analyser_texte_vocal(texte):
    prompt = f"""Extraire les infos de musculation du texte suivant : "{texte}". 
    Répondre UNIQUEMENT en JSON valide avec ces clés : zone, exercice, poids (nombre entier), reps (nombre entier).
    Zones possibles (traduis si besoin) : {L['zones']}.
    Si l'exercice est pour les pectoraux, utilise un nom de cette liste : {chest_options}
    Exemple : {{"zone": "{L['zones'][0]}", "exercice": "Bench press", "poids": 180, "reps": 10}}"""

    response = client.chat.completions.create(
        model="openai/gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    contenu = response.choices[0].message.content
    contenu = contenu.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(contenu)

# ==========================================
# 5. INTERFACE UTILISATEUR
# ==========================================
st.title("🤖 Mon Gym AI Agent")

tab1, tab2, tab3, tab4, tab5 = st.tabs(L["tabs"])

# --- ONGLET 1 : PROFIL ---
with tab1:
    st.header(L["prof_header"])
    new_lang = st.selectbox(L["lang_label"], ["Français", "English"], index=0 if st.session_state.lang == "Français" else 1)
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

    prof = st.session_state.user_profile
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric(L["weight"], f"{prof['poids']} lbs")
    col_m2.metric(L["obj_field"], prof['objectif'])
    col_m3.metric(L["age_field"], f"{prof['age']}")

    st.write(f"**{L['name_field']} :** {prof['nom']} | **{L['height_field']} :** {prof['grandeur']}")
    st.warning(f"🩹 **{L['inj_field']} :** {prof['blessures']}")

    with st.expander(L["edit_prof"]):
        with st.form("edit_profile_form_complete"):
            n = st.text_input(L["name_field"], value=prof["nom"])
            c_f1, c_f2 = st.columns(2)
            a = c_f1.number_input(L["age_field"], value=prof["age"])
            h = c_f2.text_input(L["height_field"], value=prof["grandeur"])
            p = c_f1.number_input(L["weight"], value=prof["poids"])
            obj = c_f2.selectbox(L["obj_field"], L["goals"], index=0)
            b = st.text_area(L["inj_field"], value=prof["blessures"])
            if st.form_submit_button(L["save"]):
                st.session_state.user_profile.update({"nom": n, "age": a, "grandeur": h, "poids": p, "objectif": obj, "blessures": b})
                st.rerun()

# --- ONGLET 2 : SÉANCE DU JOUR ---
with tab2:
    st.header(L["workout_header"])
    st.write(L["voice_instruction"])

    # 🎙️ BOUTON MICRO TRADUIT
    st.components.v1.html(f"""
        <style>
            #mic-btn {{
                background-color: #ff4b4b;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 16px;
                border-radius: 8px;
                cursor: pointer;
                margin-bottom: 10px;
            }}
            #mic-btn:hover {{ background-color: #cc0000; }}
            #result-box {{
                margin-top: 10px;
                padding: 10px;
                background: #1e1e1e;
                color: #00ff88;
                border-radius: 8px;
                font-size: 15px;
                min-height: 40px;
            }}
        </style>
        <button id="mic-btn" onclick="startListening()">{L['mic_btn']}</button>
        <div id="result-box">{L['mic_waiting']}</div>
        <script>
        function startListening() {{
            const btn = document.getElementById('mic-btn');
            const box = document.getElementById('result-box');
            btn.textContent = '{L['mic_listening']}';
            btn.style.backgroundColor = '#888';
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = '{L['lang_code']}';
            recognition.interimResults = false;
            recognition.onresult = function(event) {{
                const texte = event.results[0][0].transcript;
                box.textContent = '{L['mic_success']}' + texte;
                btn.textContent = '{L['mic_btn']}';
                btn.style.backgroundColor = '#ff4b4b';
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: texte}}, '*');
            }};
            recognition.onerror = function(e) {{
                box.textContent = '❌ Error: ' + e.error;
                btn.textContent = '{L['mic_btn']}';
                btn.style.backgroundColor = '#ff4b4b';
            }};
            recognition.start();
        }}
        </script>
    """, height=120)

    st.write(L["manual_input_label"])
    texte_input = st.text_input("...", value=st.session_state.texte_vocal, key="texte_vocal_input")

    if st.button(L["analyze_btn"], type="primary"):
        if texte_input:
            try:
                with st.spinner("..."):
                    data = analyser_texte_vocal(texte_input)
                    st.session_state.voice_zone = data.get("zone", L["zones"][0])
                    st.session_state.serie_zone = data.get("zone", L["zones"][0])
                    st.session_state.voice_exercice = data.get("exercice", "")
                    st.session_state.serie_exercice = data.get("exercice", "")
                    st.session_state.voice_poids = int(data.get("poids", 135))
                    st.session_state.voice_reps = int(data.get("reps", 8))
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()
    date_seance = st.date_input(L["date_label"], date.today(), key="date_input_workout")

    st.subheader(L["step1"])
    col_z, col_e = st.columns(2)
    with col_z:
        zone_index = L["zones"].index(st.session_state.serie_zone) if st.session_state.serie_zone in L["zones"] else 0
        serie_zone = st.selectbox(L["zone_label"], L["zones"], index=zone_index, key="select_zone_serie")
    with col_e:
        serie_exercice = st.text_input(L["ex_label"], value=st.session_state.serie_exercice, key="input_ex_serie")

    st.session_state.serie_zone = serie_zone
    st.session_state.serie_exercice = serie_exercice

    st.divider()
    st.subheader(L["step2"])
    series_actuelles = [s for s in st.session_state.temp_workout if s["Exercice"] == serie_exercice]
    if series_actuelles:
        for i, s in enumerate(series_actuelles):
            st.write(f"✅ **{L['set_label']} {i+1}** — {s['Poids']} lbs × {s['Reps']} reps")

    num_serie = len(series_actuelles) + 1
    st.write(f"**➕ {L['set_label']} {num_serie} :**")

    with st.form(f"serie_form_{num_serie}", clear_on_submit=True):
        col_w, col_r = st.columns(2)
        w_input = col_w.number_input(L["weight"], value=st.session_state.voice_poids)
        r_input = col_r.number_input(L["reps"], value=st.session_state.voice_reps)
        if st.form_submit_button(f"➕ {L['add_set']} ({num_serie})"):
            st.session_state.temp_workout.append({
                "Date": str(date_seance), "Zone": st.session_state.serie_zone,
                "Exercice": st.session_state.serie_exercice, "Série": num_serie,
                "Poids": w_input, "Reps": r_input
            })
            st.rerun()

    if st.session_state.temp_workout:
        st.subheader(L["summary_header"])
        for s in st.session_state.temp_workout:
            st.write(f"💪 {s['Exercice']} ({s['Zone']}) : {s['Poids']} lbs x {s['Reps']} reps")
        
        st.divider()
        cb1, cb2 = st.columns(2)
        if cb1.button(L["validate"], type="primary"):
            st.session_state.logs.extend(st.session_state.temp_workout)
            st.session_state.temp_workout = []
            st.success("OK!")
            st.balloons()
        if cb2.button(L["clear"]):
            st.session_state.temp_workout = []
            st.rerun()

# --- ONGLET 3 : GUIDE ---
with tab3:
    st.header(L["tabs"][2])
    st.video("https://www.youtube.com/watch?v=gRVjAtPip0Y")

# --- ONGLET 4 : VISION ---
with tab4:
    st.header(L["tabs"][3])
    up = st.file_uploader("Upload", type=["mp4", "mov"])
    if up: st.video(up)

# --- ONGLET 5 : CALENDRIER ---
with tab5:
    st.header(L["history_header"])
    d_cal = st.date_input(L["history_view"], date.today(), key="calendar_date_view")
    df_global = pd.DataFrame(st.session_state.logs)
    if not df_global.empty:
        seance_du_jour = df_global[df_global['Date'] == str(d_cal)]
        if not seance_du_jour.empty:
            st.table(seance_du_jour)
        else:
            st.info(L["no_data"])
    
    st.divider()
    n_cal = st.text_area(L["note_day"], value=st.session_state.notes_calendrier.get(str(d_cal), ""))
    if st.button(L["save"], key="save_note_calendar"):
        st.session_state.notes_calendrier[str(d_cal)] = n_cal
        st.success("Saved!")
