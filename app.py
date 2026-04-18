import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from datetime import timedelta
import time

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="La Niebla - Luxury Cartel",
    page_icon="⚜️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. BASE DE DONNÉES UTILISATEURS & RÔLES ---
# Roles: 1: Gérant (⚜️), 2: Lieutenant (⭐), 3: Soldat (🔫)
USERS = {
    "Admin": {"password": "0000", "pseudo": "El Patron", "role_level": 1},
    "Alex": {"password": "Alx220717", "pseudo": "Alex Smith", "role_level": 2},
    "Dany": {"password": "081219", "pseudo": "Dany Smith", "role_level": 3},
    "Aziz": {"password": "asmith", "pseudo": "Aziz Smith", "role_level": 3},
    "Alain": {"password": "999cww59", "pseudo": "Alain Bourdin", "role_level": 3},
}

DRUG_LIST = ["Marijuana", "Cocaine", "Meth", "Heroine", "Tranq", "Carte Prépayer", "B-magic", "Crack", "Autre"]

# --- 3. STYLE CSS AVANCÉ (LUXURY CARTEL) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&family=Marcellus&display=swap');
    
    .stApp {{
        background: url('https://w0.peakpx.com/wallpaper/70/463/wallpaper-dark-grey-textured-dark-grey-background-textured-background.jpg');
        background-size: cover;
        background-attachment: fixed;
    }}
    
    /* Header et Sidebar transparents */
    header, [data-testid="stSidebarHeader"], [data-testid="stHeader"] {{ background: transparent !important; }}
    
    /* Titres et Textes en Or/Gris */
    h1, h2, h3, h4, p, label, .stMarkdown, [data-testid="stWidgetLabel"] {{
        color: #f7e0a3 !important;
        font-family: 'Marcellus', serif !important;
    }}
    
    .gta-title {{
        font-family: 'UnifrakturMaguntia', cursive;
        font-size: 100px;
        color: transparent;
        background-image: linear-gradient(to bottom, #f7e0a3, #b48c3e, #f7e0a3);
        -webkit-background-clip: text;
        background-clip: text;
        text-align: center;
        text-shadow: 0px 4px 15px rgba(180, 140, 62, 0.4);
        margin-top: -50px;
        margin-bottom: 10px;
        letter-spacing: 5px;
    }}
    
    .gta-slogan {{
        font-family: 'Marcellus', serif;
        font-size: 20px;
        color: #a6a6a6 !important;
        text-align: center;
        margin-bottom: 40px;
        font-style: italic;
    }}

    /* Formulaires et Inputs */
    .stForm {{
        background-color: rgba(10, 10, 10, 0.85) !important;
        border: 1px solid #b48c3e !important;
        border-radius: 8px;
    }}
    
    .stTextInput>div>div>input, .stNumberInput>div>div>input {{
        background-color: #1a1a1a !important;
        color: #f7e0a3 !important;
        border: 1px solid #444 !important;
    }}

    /* Barre de progression Or */
    .stProgress > div > div > div > div {{
        background-image: linear-gradient(to right, #b48c3e, #f7e0a3) !important;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: rgba(15, 15, 15, 0.98) !important;
        border-right: 1px solid #b48c3e;
    }}
    
    /* Metrics */
    [data-testid="stMetricValue"] {{
        color: #f7e0a3 !important;
        font-family: 'Marcellus', serif;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. INITIALISATION ET FONCTIONS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_now():
    return (datetime.datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")

if 'connected' not in st.session_state:
    st.session_state['connected'] = False

# --- 5. ÉCRAN DE CONNEXION ---
if not st.session_state['connected']:
    st.write("<br><br><br>", unsafe_allow_html=True)
    st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
    st.markdown('<div class="gta-slogan">On ne nous voit pas... mais on est partout.</div>', unsafe_allow_html=True)
    
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        with st.form("login_form"):
            user_input = st.text_input("NOM DE CODE")
            pass_input = st.text_input("MOT DE PASSE", type="password")
            if st.form_submit_button("S'INFILTRER"):
                if user_input in USERS and USERS[user_input]["password"] == pass_input:
                    st.session_state['connected'] = True
                    st.session_state['user_id'] = user_input
                    st.session_state['user_pseudo'] = USERS[user_input]["pseudo"]
                    st.session_state['role_level'] = USERS[user_input]["role_level"]
                    st.rerun()
                else:
                    st.error("Accès refusé.")

# --- 6. INTERFACE PRINCIPALE ---
else:
    # Récupération sécurisée des infos de session pour éviter KeyError
    u_pseudo = st.session_state.get('user_pseudo', 'Soldado')
    u_role_lv = st.session_state.get('role_level', 3)

   # Sidebar Navigation
    with st.sidebar:
        # On récupère le niveau de rôle
        u_role_lv = st.session_state.get('role_level', 3)
        u_pseudo = st.session_state.get('user_pseudo', 'Soldado')

        # Logique d'affichage des grades
        if u_role_lv == 1:
            icon, r_name = "⚜️", "El Patron"
        elif u_role_lv == 2:
            icon, r_name = "⭐", "Lieutenant"
        else:
            icon, r_name = "🔫", "Sicario"
        
        st.write(f"### {u_pseudo} {icon}")
        st.write(f"**Rang :** {r_name}")
        st.write("---")
        
        # Menu dynamique selon le rôle
        menu = ["Tableau de bord"]
        if u_role_lv <= 2:
            menu += ["Comptabilité Globale", "Archives de la Niebla"]
            
        choice = st.sidebar.radio("Navigation", menu)
        
        st.write("---")
        if st.sidebar.button("Se déconnecter"):
            st.session_state.clear()
            st.rerun()
            
    # Lecture des données
    df_full = conn.read(worksheet="Rapports", ttl=0)

    if choice == "Tableau de bord":
        st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
        st.markdown('<div class="gta-slogan">On ne nous voit pas... mais on est partout.</div>', unsafe_allow_html=True)
        
        # --- SAISIE ACTIVITÉ ---
        tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

        def submit_op(action, butin=0, drogue="N/A", qte=0):
            try:
                ts = get_now()
                # Enregistrement Rapport
                df_rep = conn.read(worksheet="Rapports", ttl=0)
                new_rep = pd.DataFrame([{"Date": ts, "Membre": u_pseudo, "Action": action, "Drogue": drogue, "Quantite": float(qte), "Butin": float(butin)}])
                conn.update(worksheet="Rapports", data=pd.concat([df_rep, new_rep], ignore_index=True))
                # Enregistrement Trésorerie
                df_treso = conn.read(worksheet="Tresorerie", ttl=0)
                new_treso = pd.DataFrame([{"Date": ts, "Type": "Recette", "Etat": "Sale", "Catégorie": action, "Montant": float(butin), "Note": f"Par {u_pseudo}"}])
                conn.update(worksheet="Tresorerie", data=pd.concat([df_treso, new_treso], ignore_index=True))
                st.success("Opération archivée."); time.sleep(1); st.rerun()
            except Exception as e: st.error(f"Erreur de transmission : {e}")

        with tabs[0]:
            with st.form("atm_f"):
                b = st.number_input("Butin ATM ($)", min_value=0)
                if st.form_submit_button("VALIDER"): submit_op("ATM", butin=b)
        with tabs[1]:
            with st.form("sup_f"):
                b = st.number_input("Butin Supérette ($)", min_value=0)
                if st.form_submit_button("VALIDER"): submit_op("Supérette", butin=b)
        with tabs[2]:
            with st.form("gf_f"):
                b = st.number_input("Butin Go Fast ($)", min_value=0)
                if st.form_submit_button("VALIDER"): submit_op("Go Fast", butin=b)
        with tabs[3]:
            with st.form("cam_f"):
                if st.form_submit_button("VALIDER CAMBRIOLAGE"): submit_op("Cambriolage")
        with tabs[4]:
            with st.form("drug_f"):
                d = st.selectbox("Produit", DRUG_LIST)
                q = st.number_input("Nombre d'unités", min_value=0.0)
                b = st.number_input("Prix de vente total ($)", min_value=0)
                if st.form_submit_button("VALIDER VENTE"): submit_op("Drogue", butin=b, drogue=d, qte=-abs(q))

        st.markdown("---")

        # --- ÉTAT DE LA SEMAINE ---
        st.write("### 📊 Activité du groupe (Cette semaine)")
        if not df_full.empty:
            df_full['Date'] = pd.to_datetime(df_full['Date'], dayfirst=True, errors='coerce')
            start_week = (datetime.datetime.now() - timedelta(days=datetime.datetime.now().weekday())).replace(hour=0, minute=0, second=0)
            week_data = df_full[df_full['Date'] >= start_week]
            
            st.markdown("""
                <div style="display: flex; font-weight: bold; color: #a6a6a6; border-bottom: 2px solid #b48c3e; padding-bottom: 10px; margin-bottom: 15px;">
                    <div style="flex: 1.2;">NOM</div><div style="flex: 1;">ACTIONS ($)</div><div style="flex: 2;">OBJECTIF (20)</div><div style="flex: 2;">VENTES (300)</div>
                </div>
            """, unsafe_allow_html=True)

            for u_id, info in USERS.items():
                ps = info["pseudo"]
                u_lv = info["role_level"]
                u_data = week_data[week_data['Membre'] == ps]
                
                # Butin uniquement pour les actions (Hors Drogue/Ajustements Ventes)
                cash = u_data[~u_data['Action'].str.contains("Drogue|Ventes", case=False, na=False)]['Butin'].sum()
                
                # Calcul des actions (Normales + Ajustements)
                act_norm = len(u_data[(u_data['Action'] != "Drogue") & (~u_data['Action'].str.contains("Ajustement", na=False))])
                act_adj = u_data[u_data['Action'] == "Ajustement Action"]["Quantite"].sum()
                total_act = int(act_norm + act_adj)
                
                # Calcul des ventes
                total_vnt = int(abs(u_data[u_data['Action'].str.contains("Drogue|Ventes", case=False, na=False)]['Quantite'].sum()))
                
                ic = "⚜️" if u_lv == 1 else "⭐" if u_lv == 2 else "🔫"
                
                c1, c2, c3, c4 = st.columns([1.2, 1, 2, 2])
                c1.markdown(f'<div style="color:#f7e0a3; font-weight:bold;">{ic} {ps}</div>', unsafe_allow_html=True)
                c2.markdown(f'<div style="color:#ffffff;">{int(cash):,} $</div>'.replace(',', ' '), unsafe_allow_html=True)
                c3.progress(min(float(total_act)/20, 1.0), text=f"{total_act}/20")
                c4.progress(min(float(total_vnt)/300, 1.0), text=f"{total_vnt}/300")
                st.write("")

        st.markdown("---")
        st.write("### 🕒 Mes 3 dernières activités")
        mes_actions = df_full[df_full['Membre'] == u_pseudo].tail(3).iloc[::-1]
        if not mes_actions.empty:
            st.table(mes_actions[['Date', 'Action', 'Butin']])

    elif choice == "Comptabilité Globale" and u_role_lv <= 2:
        st.markdown('<div class="gta-title">Trésorerie</div>', unsafe_allow_html=True)
        
        df_v = conn.read(worksheet="Tresorerie", ttl=0)
        if not df_v.empty:
            def calc_v(df, et):
                sub = df[df['Etat'] == et]
                return sub[sub['Type'] == 'Recette']['Montant'].sum() - sub[sub['Type'] == 'Dépense']['Montant'].sum()
            
            p, s = calc_v(df_v, 'Propre'), calc_v(df_v, 'Sale')
            c1, c2, c3 = st.columns(3)
            c1.metric("PROPRE ⚜️", f"{int(p):,} $".replace(',', ' '))
            c2.metric("SALE 💵", f"{int(s):,} $".replace(',', ' '))
            c3.metric("TOTAL", f"{int(p+s):,} $".replace(',', ' '))
            
            st.markdown("---")
            st.write("### Historique des mouvements")
            st.dataframe(df_v.sort_index(ascending=False), use_container_width=True)

    elif choice == "Archives de la Niebla" and u_role_lv <= 2:
        st.markdown('<div class="gta-title">Archives</div>', unsafe_allow_html=True)
        st.dataframe(df_full.sort_index(ascending=False), use_container_width=True)
