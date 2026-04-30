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

# Utilisation du client OpenAI pré-configuré
client = openai.OpenAI()

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

chest_options = ["Développé couché", "Développé incliné", "Développé décliné", "Développé haltères", "Écarté couché", "Écarté incliné", "Pec deck (machine)", "Cross-over à la poulie", "Pompes", "Pompes inclinées", "Pompes déclinées", "Dips (buste penché)", "Pullover haltère", "Pullover à la poulie", "Machine chest press"]
arm_options = ["Curl barre EZ", "Curl haltères", "Curl marteau", "Curl incliné", "Curl pupitre (Larry Scott)", "Curl concentration", "Extension triceps poulie haute", "Barre au front", "Extension triceps haltère", "Dips machine", "Pompes diamant", "Kickback haltère"]
back_options = ["Tractions", "Tirage poitrine poulie haute", "Tirage horizontal poulie basse", "Rowing barre", "Rowing haltère", "Tirage bûcheron", "Pull-over poulie haute", "Lombaires (banc)", "Soulevé de terre", "Shrugs haltères", "Tirage vertical prise serrée"]
leg_options = ["Squat barre", "Presse à cuisses", "Fentes haltères", "Leg extension", "Leg curl assis", "Leg curl allongé", "Hack squat", "Soulevé de terre jambes tendues", "Mollets debout", "Mollets assis", "Adducteurs machine"]
shoulder_options = ["Développé militaire", "Développé haltères", "Élévations latérales", "Oiseau haltères", "Tirage menton", "Développé Arnold", "Face pull", "Élévations frontales"]
abs_options = ["Crunch au sol", "Relevé de jambes", "Planche (gainage)", "Russian twist", "Crunch poulie haute", "Roulette à abdos", "Mountain climbers", "V-ups"]
zones_disponibles = ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos", "Bras"]

