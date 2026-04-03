import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import time

st.set_page_config(page_title="La Niebla", layout="wide")

STYLE GLOBAL
st.markdown("""
<style>

/* Fond global /
.stApp {
    background: radial-gradient(circle at center, #0a0a0a 0%, #000000 100%);
    overflow: hidden;
}

/ Brume animée /
#fog {
    position: fixed;
    top: 0;
    left: 0;
    width: 120%;
    height: 120%;
    background-image: url("https://i.gifer.com/7VE.gif");
    background-size: cover;
    opacity: 0.08;
    z-index: 0;
    animation: fogMove 120s linear infinite;
}

@keyframes fogMove {
    0% { transform: translate(0, 0); }
    50% { transform: translate(-5%, -3%); }
    100% { transform: translate(0, 0); }
}

/ Contenu au-dessus /
.main {
    position: relative;
    z-index: 1;
}

/ Titre /
h1 {
    text-align: center;
    font-family: "Georgia", serif;
    color: #ffffff;
    font-size: 70px;
    letter-spacing: 3px;
    text-shadow: 0 0 15px rgba(255,255,255,0.2);
}

/ Sous-texte RP /
.subtitle {
    text-align: center;
    color: #888;
    font-size: 14px;
    margin-bottom: 40px;
    letter-spacing: 2px;
}

/ Inputs /
.stTextInput input {
    background-color: #1a1a1a;
    border: 1px solid #333;
    color: white;
    border-radius: 8px;
}

/ Bouton /
.stButton button {
    background-color: transparent;
    border: 1px solid #444;
    color: white;
    padding: 10px 25px;
    border-radius: 8px;
    transition: 0.3s;
}

.stButton button:hover {
    border: 1px solid #888;
    box-shadow: 0 0 10px rgba(255,255,255,0.2);
}

/ Supprimer footer Streamlit */
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}

</style>

<div id="fog"></div>

""", unsafe_allow_html=True)

CONTENU RP
st.markdown("<h1>La Niebla</h1>", unsafe_allow_html=True)
st.markdown('<div class="subtitle">EN EL SILENCIO, MANDAMOS</div>', unsafe_allow_html=True)

st.markdown("---")

code = st.text_input("Nom de code")
password = st.text_input("Mot de passe", type="password")

st.button("S'INFILTRER")

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="La Niebla - FlashBack FA", page_icon="🥷", layout="wide")

# --- 2. LIEN DE LA VIDÉO ---
VIDEO_URL = "https://assets.mixkit.co/videos/preview/mixkit-mysterious-pale-fog-moving-slowly-over-the-ground-44130-large.mp4"

