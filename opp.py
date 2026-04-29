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
        "voice_instruction": "🎙️ Clique sur le bouton micro, parle, et les champs se remplissent tout seuls !",
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
        "voice_instruction": "🎙️ Click the mic button, speak, and fields fill automatically!",
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
if 'last_voice_ts' not in st.session_state: st.session_state.last_voice_ts = 0

chest_options = [
    "Développé couché", "Développé incliné", "Développé décliné",
    "Développé haltères", "Écarté couché", "Écarté incliné",
    "Pec deck (machine)", "Cross-over à la poulie", "Pompes",
    "Pompes inclinées", "Pompes déclinées", "Dips (buste penché)",
    "Pullover haltère", "Pullover à la poulie", "Machine chest press"
]
arm_options = [
    "Curl barre EZ", "Curl haltères", "Curl marteau",
    "Curl incliné", "Curl pupitre (Larry Scott)", "Curl concentration",
    "Extension triceps poulie haute", "Barre au front", "Extension triceps haltère",
    "Dips machine", "Pompes diamant", "Kickback haltère"
]
back_options = [
    "Tractions", "Tirage poitrine poulie haute", "Tirage horizontal poulie basse",
    "Rowing barre", "Rowing haltère", "Tirage bûcheron",
    "Pull-over poulie haute", "Lombaires (banc)", "Soulevé de terre",
    "Shrugs haltères", "Tirage vertical prise serrée"
]
leg_options = [
    "Squat barre", "Presse à cuisses", "Fentes haltères",
    "Leg extension", "Leg curl assis", "Leg curl allongé",
    "Hack squat", "Soulevé de terre jambes tendues", "Mollets debout",
    "Mollets assis", "Adducteurs machine"
]
shoulder_options = [
    "Développé militaire", "Développé haltères", "Élévations latérales",
    "Oiseau haltères", "Tirage menton", "Développé Arnold",
    "Face pull", "Élévations frontales"
]
abs_options = [
    "Crunch au sol", "Relevé de jambes", "Planche (gainage)",
    "Russian twist", "Crunch poulie haute", "Roulette à abdos",
    "Mountain climbers", "V-ups"
]
zones_disponibles = ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos", "Bras"]

# Dictionnaire des vidéos par exercice (Liens YouTube courts et efficaces)
exercise_videos = {
    "Développé couché": "https://www.youtube.com/watch?v=rT7DgCr-3pg",
    "Développé incliné": "https://www.youtube.com/watch?v=SrqOu55lrYU",
    "Développé décliné": "https://www.youtube.com/watch?v=LfyQBUKR8SE",
    "Développé haltères": "https://www.youtube.com/watch?v=VmB1G1K7v94",
    "Écarté couché": "https://www.youtube.com/watch?v=eozdVDA78K0",
    "Pec deck (machine )": "https://www.youtube.com/watch?v=O-OnN_6Xp_Y",
    "Pompes": "https://www.youtube.com/watch?v=IODxDxX7oi4",
    "Dips (buste penché )": "https://www.youtube.com/watch?v=2z8JmcrW-As",
    "Tractions": "https://www.youtube.com/watch?v=eGo4IYlbE5g",
    "Tirage poitrine poulie haute": "https://www.youtube.com/watch?v=CAwf7n6Luuc",
    "Tirage horizontal poulie basse": "https://www.youtube.com/watch?v=GZbfZ033f74",
    "Rowing barre": "https://www.youtube.com/watch?v=9efgcAjQe7E",
    "Rowing haltère": "https://www.youtube.com/watch?v=dFzUjzfih7k",
    "Soulevé de terre": "https://www.youtube.com/watch?v=ytGaGIn3SjE",
    "Squat barre": "https://www.youtube.com/watch?v=SW_C1A-rejs",
    "Presse à cuisses": "https://www.youtube.com/watch?v=IZxyjW7MPJQ",
    "Fentes haltères": "https://www.youtube.com/watch?v=D7KaRcUTQeE",
    "Leg extension": "https://www.youtube.com/watch?v=YyvSfVLYd80",
    "Leg curl assis": "https://www.youtube.com/watch?v=ELOCsoDSmrg",
    "Mollets debout": "https://www.youtube.com/watch?v=-M4-G8p8fmc",
    "Développé militaire": "https://www.youtube.com/watch?v=2yjwxt_4Qko",
    "Développé haltères": "https://www.youtube.com/watch?v=qEwKCR5JCog",
    "Élévations latérales": "https://www.youtube.com/watch?v=3VcKaXpzqRo",
    "Oiseau haltères": "https://www.youtube.com/watch?v=6yMdhi2DVao",
    "Face pull": "https://www.youtube.com/watch?v=rep-qVOkqgk",
    "Curl barre EZ": "https://www.youtube.com/watch?v=2CT1nE_X_S0",
    "Curl haltères": "https://www.youtube.com/watch?v=ykJgrLQ_ixQ",
    "Curl marteau": "https://www.youtube.com/watch?v=7jqi2qWAUzQ",
    "Extension triceps poulie haute": "https://www.youtube.com/watch?v=2-LAMcpzODU",
    "Barre au front": "https://www.youtube.com/watch?v=d_KZx7p_DjI",
    "Dips machine": "https://www.youtube.com/watch?v=6kALZikcIc0",
    "Crunch au sol": "https://www.youtube.com/watch?v=Xyd_fa5zoEU",
    "Relevé de jambes": "https://www.youtube.com/watch?v=l4kQd9eWclE",
    "Planche (gainage )": "https://www.youtube.com/watch?v=pSHjTRCQxIw",
    "Russian twist": "https://www.youtube.com/watch?v=wkD8rjkS_Rs",
    "Roulette à abdos": "https://www.youtube.com/watch?v=rqiQtEW_v_I"
}