# Dictionnaire des vidéos par exercice
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
    "Pompes inclinées": "https://www.youtube.com/watch?v=4pS_6-N4ZfM",
    "Pompes déclinées": "https://www.youtube.com/watch?v=SKPab2z8qhA",
    "Dips (buste penché)": "https://www.youtube.com/watch?v=2z8JmcrW-As",
    "Pullover haltère": "https://www.youtube.com/watch?v=FK4rHfWtuac",
    "Pullover à la poulie": "https://www.youtube.com/watch?v=p9S_0vY_n-Y",
    "Machine chest press": "https://www.youtube.com/watch?v=nw9p_Z_3WpE",
    "Tractions": "https://www.youtube.com/watch?v=eGo4IYlbE5g",
    "Tirage poitrine poulie haute": "https://www.youtube.com/watch?v=CAwf7n6Luuc",
    "Tirage horizontal poulie basse": "https://www.youtube.com/watch?v=GZbfZ033f74",
    "Rowing barre": "https://www.youtube.com/watch?v=9efgcAjQe7E",
    "Rowing haltère": "https://www.youtube.com/watch?v=dFzUjzfih7k",
    "Tirage bûcheron": "https://www.youtube.com/watch?v=dFzUjzfih7k",
    "Pull-over poulie haute": "https://www.youtube.com/watch?v=p9S_0vY_n-Y",
    "Lombaires (banc)": "https://www.youtube.com/watch?v=5_EjZ7Xv_6E",
    "Soulevé de terre": "https://www.youtube.com/watch?v=ytGaGIn3SjE",
    "Shrugs haltères": "https://www.youtube.com/watch?v=g6qbq4i1_hQ",
    "Tirage vertical prise serrée": "https://www.youtube.com/watch?v=CAwf7n6Luuc",
    "Squat barre": "https://www.youtube.com/watch?v=SW_C1A-rejs",
    "Presse à cuisses": "https://www.youtube.com/watch?v=IZxyjW7MPJQ",
    "Fentes haltères": "https://www.youtube.com/watch?v=D7KaRcUTQeE",
    "Leg extension": "https://www.youtube.com/watch?v=YyvSfVLYd80",
    "Leg curl assis": "https://www.youtube.com/watch?v=ELOCsoDSmrg",
    "Leg curl allongé": "https://www.youtube.com/watch?v=1Tq3QdAU0P0",
    "Hack squat": "https://www.youtube.com/watch?v=0tn5K9NlCfo",
    "Soulevé de terre jambes tendues": "https://www.youtube.com/watch?v=ytGaGIn3SjE",
    "Mollets debout": "https://www.youtube.com/watch?v=-M4-G8p8fmc",
    "Mollets assis": "https://www.youtube.com/watch?v=JbyjN744z9w",
    "Adducteurs machine": "https://www.youtube.com/watch?v=S_7u6_Tf9fA",
    "Développé militaire": "https://www.youtube.com/watch?v=2yjwxt_4Qko",
    "Développé haltères": "https://www.youtube.com/watch?v=qEwKCR5JCog",
    "Élévations latérales": "https://www.youtube.com/watch?v=3VcKaXpzqRo",
    "Oiseau haltères": "https://www.youtube.com/watch?v=6yMdhi2DVao",
    "Tirage menton": "https://www.youtube.com/watch?v=ak3R7lYI7zE",
    "Développé Arnold": "https://www.youtube.com/watch?v=6mc7nm9igT4",
    "Face pull": "https://www.youtube.com/watch?v=rep-qVOkqgk",
    "Élévations frontales": "https://www.youtube.com/watch?v=-t7fuZ0KhDA",
    "Curl barre EZ": "https://www.youtube.com/watch?v=2CT1nE_X_S0",
    "Curl haltères": "https://www.youtube.com/watch?v=ykJgrLQ_ixQ",
    "Curl marteau": "https://www.youtube.com/watch?v=7jqi2qWAUzQ",
    "Curl incliné": "https://www.youtube.com/watch?v=aTYlqC_JacQ",
    "Curl pupitre (Larry Scott)": "https://www.youtube.com/watch?v=fIWP-FRFNU0",
    "Curl concentration": "https://www.youtube.com/watch?v=0AUGkch3tzc",
    "Extension triceps poulie haute": "https://www.youtube.com/watch?v=2-LAMcpzODU",
    "Barre au front": "https://www.youtube.com/watch?v=d_KZx7p_DjI",
    "Extension triceps haltère": "https://www.youtube.com/watch?v=6SS6K3lAwZ8",
    "Dips machine": "https://www.youtube.com/watch?v=6kALZikcIc0",
    "Pompes diamant": "https://www.youtube.com/watch?v=Xt_m-pXp-v0",
    "Kickback haltère": "https://www.youtube.com/watch?v=6SS6K3lAwZ8",
    "Crunch au sol": "https://www.youtube.com/watch?v=Xyd_fa5zoEU",
    "Relevé de jambes": "https://www.youtube.com/watch?v=l4kQd9eWclE",
    "Planche (gainage)": "https://www.youtube.com/watch?v=pSHjTRCQxIw",
    "Russian twist": "https://www.youtube.com/watch?v=wkD8rjkS_Rs",
    "Crunch poulie haute": "https://www.youtube.com/watch?v=2fO6_p8fXyM",
    "Roulette à abdos": "https://www.youtube.com/watch?v=rqiQtEW_v_I",
    "Mountain climbers": "https://www.youtube.com/watch?v=nmwgirgXLYM",
    "V-ups": "https://www.youtube.com/watch?v=7UVp79vW_L0"
}

