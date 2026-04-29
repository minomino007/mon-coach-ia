import streamlit as st
import pandas as pd
from datetime import date
import openai
from streamlit_mic_recorder import mic_recorder
import json

# ==========================================
# 1. CONFIGURATION DE LA PAGE & SECRETS
# ==========================================
st.set_page_config(
    page_title="Gym AI Agent PRO",
    layout="centered",
    page_icon="🏋️",
    initial_sidebar_state="collapsed"
)

# Initialisation du client OpenAI avec ta clé sécurisée (Secrets Streamlit)
if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("⚠️ Erreur : La clé OPENAI_API_KEY est introuvable dans les Secrets de Streamlit.")

# ==========================================
# 2. SYSTÈME DE TRADUCTION COMPLET
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
# 3. INITIALISATION DE LA MÉMOIRE (SESSION STATE)
# ==========================================
if 'lang' not in st.session_state: st.session_state.lang = "Français"
if 'logs' not in st.session_state: st.session_state.logs = [] 
if 'notes_calendrier' not in st.session_state: st.session_state.notes_calendrier = {}
if 'temp_workout' not in st.session_state: st.session_state.temp_workout = []
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "nom": "Athlète", 
        "age": 25, 
        "grandeur": "5'10",
        "objectif": "Prise de masse", 
        "poids": 205, 
        "blessures": "Aucune", 
        "niveau": "Intermédiaire"
    }

# Liste des exercices pour aider l'IA à choisir le bon terme
chest_options = [
    "Développé couché", "Développé incliné", "Développé décliné", 
    "Développé haltères", "Écarté couché", "Écarté incliné", 
    "Pec deck (machine)", "Cross-over à la poulie", "Pompes", 
    "Pompes inclinées", "Pompes déclinées", "Dips (buste penché)", 
    "Pullover haltère", "Pullover à la poulie", "Machine chest press"
]

