import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import time
import hashlib

# --- CONFIG ---
st.set_page_config(page_title="La Niebla - FlashBack FA", page_icon="🥷", layout="wide")

# --- HASH PASSWORD ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- USERS SECURISES ---
USERS = {
    "Admin": {"password": hash_password("0000"), "pseudo": "El Patron"},
    "Alex": {"password": hash_password("Alx220717"), "pseudo": "Alex Smith"},
    "Dany": {"password": hash_password("081219"), "pseudo": "Dany Smith"},
    "Emilio": {"password": hash_password("azertyuiop123"), "pseudo": "Emilio Montoya"},
    "Aziz": {"password": hash_password("asmith"), "pseudo": "Aziz Smith"},
    "Junior": {"password": hash_password("Loup1304"), "pseudo": "Madra Junior"},
}

# --- SESSION ---
if 'connected' not in st.session_state:
    st.session_state['connected'] = False

# --- LOGIN ---
def check_login():
    u = st.session_state.get("user_login")
    p = st.session_state.get("password_login")
    if u in USERS and USERS[u]["password"] == hash_password(p):
        st.session_state['connected'] = True
        st.session_state['user_role'] = u
        st.session_state['user_pseudo'] = USERS[u]["pseudo"]

# --- CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- CACHE DATA ---
@st.cache_data(ttl=10)
def load_data(sheet):
    return conn.read(worksheet=sheet)

# --- SAFE UPDATE ---
def safe_update(sheet, new_row):
    for _ in range(3):
        try:
            df = conn.read(worksheet=sheet, ttl=0)
            conn.update(worksheet=sheet, data=pd.concat([df, new_row], ignore_index=True))
            return True
        except:
            time.sleep(1)
    return False

# --- CSS ---
st.markdown("""
<style>
body { background-color: #000; }
.gta-title {
    font-size: 70px;
    text-align: center;
    color: white;
    text-shadow: 0 0 10px #fff, 0 0 20px #aaa;
}
button:hover {
    transform: scale(1.05);
    transition: 0.2s;
}
</style>
""", unsafe_allow_html=True)

# --- LOGIN PAGE ---
if not st.session_state['connected']:
    st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)

    with st.form("login"):
        st.text_input("Nom", key="user_login")
        st.text_input("Mot de passe", type="password", key="password_login")
        if st.form_submit_button("Connexion"):
            check_login()
            if st.session_state['connected']:
                st.rerun()
            else:
                st.error("Accès refusé")

# --- APP ---
else:
    with st.sidebar:
        st.write(f"🥷 {st.session_state['user_pseudo']}")
        menu = ["Dashboard"]
        if st.session_state['user_role'] == "Admin":
            menu.append("Compta")
        choice = st.radio("Menu", menu)

        if st.button("Déconnexion"):
            st.session_state['connected'] = False
            st.rerun()

    # --- DASHBOARD ---
    if choice == "Dashboard":

        tabs = st.tabs(["ATM", "Supérette", "GoFast", "Cambriolage", "Drogue"])

        def handle_submit(action, butin=0, drogue="N/A", quantite=0):
            new_row = pd.DataFrame([{
                "Date": datetime.datetime.now(),
                "Membre": st.session_state['user_pseudo'],
                "Action": action,
                "Drogue": drogue,
                "Quantite": float(quantite),
                "Butin": float(butin)
            }])

            ok1 = safe_update("Rapports", new_row)

            new_money = pd.DataFrame([{
                "Date": datetime.datetime.now(),
                "Type": "Recette",
                "Etat": "Sale",
                "Catégorie": action,
                "Montant": float(butin),
                "Note": st.session_state['user_pseudo']
            }])

            ok2 = safe_update("Tresorerie", new_money)

            if ok1 and ok2:
                st.success("Envoyé")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Erreur envoi")

        # --- FORMS ---
        with tabs[0]:
            with st.form("atm"):
                b = st.number_input("Butin", 0)
                if st.form_submit_button("Valider"):
                    handle_submit("ATM", b)

        with tabs[4]:
            with st.form("dr"):
                d = st.selectbox("Produit", ["Marijuana", "Cocaine", "Meth"])
                q = st.number_input("Quantité", 0.0)
                b = st.number_input("Prix", 0)

                if st.form_submit_button("Vendre"):
                    df = load_data("Rapports")
                    stock = df[df["Drogue"] == d]["Quantite"].sum()

                    if stock < q:
                        st.error("Stock insuffisant")
                    else:
                        handle_submit("Drogue", b, d, -abs(q))

        # --- STATS ---
        st.markdown("## Stats semaine")

        df = load_data("Rapports")
        if df is not None and not df.empty:
            df['Date'] = pd.to_datetime(df['Date'])
            week = df[df['Date'] >= datetime.datetime.now() - datetime.timedelta(days=7)]

            stats = week.groupby("Membre").agg({
                "Action": "count",
                "Quantite": lambda x: abs(x).sum(),
                "Butin": "sum"
            }).reset_index()

            max_actions = max(stats["Action"].max(), 1)

            for _, row in stats.iterrows():
                c1, c2 = st.columns(2)
                c1.write(row["Membre"])
                c2.progress(row["Action"] / max_actions)

            # --- LEADERBOARD ---
            st.markdown("### 🏆 Top joueurs")
            top = stats.sort_values(by="Butin", ascending=False).head(3)
            st.table(top)

    # --- COMPTA ---
    elif choice == "Compta":
        st.write("Comptabilité")

        with st.form("add"):
            montant = st.number_input("Montant", 0)
            if st.form_submit_button("Ajouter"):
                new = pd.DataFrame([{
                    "Date": datetime.datetime.now(),
                    "Type": "Recette",
                    "Etat": "Propre",
                    "Catégorie": "Manuel",
                    "Montant": montant
                }])

                if safe_update("Tresorerie", new):
                    st.success("Ajouté")
                else:
                    st.error("Erreur")

        df = load_data("Tresorerie")
        if df is not None:
            st.dataframe(df)