# ==========================================
# 4. FONCTION ANALYSE IA
# ==========================================
def analyser_texte_vocal(texte ):
    prompt = f"""Tu es un assistant expert en musculation. Analyse la demande de l'utilisateur : "{texte}".
    Extraire les informations suivantes et répondre UNIQUEMENT en JSON valide.
    
    Zones possibles : Pectoraux, Dos, Jambes, Épaules, Abdos, Bras.
    Choisis l'option la plus proche dans ces listes selon la zone :
    - Pectoraux: {chest_options}
    - Bras: {arm_options}
    - Dos: {back_options}
    - Jambes: {leg_options}
    - Épaules: {shoulder_options}
    - Abdos: {abs_options}
    
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

    voice_data = st.components.v1.html(f"""
        <style>
            .btn-container {{ display: flex; gap: 10px; }}
            #mic-btn {{ background-color: #ff4b4b; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 8px; cursor: pointer; flex: 2; transition: 0.3s; }}
            #stop-btn {{ background-color: #333; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 8px; cursor: pointer; flex: 1; display: none; transition: 0.3s; }}
            #mic-btn:hover {{ background-color: #e63939; }}
            #stop-btn:hover {{ background-color: #555; }}
            #result-box {{ margin-top: 10px; padding: 10px; background: #1e1e1e; color: #00ff88; border-radius: 8px; font-size: 15px; min-height: 40px; border: 1px solid #333; }}
        </style>
        <div class="btn-container">
            <button id="mic-btn" onclick="startListening()">🎙️ Dicter ma séance</button>
            <button id="stop-btn" onclick="stopListening()">⏹️ Arrêter</button>
        </div>
        <div id="result-box">En attente de ta voix...</div>
        <script>
        let recognition;
        let lastFinal = "";
        let isListening = false;
        
        function startListening() {{
            if (isListening) return;
            const btn = document.getElementById('mic-btn');
            const stopBtn = document.getElementById('stop-btn');
            const box = document.getElementById('result-box');
            
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
                box.textContent = "❌ Ton navigateur ne supporte pas la reconnaissance vocale.";
                return;
            }}

            isListening = true;
            btn.textContent = '🔴 Je t\\'écoute...';
            btn.style.backgroundColor = '#222';
            stopBtn.style.display = 'block';
            lastFinal = "";
            
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'fr-FR';
            recognition.interimResults = true;
            recognition.continuous = true;

            recognition.onresult = function(event) {{
                let interim_transcript = '';
                let final_transcript = '';
                for (let i = event.resultIndex; i < event.results.length; ++i) {{
                    if (event.results[i].isFinal) {{
                        final_transcript += event.results[i][0].transcript;
                    }} else {{
                        interim_transcript += event.results[i][0].transcript;
                    }}
                }}
                if (final_transcript) lastFinal += final_transcript;
                box.textContent = '🎤 ' + (lastFinal || interim_transcript);
            }};

            recognition.onerror = function(event) {{
                box.textContent = "❌ Erreur : " + event.error;
                resetUI();
            }};

            recognition.onend = function() {{
                if (isListening) resetUI();
            }};

            recognition.start();
        }}

        function stopListening() {{
            if (recognition && isListening) {{
                isListening = false;
                recognition.stop();
                const box = document.getElementById('result-box');
                const currentText = box.textContent.replace('🎤 ', '');
                const textToSend = lastFinal || currentText;
                
                if (textToSend && textToSend !== "En attente de ta voix...") {{
                    const payload = JSON.stringify({{text: textToSend, ts: Date.now()}});
                    window.parent.postMessage({{type: 'streamlit:setComponentValue', value: payload}}, '*');
                }}
            }}
            resetUI();
        }}

        function resetUI() {{
            isListening = false;
            const btn = document.getElementById('mic-btn');
            const stopBtn = document.getElementById('stop-btn');
            btn.textContent = '🎙️ Dicter ma séance';
            btn.style.backgroundColor = '#ff4b4b';
            stopBtn.style.display = 'none';
        }}
        </script>
    """, height=130)

    if voice_data:
        try:
            v_json = json.loads(voice_data)
            v_text = v_json.get("text", "")
            v_ts = v_json.get("ts", 0)
            
            if v_text and v_ts != st.session_state.get('last_voice_ts', 0):
                st.session_state.last_voice_ts = v_ts
                with st.spinner("L'IA analyse ta voix..."):
                    data = analyser_texte_vocal(v_text)
                    st.session_state.serie_zone = data.get("zone", "Pectoraux")
                    st.session_state.serie_exercice = data.get("exercice", "")
                    st.session_state.voice_poids = int(data.get("poids", 135))
                    st.session_state.voice_reps = int(data.get("reps", 8))
                    st.session_state.ai_message = data.get("message", "Série ajoutée automatiquement !")
                    
                    st.session_state.temp_workout.append({
                        "Date": str(date_seance), 
                        "Zone": st.session_state.serie_zone,
                        "Exercice": st.session_state.serie_exercice, 
                        "Poids": st.session_state.voice_poids, 
                        "Reps": st.session_state.voice_reps
                    })
                    st.rerun()
        except:
            pass

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
        elif serie_zone == "Bras":
            ex_index = arm_options.index(st.session_state.serie_exercice) if st.session_state.serie_exercice in arm_options else 0
            serie_exercice = st.selectbox(L["ex_label"], arm_options, index=ex_index)
        elif serie_zone == "Dos":
            ex_index = back_options.index(st.session_state.serie_exercice) if st.session_state.serie_exercice in back_options else 0
            serie_exercice = st.selectbox(L["ex_label"], back_options, index=ex_index)
        elif serie_zone == "Jambes":
            ex_index = leg_options.index(st.session_state.serie_exercice) if st.session_state.serie_exercice in leg_options else 0
            serie_exercice = st.selectbox(L["ex_label"], leg_options, index=ex_index)
        elif serie_zone == "Épaules":
            ex_index = shoulder_options.index(st.session_state.serie_exercice) if st.session_state.serie_exercice in shoulder_options else 0
            serie_exercice = st.selectbox(L["ex_label"], shoulder_options, index=ex_index)
        elif serie_zone == "Abdos":
            ex_index = abs_options.index(st.session_state.serie_exercice) if st.session_state.serie_exercice in abs_options else 0
            serie_exercice = st.selectbox(L["ex_label"], abs_options, index=ex_index)
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
    st.write("Sélectionne une zone pour voir les exercices et les conseils techniques.")
    
    guide_zone = st.selectbox("Choisir une zone", zones_disponibles, key="guide_zone_select")
    
    zone_to_options = {
        "Pectoraux": chest_options,
        "Dos": back_options,
        "Jambes": leg_options,
        "Épaules": shoulder_options,
        "Abdos": abs_options,
        "Bras": arm_options
    }
    
    exercices_guide = zone_to_options.get(guide_zone, [])
    
    if exercices_guide:
        st.subheader(f"Exercices pour : {guide_zone}")
        for ex in exercices_guide:
            with st.expander(f"📖 {ex}"):
                st.write(f"Voici comment réaliser correctement l'exercice : **{ex}**.")
                st.info("💡 Conseil : Garde une forme stricte et contrôle la charge.")
                
                video_url = exercise_videos.get(ex, "https://www.youtube.com/watch?v=gRVjAtPip0Y" )
                st.video(video_url)

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
