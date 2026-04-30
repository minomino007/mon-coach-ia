import streamlit as st
import pandas as pd
from datetime import date
import openai
import json
import calendar
import streamlit.components.v1 as components

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
client = openai.OpenAI(api_key=api_key_val, base_url="https://openrouter.ai/api/v1")

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
if 'serie_zone' not in st.session_state: st.session_state.serie_zone = "Pectoraux"
if 'serie_exercice' not in st.session_state: st.session_state.serie_exercice = ""
if 'last_voice_ts' not in st.session_state: st.session_state.last_voice_ts = 0
if 'ai_message' not in st.session_state: st.session_state.ai_message = ""

# ==========================================
# LISTES D'EXERCICES
# ==========================================
chest_options = ["Développé couché", "Développé incliné", "Développé décliné", "Développé haltères", "Écarté couché", "Écarté incliné", "Pec deck (machine)", "Cross-over à la poulie", "Pompes", "Pompes inclinées", "Pompes déclinées", "Dips (buste penché)", "Pullover haltère", "Pullover à la poulie", "Machine chest press"]
arm_options = ["Curl barre EZ", "Curl haltères", "Curl marteau", "Curl incliné", "Curl pupitre (Larry Scott)", "Curl concentration", "Extension triceps poulie haute", "Barre au front", "Extension triceps haltère", "Dips machine", "Pompes diamant", "Kickback haltère"]
back_options = ["Tractions", "Tirage poitrine poulie haute", "Tirage horizontal poulie basse", "Rowing barre", "Rowing haltère", "Tirage bûcheron", "Pull-over poulie haute", "Lombaires (banc)", "Soulevé de terre", "Shrugs haltères", "Tirage vertical prise serrée"]
leg_options = ["Squat barre", "Presse à cuisses", "Fentes haltères", "Leg extension", "Leg curl assis", "Leg curl allongé", "Hack squat", "Soulevé de terre jambes tendues", "Mollets debout", "Mollets assis", "Adducteurs machine"]
shoulder_options = ["Développé militaire", "Développé haltères", "Élévations latérales", "Oiseau haltères", "Tirage menton", "Développé Arnold", "Face pull", "Élévations frontales"]
abs_options = ["Crunch au sol", "Relevé de jambes", "Planche (gainage)", "Russian twist", "Crunch poulie haute", "Roulette à abdos", "Mountain climbers", "V-ups"]
zones_disponibles = ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos", "Bras"]

options_map = {
    "Pectoraux": chest_options,
    "Bras": arm_options,
    "Dos": back_options,
    "Jambes": leg_options,
    "Épaules": shoulder_options,
    "Abdos": abs_options
}

# ==========================================
# VIDÉOS YOUTUBE
# ==========================================
exercise_videos = {
    "Développé couché": "https://www.youtube.com/watch?v=rT7DgCr-3pg",
    "Développé incliné": "https://www.youtube.com/watch?v=SrqOu55lrYU",
    "Développé décliné": "https://www.youtube.com/watch?v=LfyQBUKR8SE",
    "Développé haltères": "https://www.youtube.com/watch?v=VmB1G1K7v94",
    "Écarté couché": "https://www.youtube.com/watch?v=eozdVDA78K0",
    "Écarté incliné": "https://www.youtube.com/watch?v=8iPEnT_v9vM",
    "Pec deck (machine)": "https://www.youtube.com/watch?v=O-OnN_6Xp_Y",
    "Cross-over à la poulie": "https://www.youtube.com/watch?v=Wp4p66Lnu_4",
    "Pompes": "https://www.youtube.com/watch?v=IODxDxX7oi4",
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
    "Développé militaire": "https://www.youtube.com/watch?v=2yjwxt_4Qko",
    "Élévations latérales": "https://www.youtube.com/watch?v=3VcKaXpzqRo",
    "Face pull": "https://www.youtube.com/watch?v=rep-qVOkqgk",
    "Curl barre EZ": "https://www.youtube.com/watch?v=2CT1nE_X_S0",
    "Curl haltères": "https://www.youtube.com/watch?v=ykJgrLQ_ixQ",
    "Curl marteau": "https://www.youtube.com/watch?v=7jqi2qWAUzQ",
    "Extension triceps poulie haute": "https://www.youtube.com/watch?v=2-LAMcpzODU",
    "Barre au front": "https://www.youtube.com/watch?v=d_KZx7p_DjI",
    "Crunch au sol": "https://www.youtube.com/watch?v=Xyd_fa5zoEU",
    "Relevé de jambes": "https://www.youtube.com/watch?v=l4kQd9eWclE",
    "Planche (gainage)": "https://www.youtube.com/watch?v=pSHjTRCQxIw"
}

