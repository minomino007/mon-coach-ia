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
        "voice_instruction": "🎙️ Clique sur le bouton micro, parle, et les champs se remplissent tout seuls !"
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
        "voice_instruction": "🎙️ Click the mic button, speak, and fields fill automatically!"
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

# Dictionnaire des GIFs par exercice
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

    # 🎙️ BOUTON MICRO NAVIGATEUR
    st.components.v1.html("""
        <style>
            #mic-btn {
                background-color: #ff4b4b;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 16px;
                border-radius: 8px;
                cursor: pointer;
                margin-bottom: 10px;
            }
            #mic-btn:hover { background-color: #cc0000; }
            #result-box {
                margin-top: 10px;
                padding: 10px;
                background: #1e1e1e;
                color: #00ff88;
                border-radius: 8px;
                font-size: 15px;
                min-height: 40px;
            }
        </style>
        <button id="mic-btn" onclick="startListening()">🎙️ Parler</button>
        <div id="result-box">En attente...</div>
        <script>
        function startListening() {
            const btn = document.getElementById('mic-btn');
            const box = document.getElementById('result-box');
            btn.textContent = '🔴 Écoute en cours...';
            btn.style.backgroundColor = '#888';
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'fr-FR';
            recognition.interimResults = false;
            recognition.onresult = function(event) {
                const texte = event.results[0][0].transcript;
                box.textContent = '✅ Entendu : ' + texte;
                btn.textContent = '🎙️ Parler';
                btn.style.backgroundColor = '#ff4b4b';
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: texte}, '*');
            };
            recognition.onerror = function(e) {
                box.textContent = '❌ Erreur : ' + e.error;
                btn.textContent = '🎙️ Parler';
                btn.style.backgroundColor = '#ff4b4b';
            };
            recognition.start();
        }
        </script>
    """, height=120)

    # Champ texte + bouton analyser
    st.write("**Ou écris ta séance directement ici :**")
    texte_input = st.text_input(
        "Ex: Pectoraux, développé couché, 180 lbs, 10 reps",
        value=st.session_state.texte_vocal,
        key="texte_vocal_input"
    )

    if st.button("🤖 Analyser", type="primary"):
        if texte_input:
            try:
                with st.spinner("L'IA analyse..."):
                    data = analyser_texte_vocal(texte_input)
                    zone_detectee = data.get("zone", "Pectoraux")
                    if zone_detectee in zones_disponibles:
                        st.session_state.voice_zone = zone_detectee
                        st.session_state.serie_zone = zone_detectee
                    st.session_state.voice_exercice = data.get("exercice", "")
                    st.session_state.serie_exercice = data.get("exercice", "")
                    st.session_state.voice_poids = int(data.get("poids", 135))
                    st.session_state.voice_reps = int(data.get("reps", 8))
                    st.success(f"✅ Zone : **{st.session_state.voice_zone}** | Exercice : **{st.session_state.voice_exercice}** | Poids : **{st.session_state.voice_poids} lbs** | Reps : **{st.session_state.voice_reps}**")
                    st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")

    st.divider()
    date_seance = st.date_input(L["date_label"], date.today(), key="date_input_workout")

    # ✅ ÉTAPE 1 — Choisir la zone et l'exercice UNE SEULE FOIS
    st.subheader("📌 Étape 1 — Choisir l'exercice")
    col_z, col_e = st.columns(2)

    with col_z:
        zone_index = zones_disponibles.index(st.session_state.serie_zone) if st.session_state.serie_zone in zones_disponibles else 0
        serie_zone = st.selectbox(L["zone_label"], zones_disponibles, index=zone_index, key="select_zone_serie")

    with col_e:
        if serie_zone == "Pectoraux":
            ex_index = chest_options.index(st.session_state.serie_exercice) if st.session_state.serie_exercice in chest_options else 0
            serie_exercice = st.selectbox(L["ex_label"], chest_options, index=ex_index, key="select_ex_serie")
        else:
            serie_exercice = st.text_input(L["ex_label"], value=st.session_state.serie_exercice, key="input_ex_serie")

    # Sauvegarder la zone et exercice choisis
    st.session_state.serie_zone = serie_zone
    st.session_state.serie_exercice = serie_exercice

    st.divider()

    # ✅ ÉTAPE 2 — Ajouter les séries une par une
    st.subheader("📋 Étape 2 — Ajouter tes séries")

    # Afficher les séries déjà ajoutées pour cet exercice
    series_actuelles = [s for s in st.session_state.temp_workout if s["Exercice"] == serie_exercice]
    if series_actuelles:
        for i, s in enumerate(series_actuelles):
            st.write(f"✅ **Série {i+1}** — {s['Poids']} lbs × {s['Reps']} reps")

    # Formulaire pour ajouter UNE série
    num_serie = len(series_actuelles) + 1
    st.write(f"**➕ Série {num_serie} :**")

    with st.form(f"serie_form_{num_serie}", clear_on_submit=True):
        col_w, col_r = st.columns(2)
        w_input = col_w.number_input(L["weight"], value=st.session_state.voice_poids, key=f"w_{num_serie}")
        r_input = col_r.number_input(L["reps"], value=st.session_state.voice_reps, key=f"r_{num_serie}")

        if st.form_submit_button(f"➕ Ajouter Série {num_serie}"):
            st.session_state.temp_workout.append({
                "Date": str(date_seance),
                "Zone": st.session_state.serie_zone,
                "Exercice": st.session_state.serie_exercice,
                "Série": num_serie,
                "Poids": w_input,
                "Reps": r_input
            })
            st.rerun()

    st.divider()

    # ✅ RÉSUMÉ COMPLET DE LA SÉANCE — toujours visible, groupé par exercice
    if st.session_state.temp_workout:
        st.subheader("📊 Ta séance complète")

        # Grouper les séries par exercice
        exercices_faits = {}
        for s in st.session_state.temp_workout:
            nom_ex = s["Exercice"]
            if nom_ex not in exercices_faits:
                exercices_faits[nom_ex] = []
            exercices_faits[nom_ex].append(s)

        # Afficher chaque exercice avec ses séries
        for nom_ex, series in exercices_faits.items():
            zone_ex = series[0]["Zone"]
            st.markdown(f"**💪 {nom_ex}** — *{zone_ex}*")
            for i, s in enumerate(series):
                st.write(f"　　Série {i+1} : {s['Poids']} lbs × {s['Reps']} reps")
            st.write("")

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

