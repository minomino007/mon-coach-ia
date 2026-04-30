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
        "validate": "✅ Enregistrer l\'entraînement complet",
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
        "cal_title": "📅 Calendrier d\'Activités",
        "detail_title": "🔎 Détail de la séance"
    },
    "English": {
        "tabs": ["📊 Profile", "🏋️ Today\'s Workout", "👤 Guide", "🎥 Vision", "📅 Calendar"],
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
        "nom": "Athlète", "age": 25, "grandeur": "5\'10",
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

# Dictionnaire des vidéos par exercice
exercise_videos = {
    "Développé couché": "https://www.youtube.com/watch?v=rT7DgCr-3pg",
    "Développé incliné": "https://www.youtube.com/watch?v=SrqOu55lrYU",
    "Développé décliné": "https://www.youtube.com/watch?v=LfyQBUKR8SE",
    "Développé haltères": "https://www.youtube.com/watch?v=VmB1G1K7v94",
    "Écarté couché": "https://www.youtube.com/watch?v=eozdVDA78K0",
    "Écarté incliné": "https://www.youtube.com/watch?v=8iPEnT_v9vM",
    "Pec deck (machine )": "https://www.youtube.com/watch?v=O-OnN_6Xp_Y",
    "Cross-over à la poulie": "https://www.youtube.com/watch?v=Wp4p66Lnu_4",
    "Pompes": "https://www.youtube.com/watch?v=IODxDxX7oi4",
    "Pompes inclinées": "https://www.youtube.com/watch?v=4pS_6-N4ZfM",
    "Pompes déclinées": "https://www.youtube.com/watch?v=SKPab2z8qhA",
    "Dips (buste penché )": "https://www.youtube.com/watch?v=2z8JmcrW-As",
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
    "Lombaires (banc )": "https://www.youtube.com/watch?v=5_EjZ7Xv_6E",
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
    "Curl pupitre (Larry Scott )": "https://www.youtube.com/watch?v=fIWP-FRFNU0",
    "Curl concentration": "https://www.youtube.com/watch?v=0AUGkch3tzc",
    "Extension triceps poulie haute": "https://www.youtube.com/watch?v=2-LAMcpzODU",
    "Barre au front": "https://www.youtube.com/watch?v=d_KZx7p_DjI",
    "Extension triceps haltère": "https://www.youtube.com/watch?v=6SS6K3lAwZ8",
    "Dips machine": "https://www.youtube.com/watch?v=6kALZikcIc0",
    "Pompes diamant": "https://www.youtube.com/watch?v=Xt_m-pXp-v0",
    "Kickback haltère": "https://www.youtube.com/watch?v=6SS6K3lAwZ8",
    "Crunch au sol": "https://www.youtube.com/watch?v=Xyd_fa5zoEU",
    "Relevé de jambes": "https://www.youtube.com/watch?v=l4kQd9eWclE",
    "Planche (gainage )": "https://www.youtube.com/watch?v=pSHjTRCQxIw",
    "Russian twist": "https://www.youtube.com/watch?v=wkD8rjkS_Rs",
    "Crunch poulie haute": "https://www.youtube.com/watch?v=2fO6_p8fXyM",
    "Roulette à abdos": "https://www.youtube.com/watch?v=rqiQtEW_v_I",
    "Mountain climbers": "https://www.youtube.com/watch?v=nmwgirgXLYM",
    "V-ups": "https://www.youtube.com/watch?v=7UVp79vW_L0"
}

# Dictionnaire des animations (GIFs ) par exercice
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
    "Planche (gainage )": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/3544-5VXmnV5.gif"
}