# ==========================================
# GIFs ANIMÉS
# ==========================================
exercise_animations = {
    "Développé couché": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0025-EIeI8Vf.gif",
    "Développé incliné": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0047-3TZduzM.gif",
    "Développé décliné": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0033-GrO65fd.gif",
    "Développé haltères": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0289-SpYC0Kp.gif",
    "Tractions": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0652-lBDjFxJ.gif",
    "Tirage poitrine poulie haute": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/2330-LEprlgG.gif",
    "Soulevé de terre": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0032-ila4NZS.gif",
    "Squat barre": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0043-qXTaZnJ.gif",
    "Presse à cuisses": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/2287-V07qpXy.gif",
    "Leg extension": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0585-my33uHU.gif",
    "Leg curl assis": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0599-Zg3XY7P.gif",
    "Développé militaire": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0040-33AzZeV.gif",
    "Élévations latérales": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0334-DsgkuIt.gif",
    "Face pull": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0372-l1z0Y4Y.gif",
    "Curl barre EZ": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0294-NbVPDMW.gif",
    "Curl haltères": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/1651-1VpF8db.gif",
    "Curl marteau": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0313-slDvUAU.gif",
    "Extension triceps poulie haute": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/2406-ThKP69G.gif",
    "Barre au front": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0010-8K0w2yA.gif",
    "Dips machine": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0031-25GPyDY.gif",
    "Crunch au sol": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0972-tZkGYZ9.gif",
    "Relevé de jambes": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0472-I3tsCnC.gif",
    "Planche (gainage)": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/3544-5VXmnV5.gif"
}

# ==========================================
# 4. FONCTION ANALYSE IA
# ==========================================
def analyser_texte_vocal(texte):
    prompt = f"""Tu es un assistant expert en musculation. Analyse la demande : "{texte}".
    Zones possibles : Pectoraux, Dos, Jambes, Épaules, Abdos, Bras.
    Réponds UNIQUEMENT en JSON valide avec ces clés : zone, exercice, poids (int), reps (int), message (string encouragement).
    Exemple : {{"zone": "Pectoraux", "exercice": "Développé couché", "poids": 180, "reps": 10, "message": "Super série !"}}"""
    try:
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        contenu = response.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(contenu)
    except Exception as e:
        return {"zone": "Pectoraux", "exercice": "Développé couché", "poids": 135, "reps": 8, "message": f"Erreur : {e}"}

# ==========================================
# 5. INTERFACE UTILISATEUR
# ==========================================
L = languages[st.session_state.lang]
st.title("🤖 Mon Gym AI Agent")
tab1, tab2, tab3, tab4, tab5 = st.tabs(L["tabs"])

# ==========================================
# ONGLET 1 : PROFIL
# ==========================================
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
            old_goals = languages[st.session_state.lang]["goals"]
            new_goals = languages[new_lang]["goals"]
            try:
                idx = old_goals.index(st.session_state.user_profile["objectif"])
                st.session_state.user_profile["objectif"] = new_goals[idx]
            except:
                st.session_state.user_profile["objectif"] = new_goals[0]
            st.session_state.lang = new_lang
            st.rerun()

        with st.form("edit_profile_form"):
            n = st.text_input(L["name_field"], value=prof["nom"])
            c1, c2 = st.columns(2)
            a = c1.number_input(L["age_field"], value=prof["age"])
            h = c2.text_input(L["height_field"], value=prof["grandeur"])
            p = c1.number_input(L["weight"], value=prof["poids"])
            try:
                obj_idx = L["goals"].index(prof["objectif"])
            except:
                obj_idx = 0
            obj = c2.selectbox(L["obj_field"], L["goals"], index=obj_idx)
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
                day_label = f"**{day.day}** 🌟" if day == today else f"**{day.day}**"
                st.write(day_label)
                df_logs = pd.DataFrame(st.session_state.logs)
                if not df_logs.empty:
                    work_this_day = df_logs[df_logs['Date'] == str(day)]
                    if not work_this_day.empty:
                        zones_faites = work_this_day['Zone'].unique()
                        for z in zones_faites:
                            if st.button(z, key=f"cal_{day}_{z}", use_container_width=True):
                                st.session_state.selected_date_prof = str(day)

    if 'selected_date_prof' in st.session_state:
        st.info(f"{L['detail_title']} : {st.session_state.selected_date_prof}")
        det_df = pd.DataFrame(st.session_state.logs)
        st.table(det_df[det_df['Date'] == st.session_state.selected_date_prof][["Zone", "Exercice", "Poids", "Reps"]])