# ==========================================
# 4. FONCTION INTELLIGENTE (VOCAL -> DONNÉES)
# ==========================================
def extraire_donnees_seance(audio_bytes):
    # Sauvegarde temporaire du fichier audio pour l'IA
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_bytes)
    
    # Étape 1 : Transcription (Audio vers Texte) via Whisper
    with open("temp_audio.wav", "rb") as audio_file:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        texte = transcript.text

    # Étape 2 : Extraction structurée (Texte vers JSON) via GPT-3.5
    prompt = f"""
    Analyse ce texte de musculation : "{texte}".
    Tu dois extraire les informations et répondre UNIQUEMENT avec un objet JSON.
    Format attendu : {{"zone": "string", "exercice": "string", "poids": nombre, "reps": nombre}}
    Zones autorisées : Pectoraux, Dos, Jambes, Épaules, Abdos.
    Si l'exercice concerne les pectoraux, choisis impérativement le nom le plus proche dans cette liste : {chest_options}
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Tu es un assistant de gym expert en extraction de données."},
                  {"role": "user", "content": prompt}]
    )
    return json.loads(response.choices[0].message.content), texte

# Chargement de la langue active
L = languages[st.session_state.lang]

# ==========================================
# 5. INTERFACE UTILISATEUR (ONGLETS)
# ==========================================
st.title("🤖 Mon Gym AI Agent")

tab1, tab2, tab3, tab4, tab5 = st.tabs(L["tabs"])

# --- ONGLET 1 : PROFIL COMPLET ---
with tab1:
    st.header(L["prof_header"])
    
    # Changement de langue
    new_lang = st.selectbox(L["lang_label"], ["Français", "English"], index=0 if st.session_state.lang == "Français" else 1)
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

    prof = st.session_state.user_profile
    
    # Affichage des statistiques du profil
    col_p1, col_p2, col_p3 = st.columns(3)
    col_p1.metric(L["weight"], f"{prof['poids']} lbs")
    col_p2.metric(L["obj_field"], prof['objectif'])
    col_p3.metric(L["age_field"], f"{prof['age']} ans")

    st.info(f"**Nom :** {prof['nom']}  \n**Taille :** {prof['grandeur']}  \n**Blessures/Notes :** {prof['blessures']}")

    # Formulaire de modification (Expander)
    with st.expander(L["edit_prof"]):
        with st.form("form_edit_full_profil"):
            nom_edit = st.text_input(L["name_field"], value=prof["nom"])
            c1, c2 = st.columns(2)
            age_edit = c1.number_input(L["age_field"], value=prof["age"])
            taille_edit = c2.text_input(L["height_field"], value=prof["grandeur"])
            poids_edit = c1.number_input(L["weight"], value=prof["poids"])
            obj_edit = c2.selectbox(L["obj_field"], L["goals"], index=L["goals"].index(prof["objectif"]))
            blessures_edit = st.text_area(L["inj_field"], value=prof["blessures"])
            
            if st.form_submit_button(L["save"]):
                st.session_state.user_profile.update({
                    "nom": nom_edit, "age": age_edit, "grandeur": taille_edit, 
                    "poids": poids_edit, "objectif": obj_edit, "blessures": blessures_edit
                })
                st.success("Profil mis à jour !")
                st.rerun()

# --- ONGLET 2 : SÉANCE DU JOUR (AVEC VOCAL INTELLIGENT) ---
with tab2:
    st.header(L["workout_header"])
    
    # SECTION VOCALE
    st.write(L["voice_instruction"])
    audio_record = mic_recorder(
        start_prompt="🔴 Commencer l'enregistrement",
        stop_prompt="🟢 Analyser ma séance",
        key="gym_mic_pro_final"
    )

    if audio_record:
        try:
            with st.spinner("L'IA analyse votre voix..."):
                extracted, original_text = extraire_donnees_seance(audio_record['bytes'])
                
                # Ajout automatique des données extraites à la liste temporaire
                st.session_state.temp_workout.append({
                    "Date": str(date.today()), 
                    "Zone": extracted.get("zone", "Pectoraux"), 
                    "Exercice": extracted.get("exercice", "Inconnu"), 
                    "Poids": extracted.get("poids", 0), 
                    "Reps": extracted.get("reps", 0)
                })
                st.success(f"Compris : '{original_text}'")
        except Exception as e:
            st.error(f"Erreur d'analyse : {e}")

    st.divider()
    
    # FORMULAIRE MANUEL
    d_workout = st.date_input(L["date_label"], date.today(), key="manual_date_picker")
    with st.form("manual_workout_form", clear_on_submit=True):
        z_manual = st.selectbox(L["zone_label"], ["Pectoraux", "Dos", "Jambes", "Épaules", "Abdos"])
        ex_manual = st.selectbox(L["ex_label"], chest_options) if z_manual == "Pectoraux" else st.text_input(L["ex_label"])
        cw, cr = st.columns(2)
        w_manual = cw.number_input(L["weight"], value=135)
        r_manual = cr.number_input(L["reps"], value=8)
        
        if st.form_submit_button(L["add_set"]):
            st.session_state.temp_workout.append({
                "Date": str(d_workout), "Zone": z_manual, "Exercice": ex_manual, "Poids": w_manual, "Reps": r_manual
            })

    # AFFICHAGE ET VALIDATION DE LA SÉANCE
    if st.session_state.temp_workout:
        st.subheader("Séries en attente")
        st.dataframe(pd.DataFrame(st.session_state.temp_workout), use_container_width=True)
        v1, v2 = st.columns(2)
        if v1.button(L["validate"], type="primary"):
            st.session_state.logs.extend(st.session_state.temp_workout)
            st.session_state.temp_workout = []
            st.success("Entraînement enregistré dans l'historique !")
            st.balloons()
        if v2.button(L["clear"]):
            st.session_state.temp_workout = []
            st.rerun()

# --- ONGLET 3 : GUIDE D'EXÉCUTION ---
with tab3:
    st.header("👤 Guide Technique")
    st.write("Visionnez les bonnes pratiques pour vos exercices.")
    if st.button("Démonstration : Développé Couché"):
        st.video("https://www.youtube.com/watch?v=gRVjAtPip0Y")

# --- ONGLET 4 : VISION IA ---
with tab4:
    st.header("🎥 Vision IA")
    st.write("Téléchargez une vidéo pour analyser votre forme (Fonctionnalité en cours).")
    vid = st.file_uploader("Upload vidéo", type=["mp4", "mov"])
    if vid:
        st.video(vid)

# --- ONGLET 5 : CALENDRIER & HISTORIQUE ---
with tab5:
    st.header("📅 Historique Complet")
    cal_date = st.date_input("Choisir une date", date.today(), key="calendar_view")
    
    # Affichage des données enregistrées
    df_logs = pd.DataFrame(st.session_state.logs)
    if not df_logs.empty:
        filtered_data = df_logs[df_logs['Date'] == str(cal_date)]
        if not filtered_data.empty:
            st.success(f"Séance du {cal_date}")
            st.table(filtered_data[["Zone", "Exercice", "Poids", "Reps"]])
        else:
            st.info("Aucun entraînement trouvé pour cette date.")
    else:
        st.info("L'historique est vide pour le moment.")

    # Notes de l'historique
    st.divider()
    st.subheader("📝 Notes de séance")
    note_val = st.session_state.notes_calendrier.get(str(cal_date), "")
    note_input = st.text_area("Vos remarques sur cette journée...", value=note_val)
    if st.button("Enregistrer la note", key="btn_save_note"):
        st.session_state.notes_calendrier[str(cal_date)] = note_input
        st.success("Note sauvegardée !")