# ==========================================
# 4. FONCTION ANALYSE IA
# ==========================================
def analyser_texte_vocal(texte ):
    prompt = f"""En tant qu\'assistant d\'entraînement, analyse le texte suivant pour extraire la zone musculaire, l\'exercice spécifique, le poids en livres (lbs) et le nombre de répétitions. Si le poids ou les répétitions ne sont pas mentionnés, utilise des valeurs par défaut raisonnables (ex: poids 135, reps 8). Si l\'exercice n\'est pas clair, suggère un exercice courant pour la zone mentionnée. Retourne le résultat au format JSON. Les zones musculaires possibles sont : Pectoraux, Dos, Jambes, Épaules, Abdos, Bras. Les exercices sont : {', '.join(chest_options + arm_options + back_options + leg_options + shoulder_options + abs_options)}. Si tu ne trouves pas l\'exercice exact, trouve le plus proche ou un exercice commun pour la zone.\n\nTexte à analyser : "{texte}"\nFormat de sortie JSON: {{"zone": "<zone_musculaire>", "exercice": "<exercice_specifique>", "poids": <poids_en_lbs>, "reps": <nombre_de_repetitions>, "message": "<message_de_confirmation_ou_suggestion>"}}\n"""
    
    response = client.chat.completions.create(
        model="gpt-4.1-mini",  # Ou un autre modèle compatible OpenRouter
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "Tu es un assistant d\'entraînement qui extrait des informations de texte."},
            {"role": "user", "content": prompt}
        ]
    )
    return json.loads(response.choices[0].message.content)

# ==========================================
# 5. INTERFACE UTILISATEUR STREAMLIT
# ==========================================
L = languages[st.session_state.lang]

tab1, tab2, tab3, tab4, tab5 = st.tabs(L["tabs"])

# --- ONGLET 1 : PROFIL ---
with tab1:
    st.header(L["prof_header"])
    
    # Affichage du profil
    st.write(f"**{L['name_field']} :** {st.session_state.user_profile['nom']}")
    st.write(f"**{L['age_field']} :** {st.session_state.user_profile['age']} ans")
    st.write(f"**{L['height_field']} :** {st.session_state.user_profile['grandeur']}")
    st.write(f"**{L['weight']} :** {st.session_state.user_profile['poids']} lbs")
    st.write(f"**{L['obj_field']} :** {st.session_state.user_profile['objectif']}")
    st.write(f"**{L['inj_field']} :** {st.session_state.user_profile['blessures']}")

    if st.button(L["edit_prof"]):
        st.session_state.edit_profile = True

    if st.session_state.get('edit_profile', False):
        with st.form("profile_form"):
            st.session_state.user_profile["nom"] = st.text_input(L["name_field"], value=st.session_state.user_profile["nom"])
            st.session_state.user_profile["age"] = st.number_input(L["age_field"], value=st.session_state.user_profile["age"], min_value=15, max_value=99)
            st.session_state.user_profile["grandeur"] = st.text_input(L["height_field"], value=st.session_state.user_profile["grandeur"])
            st.session_state.user_profile["poids"] = st.number_input(L["weight"], value=st.session_state.user_profile["poids"], min_value=50, max_value=500)
            
            # Correction du bug de langue pour l'objectif
            current_goal_lang = st.session_state.user_profile["objectif"]
            if st.session_state.lang == "English":
                # Convertir l'objectif actuel en anglais si nécessaire pour l'affichage
                if current_goal_lang == "Prise de masse": current_goal_lang = "Muscle Gain"
                elif current_goal_lang == "Perte de gras": current_goal_lang = "Fat Loss"
                elif current_goal_lang == "Force": current_goal_lang = "Strength"
                elif current_goal_lang == "Endurance": current_goal_lang = "Endurance"
            else:
                # Convertir l'objectif actuel en français si nécessaire pour l'affichage
                if current_goal_lang == "Muscle Gain": current_goal_lang = "Prise de masse"
                elif current_goal_lang == "Fat Loss": current_goal_lang = "Perte de gras"
                elif current_goal_lang == "Strength": current_goal_lang = "Force"
                elif current_goal_lang == "Endurance": current_goal_lang = "Endurance"

            obj_index = L["goals"].index(current_goal_lang) if current_goal_lang in L["goals"] else 0
            st.session_state.user_profile["objectif"] = st.selectbox(L["obj_field"], L["goals"], index=obj_index)
            
            st.session_state.user_profile["blessures"] = st.text_area(L["inj_field"], value=st.session_state.user_profile["blessures"])
            if st.form_submit_button(L["save"]):
                st.session_state.edit_profile = False
                st.rerun()

    st.divider()
    st.subheader(L["cal_title"])
    df_logs = pd.DataFrame(st.session_state.logs)
    if not df_logs.empty:
        df_logs['Date'] = pd.to_datetime(df_logs['Date'])
        df_logs['Mois'] = df_logs['Date'].dt.to_period('M')
        
        current_month = date.today().replace(day=1)
        if 'current_calendar_month' not in st.session_state:
            st.session_state.current_calendar_month = current_month

        col_prev, col_month, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("◀️", key="prev_month_cal"): 
                st.session_state.current_calendar_month -= pd.DateOffset(months=1)
                st.rerun()
        with col_month:
            st.markdown(f"<h3 style='text-align: center;'>{st.session_state.current_calendar_month.strftime('%B %Y')}</h3>", unsafe_allow_html=True)
        with col_next:
            if st.button("▶️", key="next_month_cal"): 
                st.session_state.current_calendar_month += pd.DateOffset(months=1)
                st.rerun()

        cal = calendar.Calendar()
        month_days = cal.monthdatescalendar(st.session_state.current_calendar_month.year, st.session_state.current_calendar_month.month)

        st.markdown("<style>div.st-emotion-cache-1r6dm1x {padding: 0px !important;}</style>", unsafe_allow_html=True)
        st.markdown("<style>div.st-emotion-cache-1r6dm1x > div {padding: 0px !important;}</style>", unsafe_allow_html=True)

        st.markdown("<div style='display: grid; grid-template-columns: repeat(7, 1fr); text-align: center; font-weight: bold;'>" +
                    "<span>Lun</span><span>Mar</span><span>Mer</span><span>Jeu</span><span>Ven</span><span>Sam</span><span>Dim</span>" +
                    "</div>", unsafe_allow_html=True)

        for week in month_days:
            week_str = "<div style='display: grid; grid-template-columns: repeat(7, 1fr); text-align: center;'>"
            for day in week:
                day_str = str(day.day)
                style = "padding: 5px; border: 1px solid #eee; min-height: 50px; position: relative;"
                
                if day.month != st.session_state.current_calendar_month.month:
                    style += "color: #aaa;"
                
                if not df_logs[df_logs['Date'].dt.date == day].empty:
                    style += "background-color: #d4edda; border-color: #28a745;"
                    day_str += "  
