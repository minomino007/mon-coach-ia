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

api_key_val = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI(api_key=api_key_val, base_url="https://openrouter.ai/api/v1" )

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
        "voice_instruction": "🎙️ Clique sur le bouton micro, parle, et l'IA remplit tout automatiquement !",
        "cal_title": "📅 Calendrier d'Activités",
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
        "voice_instruction": "🎙️ Click the mic button, speak, and AI fills everything automatically!",
        "cal_title": "📅 Activity Calendar",
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
        "objectif": "Prise de masse", "poids": 205, "blessures": "Aucune", "niveau": "Intermédiaire"
    }
if 'voice_zone' not in st.session_state: st.session_state.voice_zone = "Pectoraux"
if 'voice_exercice' not in st.session_state: st.session_state.voice_exercice = ""
if 'voice_poids' not in st.session_state: st.session_state.voice_poids = 135
if 'voice_reps' not in st.session_state: st.session_state.voice_reps = 8
if 'texte_vocal' not in st.session_state: st.session_state.texte_vocal = ""
if 'serie_zone' not in st.session_state: st.session_state.serie_zone = "Pectoraux"
if 'serie_exercice' not in st.session_state: st.session_state.serie_exercice = ""
if 'last_voice_input' not in st.session_state: st.session_state.last_voice_input = ""

chest_options = [
    "Développé couché", "Développé incliné", "Développé décliné",
    "Développé haltères", "Écarté couché", "Écarté incliné",
    "Pec deck (machine)", "Cross-over à la poulie", "Pompes",
    "Pompes inclinées", "Pompes déclinées", "Dips (buste penché)",
    "Pullover haltère", "Pullover à la poulie", "Machine chest press"
]
zones_disponibles = ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos"]

