import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from datetime import timedelta
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="La Niebla - Luxury Cartel", page_icon="⚜️", layout="wide")

# Roles: 1: El Patron, 2: Lieutenant, 3: Sicario
USERS = {
    "Admin": {"password": "0000", "pseudo": "El Patron", "role_level": 1},
    "Alex": {"password": "Alx220717", "pseudo": "Alex Smith", "role_level": 3},
    "Dany": {"password": "081219", "pseudo": "Dany Smith", "role_level": 2},
    "Aziz": {"password": "asmith", "pseudo": "Aziz Smith", "role_level": 3},
    "Alain": {"password": "999cww59", "pseudo": "Alain Bourdin", "role_level": 3},
}

DRUG_LIST = ["Marijuana", "Cocaine", "Meth", "Heroine", "Tranq", "Carte Prépayer", "B-magic", "Crack", "Autre"]

# --- 2. STYLE CSS LUXE ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&family=Marcellus&display=swap');
    .stApp {{ background: url('https://w0.peakpx.com/wallpaper/70/463/wallpaper-dark-grey-textured-dark-grey-background-textured-background.jpg'); background-size: cover; background-attachment: fixed; }}
    h1, h2, h3, h4, p, label, .stMarkdown, [data-testid="stWidgetLabel"] {{ color: #f7e0a3 !important; font-family: 'Marcellus', serif !important; }}
    .gta-title {{ font-family: 'UnifrakturMaguntia', cursive; font-size: 90px; color: transparent; background-image: linear-gradient(to bottom, #f7e0a3, #b48c3e, #f7e0a3); -webkit-background-clip: text; background-clip: text; text-align: center; margin-top: -50px; margin-bottom: 10px; }}
    .gta-slogan {{ font-family: 'Marcellus', serif; font-size: 18px; color: #a6a6a6 !important; text-align: center; margin-bottom: 30px; font-style: italic; }}
    .stForm {{ background-color: rgba(10, 10, 10, 0.85) !important; border: 1px solid #b48c3e !important; border-radius: 8px; }}
    [data-testid="stSidebar"] {{ background-color: rgba(15, 15, 15, 0.98) !important; border-right: 1px solid #b48c3e; }}
    .stProgress > div > div > div > div {{ background-image: linear-gradient(to right, #b48c3e, #f7e0a3) !important; }}
    [data-testid="stMetricValue"] {{ color: #f7e0a3 !important; font-family: 'Marcellus', serif; font-size: 35px; }}
    th {{ color: #b48c3e !important; }}
    td {{ color: #ffffff !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. FONCTIONS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_now():
    return (datetime.datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")

if 'connected' not in st.session_state: st.session_state['connected'] = False

# --- 4. LOGIQUE CONNEXION ---
if not st.session_state['connected']:
    st.write("<br><br><br>", unsafe_allow_html=True)
    st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        with st.form("login_form"):
            u_in = st.text_input("NOM DE CODE")
            p_in = st.text_input("MOT DE PASSE", type="password")
            if st.form_submit_button("S'INFILTRER"):
                if u_in in USERS and USERS[u_in]["password"] == p_in:
                    st.session_state.update({"connected": True, "user_id": u_in, "user_pseudo": USERS[u_in]["pseudo"], "role_level": USERS[u_in]["role_level"]})
                    st.rerun()
                else: st.error("Accès refusé.")
else:
    u_pseudo = st.session_state['user_pseudo']
    u_role_lv = st.session_state['role_level']

    with st.sidebar:
        icon = "⚜️" if u_role_lv == 1 else "⭐" if u_role_lv == 2 else "🔫"
        r_name = "El Patron" if u_role_lv == 1 else "Lieutenant" if u_role_lv == 2 else "Sicario"
        st.write(f"### {u_pseudo} {icon}")
        st.write(f"**Rang :** {r_name}")
        st.write("---")
        menu = ["Tableau de bord"]
        if u_role_lv <= 2: menu += ["Comptabilité Globale", "Archives de la Niebla"]
        choice = st.radio("Navigation", menu)
        st.write("---")
        if st.button("Se déconnecter"): st.session_state.clear(); st.rerun()

    df_full = conn.read(worksheet="Rapports", ttl=0)

    # --- TABLEAU DE BORD ---
    if choice == "Tableau de bord":
        st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
        
        tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])
        
        def submit_op(action, butin=0, drogue="N/A", qte=0):
            ts = get_now()
            df_r = conn.read(worksheet="Rapports", ttl=0)
            new_r = pd.DataFrame([{"Date": ts, "Membre": u_pseudo, "Action": action, "Drogue": drogue, "Quantite": float(qte), "Butin": float(butin)}])
            conn.update(worksheet="Rapports", data=pd.concat([df_r, new_r], ignore_index=True))
            
            df_t = conn.read(worksheet="Tresorerie", ttl=0)
            new_t = pd.DataFrame([{"Date": ts, "Type": "Recette", "Etat": "Sale", "Catégorie": action, "Montant": float(butin), "Note": f"Par {u_pseudo}"}])
            conn.update(worksheet="Tresorerie", data=pd.concat([df_t, new_t], ignore_index=True))
            st.success("Transmis !"); time.sleep(1); st.rerun()

        with tabs[0]:
            with st.form("atm_f"):
                b = st.number_input("Butin ATM ($)", min_value=0)
                if st.form_submit_button("VALIDER ATM"): submit_op("ATM", butin=b)
        
        with tabs[1]:
            with st.form("sup_f"):
                b = st.number_input("Butin Supérette ($)", min_value=0)
                if st.form_submit_button("VALIDER SUPÉRETTE"): submit_op("Supérette", butin=b)
        
        with tabs[2]:
            with st.form("gf_f"):
                b = st.number_input("Butin Go Fast ($)", min_value=0)
                if st.form_submit_button("VALIDER GO FAST"): submit_op("Go Fast", butin=b)
        
        with tabs[3]:
            with st.form("cam_f"):
                st.write("Confirmer le cambriolage effectué ?")
                if st.form_submit_button("VALIDER CAMBRIOLAGE"): submit_op("Cambriolage")
        
        with tabs[4]:
            with st.form("drug_f"):
                d = st.selectbox("Produit", DRUG_LIST)
                q = st.number_input("Unités vendues", min_value=0.0)
                b = st.number_input("Prix de vente total ($)", min_value=0)
                if st.form_submit_button("VALIDER VENTE DROGUE"): submit_op("Drogue", butin=b, drogue=d, qte=-abs(q))

        st.markdown("---")

        # --- OBJECTIFS ---
        st.write("### 📊 Objectifs de la Semaine")
        if not df_full.empty:
            df_stats = df_full.copy()
            df_stats['Date'] = pd.to_datetime(df_stats['Date'], dayfirst=True, errors='coerce')
            start_week = (datetime.datetime.now() - timedelta(days=datetime.datetime.now().weekday())).replace(hour=0, minute=0, second=0)
            week_data = df_stats[df_stats['Date'] >= start_week]
            
            for u_id, info in USERS.items():
                ps = info["pseudo"]; u_lv = info["role_level"]; u_data = week_data[week_data['Membre'] == ps]
                cash = u_data[~u_data['Action'].str.contains("Drogue|Ventes", case=False, na=False)]['Butin'].sum()
                act = int(len(u_data[(u_data['Action'] != "Drogue") & (~u_data['Action'].str.contains("Ajustement", na=False))]) + u_data[u_data['Action'] == "Ajustement Action"]["Quantite"].sum())
                vnt = int(abs(u_data[u_data['Action'].str.contains("Drogue|Ventes", case=False, na=False)]['Quantite'].sum()))
                
                c1, c2, c3, c4 = st.columns([1.2, 1, 2, 2])
                c1.markdown(f'<div style="color:#f7e0a3; font-weight:bold;">{ps}</div>', unsafe_allow_html=True)
                c2.markdown(f'<div style="color:#ffffff;">{int(cash):,} $</div>'.replace(',', ' '), unsafe_allow_html=True)
                c3.progress(min(float(act)/20, 1.0), text=f"{act}/20")
                c4.progress(min(float(vnt)/300, 1.0), text=f"{vnt}/300")

        st.write("---")
st.markdown("### 🏆 Top de la semaine (Revenus)")

# Calcul des revenus par membre sur la semaine en cours
if not week_data.empty:
    # On groupe par membre et on somme le Butin
    classement = week_data.groupby("Membre")["Butin"].sum().reset_index()
    classement = classement.sort_values(by="Butin", ascending=False)

    for i, row in classement.iterrows():
        # Récupération du rôle pour l'icône
        pseudo = row['Membre']
        # On cherche le niveau de rôle dans le dictionnaire USERS
        # On fait une petite boucle pour trouver le bon membre par son pseudo
        user_info = next((info for info in USERS.values() if info["pseudo"] == pseudo), None)
        
        if user_info:
            lv = user_info["role_level"]
            icon = "⚜️" if lv == 1 else "⭐" if lv == 2 else "🔫"
        else:
            icon = "👤"

        # Affichage stylisé
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{i+1}. {icon} {pseudo}**")
        with col2:
            st.markdown(f"**{int(row['Butin']):,} $**".replace(",", " "))
        
        # Barre de progression décorative (optionnel, basé sur un record de 200k)
        progression = min(float(row['Butin']) / 200000, 1.0)
        st.progress(progression)
else:
    st.write("_Aucune donnée cette semaine_")
        
        # --- MES 3 DERNIÈRES ACTIVITÉS ---
        st.write("### 🕒 Mes 3 dernières activités")
        mes_actions = df_full[df_full['Membre'] == u_pseudo].tail(3).iloc[::-1].copy()
        
        if not mes_actions.empty:
            mes_actions['Butin'] = mes_actions['Butin'].apply(lambda x: f"{int(float(x)):,} $".replace(',', ' '))
            st.table(mes_actions[['Date', 'Action', 'Butin']])

    # --- COMPTABILITÉ GLOBALE ---
    elif choice == "Comptabilité Globale":
        st.markdown('<div class="gta-title">Trésorerie</div>', unsafe_allow_html=True)
        df_v = conn.read(worksheet="Tresorerie", ttl=0)
        if not df_v.empty:
            def c_v(df, e):
                sub = df[df['Etat'] == e]
                return sub[sub['Type'] == 'Recette']['Montant'].sum() - sub[sub['Type'] == 'Dépense']['Montant'].sum()
            p, s = c_v(df_v, 'Propre'), c_v(df_v, 'Sale')
            c1, c2, c3 = st.columns(3)
            c1.metric("PROPRE ⚜️", f"{int(p):,} $".replace(',', ' '))
            c2.metric("SALE 💵", f"{int(s):,} $".replace(',', ' '))
            c3.metric("TOTAL Coffre", f"{int(p+s):,} $".replace(',', ' '))

        if u_role_lv == 1:
            st.write("---")
            col_a, col_b = st.columns(2)
            with col_a:
                with st.expander("🛠️ AJUSTEMENT OBJECTIFS"):
                    with st.form("adj_obj"):
                        target = st.selectbox("Membre", [u["pseudo"] for u in USERS.values()])
                        type_adj = st.radio("Type", ["Actions", "Ventes"])
                        valeur = st.number_input("Valeur", min_value=1)
                        if st.form_submit_button("APPLIQUER"):
                            q_save = float(valeur) if type_adj == "Actions" else -float(valeur)
                            df_r = conn.read(worksheet="Rapports", ttl=0)
                            new_l = pd.DataFrame([{"Date": get_now(), "Membre": target, "Action": f"Ajustement {type_adj}", "Drogue": "N/A", "Quantite": q_save, "Butin": 0}])
                            conn.update(worksheet="Rapports", data=pd.concat([df_r, new_l], ignore_index=True))
                            st.success("Objectif mis à jour !"); time.sleep(1); st.rerun()
            with col_b:
                with st.expander("💰 MOUVEMENT DE CAISSE"):
                    with st.form("adj_fin"):
                        t_m = st.selectbox("Type", ["Recette", "Dépense"])
                        e_m = st.selectbox("État", ["Sale", "Propre"])
                        v_m = st.number_input("Montant ($)", min_value=0)
                        cat = st.text_input("Raison")
                        if st.form_submit_button("VALIDER TRANSACTION"):
                            df_t = conn.read(worksheet="Tresorerie", ttl=0)
                            new_t = pd.DataFrame([{"Date": get_now(), "Type": t_m, "Etat": e_m, "Catégorie": cat, "Montant": float(v_m), "Note": f"Admin: {u_pseudo}"}])
                            conn.update(worksheet="Tresorerie", data=pd.concat([df_t, new_t], ignore_index=True))
                            st.success("Caisse mise à jour !"); time.sleep(1); st.rerun()

        st.write("### Historique des flux financiers")
        st.dataframe(df_v.sort_index(ascending=False), use_container_width=True)

    elif choice == "Archives de la Niebla":
        st.markdown('<div class="gta-title">Archives</div>', unsafe_allow_html=True)
        st.dataframe(df_full.sort_index(ascending=False), use_container_width=True)
