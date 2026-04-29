import streamlit as st
import pandas as pd
from datetime import date
import openai
from streamlit_mic_recorder import mic_recorder
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
        "add_set": "➕ Ajouter la série",
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
        "voice_instruction": "🎙️ **Commande Vocale** : Dis 'Pectoraux, développé couché, 180 lbs, 10 reps'."
    },
    "English": {
        "tabs": ["📊 Profile", "🏋️ Today's Workout", "👤 Guide", "🎥 Vision", "📅 Calendar"],
        "prof_header": "👤 Your Fitness Profile",
        "edit_prof": "Edit Profile",
        "save": "Save",
        "workout_header": "🏋️ Log a Workout",
        "add_set": "➕ Add Set",
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
        "voice_instruction": "🎙️ **Voice Command**: Say 'Chest, bench press, 180 lbs, 10 reps'."
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

# ✅ NOUVEAU : mémoire pour les champs pré-remplis par la voix
if 'voice_zone' not in st.session_state: st.session_state.voice_zone = "Pectoraux"
if 'voice_exercice' not in st.session_state: st.session_state.voice_exercice = ""
if 'voice_poids' not in st.session_state: st.session_state.voice_poids = 135
if 'voice_reps' not in st.session_state: st.session_state.voice_reps = 8
if 'voice_ready' not in st.session_state: st.session_state.voice_ready = False

chest_options = [
    "Développé couché", "Développé incliné", "Développé décliné",
    "Développé haltères", "Écarté couché", "Écarté incliné",
    "Pec deck (machine)", "Cross-over à la poulie", "Pompes",
    "Pompes inclinées", "Pompes déclinées", "Dips (buste penché)",
    "Pullover haltère", "Pullover à la poulie", "Machine chest press"
]

zones_disponibles = ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos"]

# ==========================================
# 4. FONCTION ANALYSE VOCALE
# ==========================================
def extraire_donnees_seance(audio_bytes):
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_bytes)

    with open("temp_audio.wav", "rb") as audio_file:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        texte = transcript.text

    prompt = f"""Extraire les infos de musculation du texte suivant : "{texte}". 
    Répondre UNIQUEMENT en JSON avec ces clés : zone, exercice, poids (nombre), reps (nombre).
    Zones possibles : Pectoraux, Dos, Jambes, Épaules, Abdos.
    Si l'exercice est pour les pectoraux, utilise un nom de cette liste : {chest_options}"""

    response = client.chat.completions.create(
        model="openai/gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.choices[0].message.content), texte

L = languages[st.session_state.lang]

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
            obj = c_f2.selectbox(L["obj_field"], L["goals"], index=L["goals"].index(prof["objectif"]))
            b = st.text_area(L["inj_field"], value=prof["blessures"])
            if st.form_submit_button(L["save"]):
                st.session_state.user_profile.update({"nom": n, "age": a, "grandeur": h, "poids": p, "objectif": obj, "blessures": b})
                st.rerun()

# --- ONGLET 2 : SÉANCE DU JOUR ---
with tab2:
    st.header(L["workout_header"])
    st.write(L["voice_instruction"])

    # 🎙️ Microphone
    audio_record = mic_recorder(
        start_prompt="🔴 Commencer l'enregistrement",
        stop_prompt="🟢 Analyser ma séance",
        key="gym_mic_final_v4"
    )

    # ✅ NOUVEAU : après analyse vocale, on remplit les champs automatiquement
    if audio_record:
        try:
            with st.spinner("L'IA analyse votre voix..."):
                data, texte_brut = extraire_donnees_seance(audio_record['bytes'])

                # On sauvegarde les valeurs détectées dans la mémoire
                zone_detectee = data.get("zone", "Pectoraux")
                if zone_detectee in zones_disponibles:
                    st.session_state.voice_zone = zone_detectee
                st.session_state.voice_exercice = data.get("exercice", "")
                st.session_state.voice_poids = int(data.get("poids", 135))
                st.session_state.voice_reps = int(data.get("reps", 8))
                st.session_state.voice_ready = True

                st.success(f"✅ Entendu : *{texte_brut}*")
                st.info(f"🎯 Détecté → Zone : **{st.session_state.voice_zone}** | Exercice : **{st.session_state.voice_exercice}** | Poids : **{st.session_state.voice_poids} lbs** | Reps : **{st.session_state.voice_reps}**")

        except Exception as e:
            st.error(f"Erreur d'analyse : {e}")

    st.divider()
    date_seance = st.date_input(L["date_label"], date.today(), key="date_input_workout")

    # ✅ NOUVEAU : le formulaire utilise les valeurs vocales si disponibles
    with st.form("add_set_form_final", clear_on_submit=True):

        # Zone : pré-sélectionnée par la voix
        zone_index = zones_disponibles.index(st.session_state.voice_zone) if st.session_state.voice_zone in zones_disponibles else 0
        zone = st.selectbox(L["zone_label"], zones_disponibles, index=zone_index)

        # Exercice : pré-rempli par la voix
        if zone == "Pectoraux":
            ex_index = chest_options.index(st.session_state.voice_exercice) if st.session_state.voice_exercice in chest_options else 0
            ex = st.selectbox(L["ex_label"], chest_options, index=ex_index)
        else:
            ex = st.text_input(L["ex_label"], value=st.session_state.voice_exercice)

        # Poids et Reps : pré-remplis par la voix
        col_w, col_r = st.columns(2)
        w_input = col_w.number_input(L["weight"], value=st.session_state.voice_poids)
        r_input = col_r.number_input(L["reps"], value=st.session_state.voice_reps)

        if st.form_submit_button(L["add_set"]):
            st.session_state.temp_workout.append({
                "Date": str(date_seance),
                "Zone": zone,
                "Exercice": ex,
                "Poids": w_input,
                "Reps": r_input
            })
            # On remet à zéro les valeurs vocales après ajout
            st.session_state.voice_ready = False
            st.rerun()

    # Liste des séries en attente
    if st.session_state.temp_workout:
        st.subheader("Séries temporaires")
        st.dataframe(pd.DataFrame(st.session_state.temp_workout), use_container_width=True)
        cb1, cb2 = st.columns(2)
        if cb1.button(L["validate"], type="primary"):
            st.session_state.logs.extend(st.session_state.temp_workout)
            st.session_state.temp_workout = []
            st.success("Enregistré avec succès !")
            st.balloons()
        if cb2.button(L["clear"]):
            st.session_state.temp_workout = []
            st.rerun()

# --- ONGLET 3 : GUIDE ---
with tab3:
    st.header("👤 Guide Technique")
    st.video("https://www.youtube.com/watch?v=gRVjAtPip0Y")

# --- ONGLET 4 : VISION ---
with tab4:
    st.header("🎥 Vision IA")
    up = st.file_uploader("Upload vidéo", type=["mp4", "mov"])
    if up: st.video(up)

# --- ONGLET 5 : CALENDRIER ---
with tab5:
    st.header("📅 Historique")
    d_cal = st.date_input("Consulter une date", date.today(), key="calendar_date_view")
    df_global = pd.DataFrame(st.session_state.logs)
    if not df_global.empty:
        seance_du_jour = df_global[df_global['Date'] == str(d_cal)]
        if not seance_du_jour.empty:
            st.table(seance_du_jour[["Zone", "Exercice", "Poids", "Reps"]])

    st.divider()
    n_cal = st.text_area("Note du jour", value=st.session_state.notes_calendrier.get(str(d_cal), ""))
    if st.button(L["save"], key="save_note_calendar"):
        st.session_state.notes_calendrier[str(d_cal)] = n_cal
        st.success("Note enregistrée !")