# ==========================================
# ONGLET 2 : SÉANCE DU JOUR
# ==========================================
with tab2:
    st.header(L["workout_header"])
    st.markdown(L["voice_instruction"])

    # ✅ MICRO — utilise un champ caché pour transférer le texte vers Streamlit
    voice_data = components.html("""
        <style>
            .mic-row { display:flex; gap:10px; margin-bottom:8px; }
            #mic-btn { background:#ff4b4b; color:white; padding:10px 22px; border-radius:6px; border:none; cursor:pointer; font-size:15px; }
            #stop-btn { background:#007bff; color:white; padding:10px 18px; border-radius:6px; border:none; cursor:pointer; font-size:15px; display:none; }
            #mic-btn:disabled { background:#888; cursor:not-allowed; }
            #output { margin-top:8px; padding:8px; background:#1a1a1a; color:#00ff88; border-radius:6px; font-size:14px; min-height:32px; }
        </style>
        <div class="mic-row">
            <button id="mic-btn" onclick="startMic()">🎙️ Dicter ma séance</button>
            <button id="stop-btn" onclick="stopMic()">⏹️ Arrêter</button>
        </div>
        <div id="output">En attente...</div>
        <script>
        var recog = null;
        var listening = false;
        var finalText = '';

        function startMic() {
            if (listening) return;
            var SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRec) { document.getElementById('output').textContent = '❌ Utilise Chrome.'; return; }
            finalText = '';
            recog = new SpeechRec();
            recog.lang = 'fr-FR';
            recog.continuous = true;
            recog.interimResults = true;
            recog.onstart = function() {
                listening = true;
                document.getElementById('mic-btn').textContent = '🔴 Écoute...';
                document.getElementById('mic-btn').disabled = true;
                document.getElementById('stop-btn').style.display = 'inline-block';
            };
            recog.onresult = function(e) {
                var interim = '';
                for (var i = e.resultIndex; i < e.results.length; i++) {
                    if (e.results[i].isFinal) { finalText += e.results[i][0].transcript; }
                    else { interim += e.results[i][0].transcript; }
                }
                document.getElementById('output').textContent = '🎤 ' + finalText + interim;
            };
            recog.onerror = function(e) {
                document.getElementById('output').textContent = '❌ Erreur: ' + e.error;
                resetMic();
            };
            recog.onend = function() { resetMic(); };
            recog.start();
        }

        function stopMic() {
            if (recog && listening) {
                listening = false;
                recog.stop();
                var text = finalText.trim();
                if (text) {
                    var payload = JSON.stringify({text: text, ts: Date.now()});
                    window.parent.postMessage({type: 'streamlit:setComponentValue', value: payload}, '*');
                    document.getElementById('output').textContent = '✅ Envoyé : ' + text;
                }
            }
            resetMic();
        }

        function resetMic() {
            listening = false;
            document.getElementById('mic-btn').textContent = '🎙️ Dicter ma séance';
            document.getElementById('mic-btn').disabled = false;
            document.getElementById('stop-btn').style.display = 'none';
        }
        </script>
    """, height=140)

    # Traitement du résultat vocal
    if voice_data:
        try:
            v_json = json.loads(str(voice_data))
            v_text = v_json.get("text", "")
            v_ts = v_json.get("ts", 0)
            if v_text and v_ts != st.session_state.last_voice_ts:
                st.session_state.last_voice_ts = v_ts
                with st.spinner("L'IA analyse ta voix..."):
                    data = analyser_texte_vocal(v_text)
                    st.session_state.serie_zone = data.get("zone", "Pectoraux") or "Pectoraux"
                    st.session_state.serie_exercice = data.get("exercice", "") or ""
                    st.session_state.voice_poids = int(data.get("poids") or 135)
                    st.session_state.voice_reps = int(data.get("reps") or 8)
                    st.session_state.ai_message = data.get("message", "") or ""
                    st.session_state.temp_workout.append({
                        "Date": str(date.today()),
                        "Zone": st.session_state.serie_zone,
                        "Exercice": st.session_state.serie_exercice,
                        "Poids": st.session_state.voice_poids,
                        "Reps": st.session_state.voice_reps
                    })
                    st.rerun()
        except: pass

    if st.session_state.ai_message:
        st.chat_message("assistant").write(st.session_state.ai_message)
        st.session_state.ai_message = ""

    # ✅ ANALYSER LE TEXTE — champ séparé du micro
    st.write("**💬 Ou écris ta séance ici :**")
    col_txt, col_btn = st.columns([3, 1])
    texte_input = col_txt.text_input("Ex: Bench press 200 lbs 12 reps", key="manual_input", label_visibility="collapsed")
    if col_btn.button("🤖 Analyser"):
        if texte_input.strip():
            with st.spinner("Analyse en cours..."):
                try:
                    data = analyser_texte_vocal(texte_input)
                    st.session_state.serie_zone = data.get("zone", "Pectoraux") or "Pectoraux"
                    st.session_state.serie_exercice = data.get("exercice", "") or ""
                    st.session_state.voice_poids = int(data.get("poids") or 135)
                    st.session_state.voice_reps = int(data.get("reps") or 8)
                    st.session_state.ai_message = data.get("message", "") or ""
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur : {e}")
        else:
            st.warning("Écris quelque chose avant d'analyser !")

    st.divider()
    date_seance = st.date_input(L["date_label"], date.today(), key="date_input_workout")

    st.subheader("📌 Étape 1 — Choisir l'exercice")
    col_z, col_e = st.columns(2)
    with col_z:
        zone_index = zones_disponibles.index(st.session_state.serie_zone) if st.session_state.serie_zone in zones_disponibles else 0
        serie_zone = st.selectbox(L["zone_label"], zones_disponibles, index=zone_index, key="select_zone")
    with col_e:
        current_options = options_map.get(serie_zone, chest_options)
        ex_index = current_options.index(st.session_state.serie_exercice) if st.session_state.serie_exercice in current_options else 0
        serie_exercice = st.selectbox(L["ex_label"], current_options, index=ex_index, key="select_ex")

    st.session_state.serie_zone = serie_zone
    st.session_state.serie_exercice = serie_exercice

    st.divider()
    st.subheader("📋 Étape 2 — Ajouter tes séries")
    series_actuelles = [s for s in st.session_state.temp_workout if s["Exercice"] == serie_exercice]
    for i, s in enumerate(series_actuelles):
        st.write(f"✅ **Série {i+1}** — {s['Poids']} lbs × {s['Reps']} reps")

    num_serie = len(series_actuelles) + 1
    with st.form("serie_form", clear_on_submit=True):
        col_w, col_r = st.columns(2)
        w_input = col_w.number_input(L["weight"], value=st.session_state.voice_poids)
        r_input = col_r.number_input(L["reps"], value=st.session_state.voice_reps)
        if st.form_submit_button(f"➕ Ajouter Série {num_serie}"):
            st.session_state.temp_workout.append({
                "Date": str(date_seance), "Zone": serie_zone,
                "Exercice": serie_exercice, "Poids": w_input, "Reps": r_input
            })
            st.rerun()

    if st.session_state.temp_workout:
        st.subheader("📊 Ta séance complète")
        exercices_faits = {}
        for s in st.session_state.temp_workout:
            nom_ex = s["Exercice"]
            if nom_ex not in exercices_faits:
                exercices_faits[nom_ex] = []
            exercices_faits[nom_ex].append(s)
        for nom_ex, series in exercices_faits.items():
            st.markdown(f"**💪 {nom_ex}** — *{series[0]['Zone']}*")
            for i, s in enumerate(series):
                st.write(f"　　Série {i+1} : {s['Poids']} lbs × {s['Reps']} reps")
        st.divider()
        cb1, cb2 = st.columns(2)
        if cb1.button(L["validate"], type="primary"):
            st.session_state.logs.extend(st.session_state.temp_workout)
            st.session_state.temp_workout = []
            st.success("Enregistré avec succès !")
            st.balloons()
        if cb2.button(L["clear"]):
            st.session_state.temp_workout = []
            st.rerun()

