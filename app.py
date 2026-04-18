import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from datetime import timedelta
import time

def calcul_paie(role, revenus):
    if role in ["Admin"]:
        return revenus * 0.40
    return revenus * 0.25

def grade_auto(revenus, actions):
    if revenus > 150000 and actions > 20:
        return "Bras droit"
    elif revenus > 80000:
        return "Sicario confirmé"
    elif revenus > 30000:
        return "Sicario"
    else:
        return "Prospecto"

def statut_auto(actions):
    if actions < 10:
        return "⚠️ Sous pression"
    return "✔️ Actif"

# --- 1. CONFIGURATION ET CONSTANTES ---
st.set_page_config(page_title="La Niebla - FlashBack FA", page_icon="🥷", layout="wide")

DRUG_LIST = ["Marijuana", "Cocaine", "Meth", "Heroine", "Tranq", "Carte Prépayer", "B-magic", "Crack", "Autre"]

USERS = {
    "Admin": {"password": "0000", "pseudo": "El Patron"},
    "Alex": {"password": "Alx220717", "pseudo": "Alex Smith"},
    "Dany": {"password": "081219", "pseudo": "Dany Smith"},
    "Aziz": {"password": "asmith", "pseudo": "Aziz Smith"},
    "Alain": {"password": "999cww59", "pseudo": "Alain Bourdin"},
}

# --- 2. STYLE CSS ---
VIDEO_URL = "https://assets.mixkit.co/videos/preview/mixkit-mysterious-pale-fog-moving-slowly-over-the-ground-44130-large.mp4"