# Dictionnaire des animations (GIFs) par exercice
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
    prompt = f"""En tant qu'assistant d'entraînement, analyse le texte suivant pour extraire la zone musculaire, l'exercice spécifique, le poids en livres (lbs) et le nombre de répétitions. 
    Zones possibles : Pectoraux, Dos, Jambes, Épaules, Abdos, Bras.
    Exercices : {', '.join(chest_options + arm_options + back_options + leg_options + shoulder_options + abs_options)}
    
    Texte : "{texte}"
    Format JSON: {{"zone": "...", "exercice": "...", "poids": 135, "reps": 8, "message": "..."}}"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"zone": "Pectoraux", "exercice": "Développé couché", "poids": 135, "reps": 8, "message": f"Erreur IA : {e}"}

# ==========================================
# 5. INTERFACE UTILISATEUR STREAMLIT
# ==========================================
L = languages[st.session_state.lang]
tab1, tab2, tab3, tab4, tab5 = st.tabs(L["tabs"])

# --- ONGLET 1 : PROFIL ---
with tab1:
    st.header(L["prof_header"])
    st.write(f"**{L['name_field']} :** {st.session_state.user_profile['nom']}")
    st.write(f"**{L['age_field']} :** {st.session_state.user_profile['age']} ans")
    st.write(f"**{L['height_field']} :** {st.session_state.user_profile['grandeur']}")
    st.write(f"**{L['weight']} :** {st.session_state.user_profile['poids']} lbs")
    st.write(f"**{L['obj_field']} :** {st.session_state.user_profile['objectif']}")
    st.write(f"**{L['inj_field']} :** {st.session_state.user_profile['blessures']}")

    if st.button(L["edit_prof"]): st.session_state.edit_profile = True
    if st.session_state.get('edit_profile', False):
        with st.form("profile_form"):
            st.session_state.user_profile["nom"] = st.text_input(L["name_field"], value=st.session_state.user_profile["nom"])
            st.session_state.user_profile["age"] = st.number_input(L["age_field"], value=st.session_state.user_profile["age"], min_value=15, max_value=99)
            st.session_state.user_profile["grandeur"] = st.text_input(L["height_field"], value=st.session_state.user_profile["grandeur"])
            st.session_state.user_profile["poids"] = st.number_input(L["weight"], value=st.session_state.user_profile["poids"], min_value=50, max_value=500)
            
            current_goal = st.session_state.user_profile["objectif"]
            goal_map = {"Prise de masse": "Muscle Gain", "Perte de gras": "Fat Loss", "Force": "Strength", "Endurance": "Endurance",
                        "Muscle Gain": "Prise de masse", "Fat Loss": "Perte de gras", "Strength": "Force", "Endurance": "Endurance"}
            if current_goal not in L["goals"] and current_goal in goal_map:
                current_goal = goal_map[current_goal]
            
            obj_index = L["goals"].index(current_goal) if current_goal in L["goals"] else 0
            st.session_state.user_profile["objectif"] = st.selectbox(L["obj_field"], L["goals"], index=obj_index)
            st.session_state.user_profile["blessures"] = st.text_area(L["inj_field"], value=st.session_state.user_profile["blessures"])
            if st.form_submit_button(L["save"]):
                st.session_state.edit_profile = False
                st.rerun()

    st.divider()
    st.subheader(L["cal_title"])
    st.info("Ton calendrier visuel est actif. Les jours avec séance sont marqués en vert.")

# --- ONGLET 2 : SÉANCE DU JOUR ---
with tab2:
    st.header(L["workout_header"])
    st.markdown(L["voice_instruction"])

    # Correction du TypeError en utilisant components.html
    voice_data = components.html("""
        <button id='mic-btn' style='background-color: #ff4b4b; color: white; padding: 10px 20px; border-radius: 5px; border: none; cursor: pointer;'>🎙️ Cliquer pour dicter ta séance</button>
        <button id='stop-btn' style='background-color: #007bff; color: white; padding: 10px 20px; border-radius: 5px; border: none; cursor: pointer; display: none; margin-left: 10px;'>⏹️ Arrêter</button>
        <p id='output' style='margin-top: 10px; font-family: sans-serif;'></p>
        <script>
        const micBtn = document.getElementById('mic-btn');
        const stopBtn = document.getElementById('stop-btn');
        const output = document.getElementById('output');
        let recognition;
        let isListening = false;
        let finalTranscript = '';

        if ('webkitSpeechRecognition' in window) {
            recognition = new webkitSpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'fr-FR';

            recognition.onstart = () => {
                isListening = true;
                micBtn.textContent = '🔴 Écoute...';
                stopBtn.style.display = 'inline-block';
            };

            recognition.onresult = (event) => {
                let interim = '';
                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) finalTranscript += event.results[i][0].transcript;
                    else interim += event.results[i][0].transcript;
                }
                output.textContent = finalTranscript + interim;
            };

            recognition.onend = () => { if (isListening) send(); };
            micBtn.onclick = () => { if (!isListening) recognition.start(); };
            stopBtn.onclick = () => { if (isListening) { isListening = false; recognition.stop(); } };

            function send() {
                const text = output.textContent.trim();
                if (text) {
                    const payload = JSON.stringify({text: text, ts: Date.now()});
                    window.parent.postMessage({type: 'streamlit:setComponentValue', value: payload}, '*');
                }
                micBtn.textContent = '🎙️ Cliquer pour dicter ta séance';
                stopBtn.style.display = 'none';
            }
        }
        </script>
    """, height=130)

    if voice_data:
        try:
            v_json = json.loads(voice_data)
            v_text, v_ts = v_json.get("text", ""), v_json.get("ts", 0)
            if v_text and v_ts != st.session_state.get('last_voice_ts', 0):
                st.session_state.last_voice_ts = v_ts
                with st.spinner("Analyse..."):
                    data = analyser_texte_vocal(v_text)
                    st.session_state.serie_zone = data.get("zone", "Pectoraux")
                    st.session_state.serie_exercice = data.get("exercice", "")
                    st.session_state.voice_poids = int(data.get("poids", 135))
                    st.session_state.voice_reps = int(data.get("reps", 8))
                    st.session_state.temp_workout.append({"Date": str(date.today()), "Zone": st.session_state.serie_zone, "Exercice": st.session_state.serie_exercice, "Poids": st.session_state.voice_poids, "Reps": st.session_state.voice_reps})
                    st.rerun()
        except: pass

    st.write("**💬 Ou écris ici :**")
    texte_input = st.text_input("Ex: Bench press 200 lbs 12 reps", key="manual_in")
    if st.button("🤖 Analyser", use_container_width=True):
        if texte_input:
            data = analyser_texte_vocal(texte_input)
            st.session_state.serie_zone = data.get("zone", "Pectoraux")
            st.session_state.serie_exercice = data.get("exercice", "")
            st.session_state.voice_poids = int(data.get("poids", 135))
            st.session_state.voice_reps = int(data.get("reps", 8))
            st.rerun()

    st.divider()
    serie_zone = st.selectbox(L["zone_label"], zones_disponibles, index=zones_disponibles.index(st.session_state.serie_zone) if st.session_state.serie_zone in zones_disponibles else 0)
    options_map = {"Pectoraux": chest_options, "Bras": arm_options, "Dos": back_options, "Jambes": leg_options, "Épaules": shoulder_options, "Abdos": abs_options}
    current_options = options_map.get(serie_zone, [])
    serie_exercice = st.selectbox(L["ex_label"], current_options, index=current_options.index(st.session_state.serie_exercice) if st.session_state.serie_exercice in current_options else 0)
    
    with st.form("add_form"):
        c1, c2 = st.columns(2)
        w = c1.number_input(L["weight"], value=st.session_state.voice_poids)
        r = c2.number_input(L["reps"], value=st.session_state.voice_reps)
        if st.form_submit_button(L["add_set"]):
            st.session_state.temp_workout.append({"Date": str(date.today()), "Zone": serie_zone, "Exercice": serie_exercice, "Poids": w, "Reps": r})
            st.rerun()

    if st.session_state.temp_workout:
        st.dataframe(pd.DataFrame(st.session_state.temp_workout))
        if st.button(L["validate"], type="primary"):
            st.session_state.logs.extend(st.session_state.temp_workout)
            st.session_state.temp_workout = []
            st.success("Enregistré !")
            st.balloons()

# --- ONGLET 3 : GUIDE TECHNIQUE ---
with tab3:
    st.header("👤 Guide Technique")
    g_zone = st.selectbox("Zone", zones_disponibles, key="g_zone")
    g_exs = options_map.get(g_zone, [])
    for ex in g_exs:
        with st.expander(f"📖 {ex}"):
            gif = exercise_animations.get(ex)
            if gif: st.image(gif, caption=f"Animation : {ex}")
            st.info(f"Conseil : Garde une forme stricte pour {ex}.")
            st.video(exercise_videos.get(ex, "https://www.youtube.com/watch?v=gRVjAtPip0Y"))

# --- ONGLET 4 : VISION IA ---
with tab4:
    st.header("🎥 Vision IA")
    up = st.file_uploader("Upload", type=["mp4", "mov"])
    if up: st.video(up)

# --- ONGLET 5 : CALENDRIER ---
with tab5:
    st.header("📅 Historique")
    d = st.date_input("Date", date.today())
    df = pd.DataFrame(st.session_state.logs)
    if not df.empty:
        s = df[df['Date'] == str(d)]
        if not s.empty: st.table(s)
        