# --- 3. STYLE CSS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&display=swap');
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {{ background: transparent !important; }}
    body {{ background-color: #000000; }}
    .gta-title {{
        font-family: 'UnifrakturMaguntia', cursive; font-size: 85px; color: white;
        text-align: center; text-shadow: 5px 5px 15px #000, 0 0 25px #555;
        margin-top: -60px; margin-bottom: 10px; letter-spacing: 3px;
    }}
    #bgVideo {{
        position: fixed; right: 0; bottom: 0; min-width: 100%; min-height: 100%;
        z-index: -1000; filter: brightness(0.3); object-fit: cover;
    }}
    .stForm {{ background-color: rgba(10, 10, 10, 0.85) !important; border: 1px solid #444 !important; border-radius: 10px; }}
    h1, h2, h3, h4, p, label, .stMarkdown, [data-testid="stWidgetLabel"] {{ color: white !important; font-family: 'Courier New', monospace; }}
    [data-testid="stSidebar"] {{ background-color: rgba(0, 0, 0, 0.9) !important; }}
    [data-testid="stMetricValue"] {{ color: white !important; }}
    [data-testid="stMetricLabel"] {{ color: #bbb !important; }}
    </style>
    <video autoplay loop muted playsinline id="bgVideo"><source src="{VIDEO_URL}" type="video/mp4"></video>
    """, unsafe_allow_html=True)

# --- 4. BASE DE DONNÉES ---
USERS = {
    "Admin": {"password": "0000", "pseudo": "El Patron"},
    "Alex": {"password": "Alx220717", "pseudo": "Alex Smith"},
    "Dany": {"password": "081219", "pseudo": "Dany Smith"},
    "Emilio": {"password": "azertyuiop123", "pseudo": "Emilio Montoya"},
}

if 'connected' not in st.session_state:
    st.session_state['connected'] = False

def check_login():
    u = st.session_state.get("user_login")
    p = st.session_state.get("password_login")
    if u in USERS and USERS[u]["password"] == p:
        st.session_state['connected'] = True
        st.session_state['user_role'] = u
        st.session_state['user_pseudo'] = USERS[u]["pseudo"]

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 5. LOGIQUE D'AFFICHAGE ---
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
        if st.session_state['user_role'] == "Admin": menu.append("Comptabilité Globale")
        choice = st.radio("Navigation", menu)
        if st.button("Déconnexion"):
            st.session_state['connected'] = False
            st.rerun()

    if choice == "Tableau de bord":
        st.markdown('<div class="gta-title" style="font-size:60px;">La Niebla</div>', unsafe_allow_html=True)
        LOGO_URL = "https://raw.githubusercontent.com/lanieblagris/Compta-La-Niebla/main/logo.png?v=4"
        st.markdown(f'<div style="text-align:center;"><img src="{LOGO_URL}" style="width:100%; max-height:200px; object-fit:cover; border-radius:10px;"></div>', unsafe_allow_html=True)
        
        tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

        def handle_submit(action, butin=0, drogue="N/A", quantite=0):
            try:
                # IMPORTANT : On enregistre la quantité telle qu'elle arrive (négative pour les ventes)
                new_row = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Membre": st.session_state['user_pseudo'], "Action": action, "Drogue": drogue, "Quantite": float(quantite), "Butin": float(butin)}])
                df = conn.read(worksheet="Rapports", ttl=0)
                conn.update(worksheet="Rapports", data=pd.concat([df, new_row], ignore_index=True))
                
                df_c = conn.read(worksheet="Tresorerie", ttl=0)
                new_op = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Type": "Recette", "Etat": "Sale", "Catégorie": action, "Montant": float(butin), "Note": f"Rapport de {st.session_state['user_pseudo']}"}])
                conn.update(worksheet="Tresorerie", data=pd.concat([df_c, new_op], ignore_index=True))
                
                st.success("Transmis avec succès.")
                time.sleep(1); st.rerun() 
            except Exception as e: st.error(f"Erreur : {e}")

        # Forms...
        with tabs[0]:
            with st.form("atm"):
                b = st.number_input("💵 Butin ($)", min_value=0, key="b_atm")
                if st.form_submit_button("VALIDER ATM"): handle_submit("ATM", butin=b)
        with tabs[1]:
            with st.form("sup"):
                b = st.number_input("💵 Butin ($)", min_value=0, key="b_sup")
                if st.form_submit_button("VALIDER SUPERETTE"): handle_submit("Supérette", butin=b)
        with tabs[2]:
            with st.form("gf"):
                b = st.number_input("💵 Butin ($)", min_value=0, key="b_gf")
                if st.form_submit_button("VALIDER GO FAST"): handle_submit("Go Fast", butin=b)
        with tabs[3]:
            with st.form("cam"):
                if st.form_submit_button("VALIDER CAMBRIOLAGE"): handle_submit("Cambriolage")
        with tabs[4]:
            with st.form("dr"):
                d = st.selectbox("🌿 Produit", ["Marijuana", "Cocaine", "Meth", "Heroine", "Crack", "Carte prepaye", "Tranq"])
                q = st.number_input("📦 Quantité vendue", min_value=0.0)
                b = st.number_input("💵 Prix de vente ($)", min_value=0)
                # ICI : On envoie la quantité en NÉGATIF pour la déduire du stock
                if st.form_submit_button("VALIDER VENTE"): 
                    handle_submit("Drogue", butin=b, drogue=d, quantite=-abs(q))

        # Stats Hebdo
        st.markdown("---")
        st.write("### 📊 STATISTIQUES DE LA SEMAINE")
        all_members = [u["pseudo"] for u in USERS.values()]
        stats = pd.DataFrame({'Membre': all_members, 'Action': [0]*len(all_members), 'Butin_x': [0.0]*len(all_members), 'Quantite': [0.0]*len(all_members), 'Butin_y': [0.0]*len(all_members)})
        try:
            data = conn.read(worksheet="Rapports", ttl=0)
            if data is not None and not data.empty:
                data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
                start_week = (datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().weekday())).replace(hour=0, minute=0)
                week_data = data[data['Date'] >= start_week].copy()
                if not week_data.empty:
                    s_act = week_data[week_data['Action'] != "Drogue"].groupby('Membre').agg({'Action': 'count', 'Butin': 'sum'}).reset_index()
                    # Pour les stats, on affiche la valeur absolue des ventes
                    s_dro = week_data[week_data['Action'] == "Drogue"].groupby('Membre').agg({'Quantite': lambda x: abs(x).sum(), 'Butin': 'sum'}).reset_index()
                    current_stats = pd.merge(s_act, s_dro, on='Membre', how='outer').fillna(0)
                    stats = pd.merge(stats[['Membre']], current_stats, on='Membre', how='left').fillna(0)
        except: pass

        for _, row in stats.iterrows():
            c1, c2, c3 = st.columns([1, 2, 2])
            c1.write(f"**{row['Membre']}**")
            c2.progress(min(int(row['Action'])/20, 1.0), text=f"Actions: {int(row['Action'])}")
            c3.progress(min(int(row['Quantite'])/300, 1.0), text=f"Ventes: {int(row['Quantite'])}")
        
        st.write("#### 💸 RÉCAPITULATIF FINANCIER (SEMAINE)")
        df_recap = stats[['Membre', 'Butin_x', 'Butin_y']].copy()
        df_recap.columns = ['Membre', 'Actions ($)', 'Drogue ($)']
        df_recap['Actions ($)'] = df_recap['Actions ($)'].apply(lambda x: f"{int(x):,.0f} $".replace(',', ' '))
        df_recap['Drogue ($)'] = df_recap['Drogue ($)'].apply(lambda x: f"{int(x):,.0f} $".replace(',', ' '))
        st.table(df_recap)

    elif choice == "Comptabilité Globale":
        st.markdown('<div class="gta-title" style="font-size:50px;">Tresorerie</div>', unsafe_allow_html=True)
        sub_tabs = st.tabs(["📊 Vue d'ensemble", "🧼 Blanchiment", "📦 Gestion des Stocks"])

        with sub_tabs[0]:
            with st.form("compta_form"):
                st.write("#### Enregistrer une Opération Manuel")
                c1, c2, c3, c4 = st.columns(4)
                t_type = c1.selectbox("Type", ["Recette", "Dépense"])
                t_etat = c2.selectbox("Argent", ["Sale", "Propre"])
                t_cat = c3.text_input("Catégorie")
                t_montant = c4.number_input("Montant ($)", min_value=0)
                t_note = st.text_area("Note / Justification")
                if st.form_submit_button("Valider"):
                    try:
                        df_c = conn.read(worksheet="Tresorerie", ttl=0)
                        new_op = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Type": t_type, "Etat": t_etat, "Catégorie": t_cat, "Montant": float(t_montant), "Note": t_note}])
                        conn.update(worksheet="Tresorerie", data=pd.concat([df_c, new_op], ignore_index=True))
                        st.success("Validé."); time.sleep(1); st.rerun()
                    except: st.error("Erreur.")

        with sub_tabs[1]:
            st.write("#### 🧼 Blanchisseur")
            with st.form("blanchiment_form"):
                col_a, col_b = st.columns(2)
                m_sale = col_a.number_input("Montant sale ($)", min_value=0)
                taux = col_b.slider("Taux (%)", 0, 100, 20)
                propre = m_sale * (1 - taux/100)
                if st.form_submit_button("BLANCHIR"):
                    df_t = conn.read(worksheet="Tresorerie", ttl=0)
                    op_s = {"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Type": "Dépense", "Etat": "Sale", "Catégorie": "Blanchiment", "Montant": float(m_sale), "Note": "Sortie blanchiment"}
                    op_p = {"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Type": "Recette", "Etat": "Propre", "Catégorie": "Blanchiment", "Montant": float(propre), "Note": f"Retour blanchiment (-{taux}%)"}
                    conn.update(worksheet="Tresorerie", data=pd.concat([df_t, pd.DataFrame([op_s, op_p])], ignore_index=True))
                    st.success("Blanchi !"); time.sleep(1); st.rerun()

        with sub_tabs[2]:
            st.write("#### 📦 État des Stocks")
            # FORMULAIRE POUR AJOUTER DU STOCK (Admin seulement)
            with st.form("add_stock"):
                st.write("➕ AJOUTER UN ARRIVAGE (Récolte / Achat)")
                c1, c2 = st.columns(2)
                d_name = c1.selectbox("Produit", ["Marijuana", "Cocaine", "Meth", "Heroine", "Crack", "Carte prepaye", "Tranq"])
                d_qty = c2.number_input("Quantité à ajouter (+)", min_value=0.0)
                if st.form_submit_button("VALIDER L'ARRIVAGE"):
                    # ICI : On enregistre en POSITIF pour augmenter le stock
                    new_s = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Membre": "LA NIEBLA", "Action": "Drogue", "Drogue": d_name, "Quantite": float(d_qty), "Butin": 0}])
                    df_all_r = conn.read(worksheet="Rapports", ttl=0)
                    conn.update(worksheet="Rapports", data=pd.concat([df_all_r, new_s], ignore_index=True))
                    st.success("Stock augmenté !"); time.sleep(1); st.rerun()

            # CALCUL ET AFFICHAGE DU STOCK REEL
            st.write("---")
            try:
                df_rep = conn.read(worksheet="Rapports", ttl=0)
                if not df_rep.empty:
                    # Stock = Somme de toutes les quantités (Ventes négatives + Arrivages positifs)
                    df_drugs = df_rep[df_rep['Action'] == "Drogue"].copy()
                    stock_final = df_drugs.groupby('Drogue')['Quantite'].sum().reset_index()
                    
                    cols = st.columns(len(stock_final) if len(stock_final) > 0 else 1)
                    if not stock_final.empty:
                        for i, row in stock_final.iterrows():
                            cols[i].metric(row['Drogue'], f"{row['Quantite']:.1f} unités")
                    else:
                        st.info("Aucun stock en inventaire.")
            except: pass

        # Footer Trésorerie
        st.markdown("---")
        try:
            df_all = conn.read(worksheet="Tresorerie", ttl=0)
            if not df_all.empty:
                df_calc = df_all.dropna(subset=['Montant', 'Type', 'Etat'])
                rec_p = df_calc[(df_calc['Type']=="Recette") & (df_calc['Etat']=="Propre")]['Montant'].sum()
                dep_p = df_calc[(df_calc['Type']=="Dépense") & (df_calc['Etat']=="Propre")]['Montant'].sum()
                rec_s = df_calc[(df_calc['Type']=="Recette") & (df_calc['Etat']=="Sale")]['Montant'].sum()
                dep_s = df_calc[(df_calc['Type']=="Dépense") & (df_calc['Etat']=="Sale")]['Montant'].sum()
                m1, m2, m3 = st.columns(3)
                m1.metric("SOLDE PROPRE", f"{rec_p - dep_p:,.0f} $")
                m2.metric("SOLDE SALE", f"{rec_s - dep_s:,.0f} $")
                m3.metric("TOTAL GLOBAL", f"{(rec_p + rec_s) - (dep_p + dep_s):,.0f} $")
                st.dataframe(df_all.sort_values(by="Date", ascending=False), use_container_width=True)
        except: pass