# --- ONGLET 3 : GUIDE ---
with tab3:
    st.header("👤 Guide Technique")
    st.write("Sélectionne une zone pour voir les exercices avec animations et vidéos.")

    guide_zone = st.selectbox("Choisir une zone", zones_disponibles, key="guide_zone_select")
    zone_to_options = {
        "Pectoraux": chest_options,
        "Dos": back_options,
        "Jambes": leg_options,
        "Épaules": shoulder_options,
        "Abdos": abs_options,
        "Bras": arm_options
    }
    exercices_guide = zone_to_options.get(guide_zone, chest_options)

    for ex in exercices_guide:
        with st.expander(f"📖 {ex}"):
            gif = exercise_animations.get(ex)
            if gif:
                st.image(gif, caption=f"Animation : {ex}")
            st.info("💡 Conseil : Garde une forme stricte et contrôle la charge.")

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
            st.table(seance_du_jour[["Zone", "Exercice", "Série", "Poids", "Reps"]])

    st.divider()
    n_cal = st.text_area("Note du jour", value=st.session_state.notes_calendrier.get(str(d_cal), ""))
    if st.button(L["save"], key="save_note_calendar"):
        st.session_state.notes_calendrier[str(d_cal)] = n_cal
        st.success("Note enregistrée !")
