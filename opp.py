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
        "sex_field": "Sexe",
        "sex_options": ["Homme", "Femme", "Autre"],
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
        "sex_field": "Sex",
        "sex_options": ["Male", "Female", "Other"],
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
        "nom": "Athlète", "sexe": "Homme", "age": 25, "grandeur": "5'10",
        "objectif": "Prise de masse", "poids": 205, "blessures": "Aucune", "niveau": "Intermédiaire"
    }
if 'voice_zone' not in st.session_state: st.session_state.voice_zone = "Pectoraux"
if 'voice_exercice' not in st.session_state: st.session_state.voice_exercice = ""
if 'voice_poids' not in st.session_state: st.session_state.voice_poids = 135
if 'voice_reps' not in st.session_state: st.session_state.voice_reps = 8
if 'texte_vocal' not in st.session_state: st.session_state.texte_vocal = ""
if 'serie_zone' not in st.session_state: st.session_state.serie_zone = "Pectoraux"
if 'serie_exercice' not in st.session_state: st.session_state.serie_exercice = ""

chest_options = [
    "Développé couché", "Développé incliné", "Développé décliné",
    "Développé haltères", "Écarté couché", "Écarté incliné",
    "Pec deck (machine)", "Cross-over à la poulie", "Pompes",
    "Pompes inclinées", "Pompes déclinées", "Dips (buste penché)",
    "Pullover haltère", "Pullover à la poulie", "Machine chest press"
]
zones_disponibles = ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos"]

# ==========================================
# 4. FONCTION ANALYSE TEXTE VOCAL
# ==========================================
def analyser_texte_vocal(texte):
    prompt = f"""Extraire les infos de musculation du texte suivant : "{texte}". 
    Répondre UNIQUEMENT en JSON valide avec ces clés : zone, exercice, poids (nombre entier), reps (nombre entier).
    Zones possibles : Pectoraux, Dos, Jambes, Épaules, Abdos.
    Si l'exercice est pour les pectoraux, utilise un nom de cette liste : {chest_options}
    Exemple de réponse : {{"zone": "Pectoraux", "exercice": "Développé couché", "poids": 180, "reps": 10}}"""

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

    st.write(f"**{L['name_field']} :** {prof['nom']} | **{L['sex_field']} :** {prof['sexe']} | **{L['height_field']} :** {prof['grandeur']}")
    st.warning(f"🩹 **{L['inj_field']} :** {prof['blessures']}")

    st.divider()

    # OPTION MODIFIER LE PROFIL
    with st.expander(L["edit_prof"]):
        new_lang = st.selectbox(L["lang_label"], ["Français", "English"], index=0 if st.session_state.lang == "Français" else 1)
        if new_lang != st.session_state.lang:
            st.session_state.lang = new_lang
            st.rerun()
            
        with st.form("edit_profile_form_complete"):
            n = st.text_input(L["name_field"], value=prof["nom"])
            
            c_f1, c_f2 = st.columns(2)
            # Ajout du Sexe dans le formulaire
            s = c_f1.selectbox(L["sex_field"], L["sex_options"], index=L["sex_options"].index(prof["sexe"]) if prof["sexe"] in L["sex_options"] else 0)
            a = c_f2.number_input(L["age_field"], value=prof["age"])
            
            h = c_f1.text_input(L["height_field"], value=prof["grandeur"])
            p = c_f2.number_input(L["weight"], value=prof["poids"])
            
            obj = st.selectbox(L["obj_field"], L["goals"], index=L["goals"].index(prof["objectif"]))
            b = st.text_area(L["inj_field"], value=prof["blessures"])
            
            if st.form_submit_button(L["save"]):
                st.session_state.user_profile.update({
                    "nom": n, "sexe": s, "age": a, "grandeur": h, 
                    "poids": p, "objectif": obj, "blessures": b
                })
                st.rerun()

    # CALENDRIER VISUEL
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

# --- LE RESTE DU CODE (ONGLET 2 À 5) RESTE INCHANGÉ ---
# [ ... ]