🏋️"
                
                if day == date.today():
                    style += "border: 2px solid #007bff;"

                week_str += f"<span style='{style}'>{day_str}</span>"
            week_str += "</div>"
            st.markdown(week_str, unsafe_allow_html=True)

# --- ONGLET 2 : SÉANCE DU JOUR ---
with tab2:
    st.header(L["workout_header"])
    st.markdown(L["voice_instruction"])

    voice_data = st.empty().html("""
        <button id='mic-btn' style='background-color: #ff4b4b; color: white; padding: 10px 20px; border-radius: 5px; border: none; cursor: pointer;'>🎙️ Cliquer pour dicter ta séance</button>
        <button id='stop-btn' style='background-color: #007bff; color: white; padding: 10px 20px; border-radius: 5px; border: none; cursor: pointer; display: none; margin-left: 10px;'>⏹️ Arrêter</button>
        <p id='output' style='margin-top: 10px;'></p>
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
            recognition.lang = 'fr-FR'; // Langue par défaut

            recognition.onstart = function() {
                isListening = true;
                micBtn.textContent = '🔴 Écoute en cours...';
                micBtn.style.backgroundColor = '#28a745';
                stopBtn.style.display = 'inline-block';
                output.textContent = 'En attente de ta voix...';
                finalTranscript = '';
            };

            recognition.onresult = function(event) {
                let interimTranscript = '';
                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    } else {
                        interimTranscript += event.results[i][0].transcript;
                    }
                }
                output.textContent = finalTranscript + interimTranscript;
            };

            recognition.onerror = function(event) {
                console.error('Speech recognition error', event);
                output.textContent = 'Erreur de reconnaissance vocale. Réessaie.';
                resetUI();
            };

            recognition.onend = function() {
                if (isListening) { // Si l'écoute s'est arrêtée sans clic sur stop
                    sendTextToStreamlit(finalTranscript);
                }
                resetUI();
            };

            micBtn.onclick = function() {
                if (!isListening) {
                    recognition.start();
                }
            };

            stopBtn.onclick = function() {
                if (isListening) {
                    recognition.stop();
                    sendTextToStreamlit(finalTranscript);
                }
            };

        } else {
            micBtn.style.display = 'none';
            stopBtn.style.display = 'none';
            output.textContent = 'Reconnaissance vocale non supportée par ce navigateur.';
        }

        function sendTextToStreamlit(text) {
            const lastFinal = text.trim();
            const currentText = output.textContent.trim();
            const textToSend = lastFinal || currentText;
            if (textToSend && textToSend !== "En attente de ta voix...") {
                const payload = JSON.stringify({text: textToSend, ts: Date.now()});
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: payload}, '*');
            }
            resetUI();
        }
        function resetUI() {
            isListening = false;
            const btn = document.getElementById('mic-btn');
            const stopBtn = document.getElementById('stop-btn');
            btn.textContent = '🎙️ Cliquer pour dicter ta séance';
            btn.style.backgroundColor = '#ff4b4b';
            stopBtn.style.display = 'none';
        }
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
                        "Date": str(date.today()), "Zone": st.session_state.serie_zone,
                        "Exercice": st.session_state.serie_exercice, "Poids": st.session_state.voice_poids, "Reps": st.session_state.voice_reps
                    })
                    st.rerun()
        except: pass

    st.write("**💬 Ou écris ta séance ici :**")
    texte_input = st.text_input("Ex: J'ai fait du bench press à 200 lbs pour 12 reps", value="", key="texte_manual_input")
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
        options_map = {"Pectoraux": chest_options, "Bras": arm_options, "Dos": back_options, "Jambes": leg_options, "Épaules": shoulder_options, "Abdos": abs_options}
        current_options = options_map.get(serie_zone, [])
        if current_options:
            ex_index = current_options.index(st.session_state.serie_exercice) if st.session_state.serie_exercice in current_options else 0
            serie_exercice = st.selectbox(L["ex_label"], current_options, index=ex_index)
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
            st.session_state.temp_workout.append({"Date": str(date_seance), "Zone": st.session_state.serie_zone, "Exercice": st.session_state.serie_exercice, "Poids": w_input, "Reps": r_input})
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
    guide_zone = st.selectbox("Choisir une zone", zones_disponibles, key="guide_zone_select")
    options_map = {"Pectoraux": chest_options, "Dos": back_options, "Jambes": leg_options, "Épaules": shoulder_options, "Abdos": abs_options, "Bras": arm_options}
    exercices_guide = options_map.get(guide_zone, [])
    if exercices_guide:
        for ex in exercices_guide:
            with st.expander(f"📖 {ex}"):
                gif_url = exercise_animations.get(ex)
                if gif_url:
                    st.image(gif_url, caption=f"Animation : {ex}", use_container_width=True)
                st.write(f"Voici comment réaliser correctement l\'exercice : **{ex}**.")
                st.info("💡 Conseil : Garde une forme stricte et contrôle la charge.")
                st.write("**🎥 Vidéo explicative :**")
                video_url = exercise_videos.get(ex, "https://www.youtube.com/watch?v=gRVjAtPip0Y" )
                st.video(video_url)

# --- ONGLET 4 : VISION IA ---
with tab4: 
    st.header("🎥 Vision IA")
    up = st.file_uploader("Upload", type=["mp4", "mov"])
    if up: st.video(up)

# --- ONGLET 5 : CALENDRIER / HISTORIQUE ---
with tab5:
    st.header("📅 Historique")
    d_cal = st.date_input("Consulter", date.today())
    df_g = pd.DataFrame(st.session_state.logs)
    if not df_g.empty:
        seance = df_g[df_g['Date'] == str(d_cal)]
        if not seance.empty: st.table(seance)
    st.text_area("Note du jour", value=st.session_state.notes_calendrier.get(str(d_cal), ""), key="note_hist")