st.markdown(f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');

/* FOND */
.stApp {{
    background: transparent !important;
}}

body {{
    background-color: #0A0A0A;
    color: #EAEAEA;
    font-family: 'Orbitron', sans-serif;
}}

/* TITRE */
.gta-title {{
    font-size: 80px;
    text-align: center;
    color: #C9A85D;
    text-shadow: 0px 0px 25px rgba(201,168,93,0.6);
    margin-top: -60px;
    letter-spacing: 3px;
}}

/* SIDEBAR */
[data-testid="stSidebar"] {{
    background-color: rgba(10,10,10,0.95) !important;
    border-right: 1px solid #222;
}}

/* CARDS */
.card {{
    background: rgba(20,20,20,0.85);
    border: 1px solid #222;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 15px;
    box-shadow: 0px 0px 15px rgba(0,0,0,0.7);
}}

/* KPI */
.kpi {{
    font-size: 24px;
    font-weight: bold;
    color: #C9A85D;
}}

/* TEXTE FAIBLE */
.small {{
    font-size: 12px;
    color: #888;
}}

/* BOUTONS */
.stButton>button {{
    border-radius: 10px;
    border: 1px solid #C9A85D;
    background-color: transparent;
    color: #C9A85D;
    width: 100%;
}}

.stButton>button:hover {{
    background-color: #C9A85D;
    color: black;
}}

/* PROGRESS BAR */
div[data-testid="stProgressBar"] > div > div {{
    background-color: #C9A85D;
}}

/* FORMULAIRES */
.stForm {{
    background-color: rgba(15,15,15,0.9) !important;
    border-radius: 15px;
    border: 1px solid #222;
}}

</style>

<video autoplay loop muted playsinline id="bgVideo">
    <source src="{VIDEO_URL}" type="video/mp4">
</video>
""", unsafe_allow_html=True)

# --- 3. FONCTIONS SYSTÈME ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_now():
    return (datetime.datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")

if 'connected' not in st.session_state: st.session_state['connected'] = False
if "form_key" not in st.session_state: st.session_state.form_key = 0

def check_login():
    u = st.session_state.get("user_login")
    p = st.session_state.get("password_login")
    if u in USERS and USERS[u]["password"] == p:
        st.session_state['connected'] = True
        st.session_state['user_role'] = u
        st.session_state['user_pseudo'] = USERS[u]["pseudo"]
    else: st.error("Accès refusé.")

# --- 4. INTERFACE ---
if not st.session_state['connected']:
    st.write("<br><br><br>", unsafe_allow_html=True)
    st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        with st.form("login_form"):
            st.text_input("NOM DE CODE", key="user_login")
            st.text_input("MOT DE PASSE", type="password", key="password_login")
            if st.form_submit_button("S'INFILTRER"):
                check_login()
                if st.session_state['connected']: st.rerun()
else:
    with st.sidebar:
        st.write(f"### 🥷 {st.session_state['user_pseudo']}")
        menu = ["Tableau de bord"]
        if st.session_state['user_role'] == "Admin": 
            menu += ["Comptabilité Globale", "Archives de la Niebla"]
        choice = st.radio("Navigation", menu)
        if st.button("Déconnexion"):
            st.session_state.clear()
            st.rerun()

    df_full = conn.read(worksheet="Rapports", ttl=0)

    if choice == "Tableau de bord":
        st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

col1.markdown(f"""
<div class="card">
<div class="small">Total semaine</div>
<div class="kpi">...</div>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="card">
<div class="small">Caisse</div>
<div class="kpi">...</div>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="card">
<div class="small">Actifs</div>
<div class="kpi">...</div>
</div>
""", unsafe_allow_html=True)
        
        tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

        def handle_submit(action, butin=0, drogue="N/A", quantite=0):
            try:
                ts = get_now()
                df_rep = conn.read(worksheet="Rapports", ttl=0)
                df_treso = conn.read(worksheet="Tresorerie", ttl=0)
                new_rep = pd.DataFrame([{"Date": ts, "Membre": st.session_state['user_pseudo'], "Action": action, "Drogue": drogue, "Quantite": float(quantite), "Butin": float(butin)}])
                new_treso = pd.DataFrame([{"Date": ts, "Type": "Recette", "Etat": "Sale", "Catégorie": action, "Montant": float(butin), "Note": f"Rapport de {st.session_state['user_pseudo']}"}])
                conn.update(worksheet="Rapports", data=pd.concat([df_rep, new_rep], ignore_index=True))
                conn.update(worksheet="Tresorerie", data=pd.concat([df_treso, new_treso], ignore_index=True))
                st.success("Transmis !"); time.sleep(1); st.session_state.form_key += 1; st.rerun()
            except Exception as e: st.error(f"Erreur : {e}")

        with tabs[0]:
            with st.form(key=f"atm_{st.session_state.form_key}"):
                b = st.number_input("Butin ATM ($)", min_value=0)
                if st.form_submit_button("VALIDER"): handle_submit("ATM", butin=b)
        with tabs[1]:
            with st.form(key=f"sup_{st.session_state.form_key}"):
                b = st.number_input("Butin Supérette ($)", min_value=0)
                if st.form_submit_button("VALIDER"): handle_submit("Supérette", butin=b)
        with tabs[2]:
            with st.form(key=f"gf_{st.session_state.form_key}"):
                b = st.number_input("Butin Go Fast ($)", min_value=0)
                if st.form_submit_button("VALIDER"): handle_submit("Go Fast", butin=b)
        with tabs[3]:
            with st.form(key=f"cam_{st.session_state.form_key}"):
                if st.form_submit_button("VALIDER"): handle_submit("Cambriolage")
        with tabs[4]:
            with st.form(key=f"dr_{st.session_state.form_key}"):
                d_select = st.selectbox("Produit", DRUG_LIST)
                q = st.number_input("Quantité", min_value=0.0)
                b = st.number_input("Prix total ($)", min_value=0)
                if st.form_submit_button("VALIDER VENTE"): handle_submit("Drogue", butin=b, drogue=d_select, quantite=-abs(q))

        st.markdown("---")

        # --- OBJECTIFS (AVEC PRISE EN COMPTE DES AJUSTEMENTS GROUPÉS) ---
        st.write("### 📊 Objectifs de la Semaine")
        if not df_full.empty:
            df_stats = df_full.copy()
            df_stats['Date'] = pd.to_datetime(df_stats['Date'], dayfirst=True, errors='coerce')
            today = datetime.datetime.now()
            start_week = (today - timedelta(days=today.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            
            week_data = df_stats[
                (df_stats['Date'] >= start_week) & 
                (~df_stats['Action'].str.contains(r'\[LOG\]', na=False, case=False))
            ]
            
            for p_id, p_info in USERS.items():
                ps = p_info["pseudo"]
                u_data = week_data[week_data['Membre'] == ps]
                
                # Calcul des actions : Actions classiques (count) + Ajustements (somme de la colonne Quantite pour les actions)
                normal_actions = len(u_data[(u_data['Action'] != "Drogue") & (~u_data['Action'].str.contains("Ajustement", na=False))])
                adj_actions = u_data[u_data['Action'] == "Ajustement Action"]["Quantite"].sum()
                total_actions = int(normal_actions + adj_actions)
                
                # Calcul des ventes : Drogue classique + Ajustement Ventes
                total_ventes = abs(u_data[u_data['Action'].str.contains("Drogue|Ventes", case=False, na=False)]['Quantite'].sum())
                
                c1, c2, c3 = st.columns([1, 2, 2])
                c1.write(f"**{ps}**")
                c2.progress(min(float(total_actions)/20, 1.0), text=f"Actions: {total_actions}/20")
                c3.progress(min(float(total_ventes)/300, 1.0), text=f"Ventes: {int(total_ventes)}/300")
        else: st.info("Aucune donnée.")

        st.markdown("---")

        st.write("### 🕒 Mes 3 dernières activités")
        if not df_full.empty:
            mes_actions = df_full[
                (df_full['Membre'] == st.session_state['user_pseudo']) & 
                (~df_full['Action'].str.contains(r'\[LOG\]', na=False, case=False))
            ].tail(3).iloc[::-1].copy()
            if not mes_actions.empty:
                mes_actions['Butin'] = mes_actions['Butin'].apply(lambda x: f"{int(float(x)):,} $".replace(',', ' '))
                st.table(mes_actions[['Date', 'Action', 'Butin']])
            else: st.info("Aucune action récente.")

    elif choice == "Archives de la Niebla":
        st.markdown('<div class="gta-title">Archives</div>', unsafe_allow_html=True)
        st.dataframe(df_full.sort_index(ascending=False), use_container_width=True)

    elif choice == "Comptabilité Globale":
        st.markdown('<div class="gta-title">Gestion Admin</div>', unsafe_allow_html=True)
        
        # --- AJUSTEMENT MANUEL AMÉLIORÉ ---
        with st.expander("🛠️ CORRIGER/AJOUTER DES OBJECTIFS (Saisie groupée)"):
            with st.form("adj_manual_bulk"):
                # On inclut tout le monde y compris El Patron
                target_user = st.selectbox("Membre à créditer", [u["pseudo"] for u in USERS.values()])
                adj_type = st.radio("Type de crédit", ["Actions (Cambriolages, ATM...)", "Ventes de Drogue"])
                
                adj_val = st.number_input("Nombre d'actions ou Quantité de drogue à ajouter", min_value=1, step=1)
                
                if st.form_submit_button("APPLIQUER LE CRÉDIT"):
                    try:
                        ts = get_now()
                        if adj_type == "Actions (Cambriolages, ATM...)":
                            name = "Ajustement Action"
                            q_to_save = float(adj_val) # On stocke le nombre d'actions dans Quantite
                        else:
                            name = "Ajustement Ventes"
                            q_to_save = -float(adj_val) # On stocke en négatif comme pour les ventes réelles
                            
                        df_r = conn.read(worksheet="Rapports", ttl=0)
                        new_line = pd.DataFrame([{"Date": ts, "Membre": target_user, "Action": name, "Drogue": "N/A", "Quantite": q_to_save, "Butin": 0}])
                        conn.update(worksheet="Rapports", data=pd.concat([df_r, new_line], ignore_index=True))
                        st.success(f"Ajout de {adj_val} au compteur de {target_user} terminé !"); time.sleep(1); st.rerun()
                    except Exception as e: st.error(e)

        st.markdown("---")

        with st.expander("➕ Opération financière manuelle"):
            with st.form("man_fin"):
                c_a, c_b = st.columns(2)
                m_t = c_a.selectbox("Type", ["Recette", "Dépense"])
                m_e = c_b.selectbox("État", ["Sale", "Propre"])
                m_c = st.text_input("Catégorie")
                m_v = st.number_input("Montant ($)", min_value=0)
                if st.form_submit_button("VALIDER FINANCES"):
                    try:
                        df_t = conn.read(worksheet="Tresorerie", ttl=0)
                        nl = pd.DataFrame([{"Date": get_now(), "Type": m_t, "Etat": m_e, "Catégorie": m_c, "Montant": float(m_v), "Note": f"Admin: {st.session_state['user_pseudo']}"}])
                        conn.update(worksheet="Tresorerie", data=pd.concat([df_t, nl], ignore_index=True))
                        st.success("Enregistré !"); time.sleep(1); st.rerun()
                    except Exception as e: st.error(e)

        df_v = conn.read(worksheet="Tresorerie", ttl=0)
        if not df_v.empty:
            def calc(df, et):
                sub = df[df['Etat'] == et]
                return sub[sub['Type'] == 'Recette']['Montant'].sum() - sub[sub['Type'] == 'Dépense']['Montant'].sum()
            sp, ss = calc(df_v, 'Propre'), calc(df_v, 'Sale')
            c1, c2, c3 = st.columns(3)
            c1.metric("PROPRE", f"{int(sp):,} $".replace(',', ' '))
            c2.metric("SALE", f"{int(ss):,} $".replace(',', ' '))
            c3.metric("TOTAL", f"{int(sp+ss):,} $".replace(',', ' '))
            st.dataframe(df_v.sort_index(ascending=False), use_container_width=True)