# ==========================================
# 4. FONCTION ANALYSE IA (AMÉLIORÉE)
# ==========================================
def analyser_texte_vocal(texte):
    prompt = f"""Tu es un assistant expert en musculation. Analyse la demande de l'utilisateur : "{texte}".
    Extraire les informations suivantes et répondre UNIQUEMENT en JSON valide.
    
    Zones possibles : Pectoraux, Dos, Jambes, Épaules, Abdos.
    Si l'exercice concerne les pectoraux, choisis l'option la plus proche dans cette liste : {chest_options}.
    
    Clés JSON requises :
    - "zone": (string) La zone musculaire identifiée.
    - "exercice": (string) Le nom de l'exercice.
    - "poids": (int) Le poids mentionné (défaut 135 si non spécifié).
    - "reps": (int) Le nombre de répétitions (défaut 8 si non spécifié).
    - "message": (string) Un court message d'encouragement ou de confirmation de l'assistant.

    Exemple : {{"zone": "Pectoraux", "exercice": "Développé couché", "poids": 180, "reps": 10, "message": "Super série ! C'est noté."}}"""

    response = client.chat.completions.create(
        model="openai/gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    contenu = response.choices[0].message.content
    contenu = contenu.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(contenu)

L = languages[st.session_state.lang]

# ==========================================
# 5. INTERFACE UTILISATEUR
# ==========================================
st.title("🤖 Mon Gym AI Agent")

tab1, tab2, tab3, tab4, tab5 = st.tabs(L["tabs"])

# --- ONGLET 1 : PROFIL ---
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

    with st.expander(L["edit_prof"]):
        new_lang = st.selectbox(L["lang_label"], ["Français", "English"], index=0 if st.session_state.lang == "Français" else 1)
        if new_lang != st.session_state.lang:
            st.session_state.lang = new_lang
            st.rerun()
            
        with st.form("edit_profile_form_complete"):
            n = st.text_input(L["name_field"], value=prof["nom"])
            c_f1, c_f2 = st.columns(2)
            a = c_f1.number_input(L["age_field"], value=prof["age"])
            h = c_f2.text_input(L["height_field"], value=prof["grandeur"])
            p = c_f1.number_input(L["weight"], value=prof["poids"])
            obj = c_f2.selectbox(L["obj_field"], L["goals"], index=L["goals"].index(prof["objectif"]))
            b = st.text_area(L["inj_field"], value=prof["blessures"])
            if st.form_submit_button(L["save"]):
                st.session_state.user_profile.update({"nom": n, "age": a, "grandeur": h, "poids": p, "objectif": obj, "blessures": b})
                st.rerun()

    st.subheader(L["cal_title"])
    today = date.today()
    cal_obj = calendar.Calendar(firstweekday=6)
    month_days = cal_obj.monthdatescalendar(today.year, today.month)
    
    for week in month_days:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                day_label = f"**{day.day}**" if day != today else f"**{day.day}** 🌟"
                st.write(day_label)
                df_logs = pd.DataFrame(st.session_state.logs)
                if not df_logs.empty:
                    day_str = str(day)
                    work_this_day = df_logs[df_logs['Date'] == day_str]
                    if not work_this_day.empty:
                        zones_faites = work_this_day['Zone'].unique()
                        for z in zones_faites:
                            if st.button(z, key=f"prof_cal_{day}_{z}", use_container_width=True):
                                st.session_state.selected_date_prof = day_str

    if 'selected_date_prof' in st.session_state:
        st.info(f"{L['detail_title']} : {st.session_state.selected_date_prof}")
        det_df = pd.DataFrame(st.session_state.logs)
        st.table(det_df[det_df['Date'] == st.session_state.selected_date_prof][["Exercice", "Poids", "Reps"]])

# --- ONGLET 2 : SÉANCE DU JOUR ---
with tab2:
    st.header(L["workout_header"])
    st.write(L["voice_instruction"])

    # COMPOSANT VOCAL AVEC ANALYSE AUTOMATIQUE
    voice_data = st.components.v1.html("""
        <style>
            #mic-btn { background-color: #ff4b4b; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 8px; cursor: pointer; width: 100%; transition: 0.3s; }
            #mic-btn:hover { background-color: #e63939; }
            #result-box { margin-top: 10px; padding: 10px; background: #1e1e1e; color: #00ff88; border-radius: 8px; font-size: 15px; min-height: 40px; border: 1px solid #333; }
        </style>
        <button id="mic-btn" onclick="startListening()">🎙️ Cliquer pour dicter ta séance</button>
        <div id="result-box">En attente de ta voix...</div>
        <script>
        function startListening() {
            const btn = document.getElementById('mic-btn');
            const box = document.getElementById('result-box');
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                box.textContent = "❌ Ton navigateur ne supporte pas la reconnaissance vocale.";
                return;
            }
            btn.textContent = '🔴 Je t'écoute...';
            btn.style.backgroundColor = '#222';
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'fr-FR';
            recognition.interimResults = false;
            recognition.onresult = function(event) {
                const texte = event.results[0][0].transcript;
                box.textContent = '✅ Analyse de : ' + texte;
                btn.textContent = '🎙️ Parler à nouveau';
                btn.style.backgroundColor = '#ff4b4b';
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: texte}, '*');
            };
            recognition.onerror = function(event) {
                box.textContent = "❌ Erreur : " + event.error;
                btn.textContent = '🎙️ Réessayer';
                btn.style.backgroundColor = '#ff4b4b';
            };
            recognition.start();
        }
        </script>
    """, height=130)

    # Logique de traitement automatique si une nouvelle voix est détectée
    if voice_data and voice_data != st.session_state.get('last_voice_input', ''):
        st.session_state.last_voice_input = voice_data
        try:
            with st.spinner("L'IA analyse ta voix..."):
                data = analyser_texte_vocal(voice_data)
                st.session_state.serie_zone = data.get("zone", "Pectoraux")
                st.session_state.serie_exercice = data.get("exercice", "")
                st.session_state.voice_poids = int(data.get("poids", 135))
                st.session_state.voice_reps = int(data.get("reps", 8))
                st.session_state.ai_message = data.get("message", "J'ai bien compris ta séance !")
                st.rerun()
        except Exception as e:
            st.error(f"Erreur d'analyse vocale : {e}")

    st.write("**💬 Ou écris ta séance ici :**")
    texte_input = st.text_input("Ex: J'ai fait du bench press à 200 lbs pour 12 reps", value="", key="texte_manual_input", placeholder="Parle-moi de ta séance...")

    if st.button("🤖 Analyser le texte", type="secondary", use_container_width=True):
        if texte_input:
            try:
                with st.spinner("L'assistant réfléchit..."):
                    data = analyser_texte_vocal(texte_input)
                    st.session_state.serie_zone = data.get("zone", "Pectoraux")
                    st.session_state.serie_exercice = data.get("exercice", "")
                    st.session_state.voice_poids = int(data.get("poids", 135))
                    st.session_state.voice_reps = int(data.get("reps", 8))
                    st.session_state.ai_message = data.get("message", "C'est prêt !")
                    st.rerun()
            except Exception as e: st.error(f"Erreur : {e}")

    if 'ai_message' in st.session_state and st.session_state.ai_message:
        st.chat_message("assistant").write(st.session_state.ai_message)
        st.session_state.ai_message = ""

    st.divider()
    date_seance = st.date_input(L["date_label"], date.today(), key="date_input_workout")

    st.subheader("📌 Étape 1 — Choisir l'exercice")
    col_z, col_e = st.columns(2)
    with col_z:
        zone_index = zones_disponibles.index(st.session_state.serie_zone) if st.session_state.serie_zone in zones_disponibles else 0
        serie_zone = st.selectbox(L["zone_label"], zones_disponibles, index=zone_index, key="select_zone")
    with col_e:
        if serie_zone == "Pectoraux":
            ex_index = chest_options.index(st.session_state.serie_exercice) if st.session_state.serie_exercice in chest_options else 0
            serie_exercice = st.selectbox(L["ex_label"], chest_options, index=ex_index)
        else:
            serie_exercice = st.text_input(L["ex_label"], value=st.session_state.serie_exercice)

    st.session_state.serie_zone = serie_zone
    st.session_state.serie_exercice = serie_exercice

    st.divider()
    st.subheader("📋 Étape 2 — Ajouter tes séries")
    series_actuelles = [s for s in st.session_state.temp_workout if s["Exercice"] == serie_exercice]
    for i, s in enumerate(series_actuelles):
        st.write(f"✅ **Série {i+1}** — {s['Poids']} lbs × {s['Reps']} reps")

    with st.form(f"serie_form", clear_on_submit=True):
        col_w, col_r = st.columns(2)
        w_input = col_w.number_input(L["weight"], value=st.session_state.voice_poids)
        r_input = col_r.number_input(L["reps"], value=st.session_state.voice_reps)
        if st.form_submit_button("➕ Ajouter la série"):
            st.session_state.temp_workout.append({
                "Date": str(date_seance), "Zone": st.session_state.serie_zone,
                "Exercice": st.session_state.serie_exercice, "Poids": w_input, "Reps": r_input
            })
            st.rerun()

    if st.session_state.temp_workout:
        st.subheader("📊 Ta séance complète")
        st.dataframe(pd.DataFrame(st.session_state.temp_workout))
        cb1, cb2 = st.columns(2)
        if cb1.button(L["validate"], type="primary"):
            st.session_state.logs.extend(st.session_state.temp_workout)
            st.session_state.temp_workout = []
            st.success("Enregistré !")
            st.balloons()
        if cb2.button(L["clear"]):
            st.session_state.temp_workout = []
            st.rerun()

# --- ONGLET 3 : GUIDE TECHNIQUE ---
with tab3: 
    st.header("👤 Guide Technique")
    st.video("https://www.youtube.com/watch?v=gRVjAtPip0Y" )

# --- ONGLET 4 : VISION IA ---
with tab4: 
    st.header("🎥 Vision IA")
    up = st.file_uploader("Upload", type=["mp4", "mov"])
    if up:
        st.video(up)

# --- ONGLET 5 : CALENDRIER / HISTORIQUE ---
with tab5:
    st.header("📅 Historique")
    d_cal = st.date_input("Consulter", date.today())
    df_g = pd.DataFrame(st.session_state.logs)
    if not df_g.empty:
        seance = df_g[df_g['Date'] == str(d_cal)]
        if not seance.empty: 
            st.table(seance)
    st.text_area("Note du jour", value=st.session_state.notes_calendrier.get(str(d_cal), ""), key="note_hist")