# ==========================================
# ONGLET 3 : GUIDE TECHNIQUE
# ==========================================
with tab3:
    st.header("👤 Guide Technique")
    st.write("Sélectionne une zone pour voir les exercices avec animations et vidéos.")
    guide_zone = st.selectbox("Choisir une zone", zones_disponibles, key="guide_zone_select")
    exercices_guide = options_map.get(guide_zone, chest_options)
    for ex in exercices_guide:
        with st.expander(f"📖 {ex}"):
            gif = exercise_animations.get(ex)
            if gif:
                st.image(gif, caption=f"Animation : {ex}")
            st.info("💡 Conseil : Garde une forme stricte et contrôle la charge.")
            video = exercise_videos.get(ex)
            if video:
                st.video(video)

# ==========================================
# ONGLET 4 : VISION IA
# ==========================================
with tab4:
    st.header("🎥 Vision IA")
    up = st.file_uploader("Upload vidéo", type=["mp4", "mov"])
    if up:
        st.video(up)

# ==========================================
# ONGLET 5 : CALENDRIER / HISTORIQUE
# ==========================================
with tab5:
    st.header("📅 Historique")
    d_cal = st.date_input("Consulter une date", date.today(), key="calendar_date_view")
    df_global = pd.DataFrame(st.session_state.logs)
    if not df_global.empty:
        seance_du_jour = df_global[df_global['Date'] == str(d_cal)]
        if not seance_du_jour.empty:
            st.table(seance_du_jour[["Zone", "Exercice", "Poids", "Reps"]])
    st.divider()
    n_cal = st.text_area("Note du jour", value=st.session_state.notes_calendrier.get(str(d_cal), ""), key="note_cal")
    if st.button(L["save"], key="save_note_calendar"):
        st.session_state.notes_calendrier[str(d_cal)] = n_cal
        st.success("Note enregistrée !")
