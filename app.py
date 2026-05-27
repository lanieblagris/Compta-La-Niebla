import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from datetime import timedelta
import time
import hashlib

# =========================================================
# ⚫️ CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="La División Network",
    page_icon="⚫️",
    layout="wide"
)

# =========================================================
# ⚫️ GOOGLE SHEETS
# =========================================================

conn = st.connection("gsheets", type=GSheetsConnection)

# =========================================================
# ⚫️ STYLE PREMIUM
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800&family=Rajdhani:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #090909 0%, #120b16 50%, #1a0f1f 100%);
    color: #f1f1f1;
}

[data-testid="stSidebar"] {
    background: rgba(10,10,10,0.95);
    border-right: 1px solid rgba(120,0,40,0.5);
}

.main-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 70px;
    font-weight: 800;
    text-align: center;
    color: #ffffff;
    margin-bottom: -10px;
    letter-spacing: 5px;
}

.sub-title {
    text-align: center;
    color: #8a2a52;
    font-size: 18px;
    margin-bottom: 30px;
    letter-spacing: 3px;
}

.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(138,42,82,0.3);
    border-radius: 18px;
    padding: 20px;
    backdrop-filter: blur(10px);
    box-shadow: 0 0 20px rgba(0,0,0,0.4);
}

.metric-card {
    text-align: center;
    padding: 20px;
    border-radius: 15px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(138,42,82,0.2);
}

.stButton>button {
    background: linear-gradient(90deg, #4b0f1c, #2b1639);
    color: white;
    border: none;
    border-radius: 12px;
    height: 45px;
    width: 100%;
    font-weight: bold;
}

.stButton>button:hover {
    background: linear-gradient(90deg, #6d1830, #3d1f4f);
    color: white;
}

.stTextInput input {
    background-color: rgba(255,255,255,0.05);
    color: white;
}

.stSelectbox div[data-baseweb="select"] {
    background-color: rgba(255,255,255,0.05);
}

table {
    border-radius: 10px !important;
    overflow: hidden !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# ⚫️ SESSION
# =========================================================

if "connected" not in st.session_state:
    st.session_state.connected = False

# =========================================================
# ⚫️ FONCTIONS
# =========================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# =========================================================
# ⚫️ INITIALISATION SHEETS
# =========================================================

try:
    users_df = conn.read(worksheet="USERS", ttl=0)
except:
    users_df = pd.DataFrame(columns=["Username", "Password", "Pseudo", "Role"])

try:
    reports_df = conn.read(worksheet="RAPPORTS", ttl=0)
except:
    reports_df = pd.DataFrame(columns=["Date", "Membre", "Action", "Gain"])

try:
    stocks_df = conn.read(worksheet="STOCKS", ttl=0)
except:
    stocks_df = pd.DataFrame(columns=["Produit", "Quantite"])

try:
    finance_df = conn.read(worksheet="FINANCE", ttl=0)
except:
    finance_df = pd.DataFrame(columns=["Date", "Type", "Montant", "Auteur"])

# =========================================================
# ⚫️ LOGIN / REGISTER
# =========================================================

if not st.session_state.connected:

    st.markdown("<div class='main-title'>LA DIVISIÓN</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>DIVISION NETWORK</div>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐 Connexion", "📝 Inscription"])

    # =====================================================
    # LOGIN
    # =====================================================

    with tab1:

        username = st.text_input("Nom de code")
        password = st.text_input("Mot de passe", type="password")

        if st.button("ACCÉDER AU RÉSEAU"):

            hashed = hash_password(password)

            user = users_df[
                (users_df["Username"] == username) &
                (users_df["Password"] == hashed)
            ]

            if not user.empty:

                st.session_state.connected = True
                st.session_state.username = username
                st.session_state.pseudo = user.iloc[0]["Pseudo"]
                st.session_state.role = user.iloc[0]["Role"]

                st.rerun()

            else:
                st.error("Accès refusé.")

    # =====================================================
    # REGISTER
    # =====================================================

    with tab2:

        new_user = st.text_input("Nom de code", key="reg_user")
        new_pass = st.text_input("Mot de passe", type="password", key="reg_pass")
        new_pseudo = st.text_input("Nom RP", key="reg_pseudo")

        if st.button("CRÉER UN ACCÈS"):

            if new_user in users_df["Username"].values:
                st.error("Nom déjà utilisé.")

            else:

                new_row = pd.DataFrame([{
                    "Username": new_user,
                    "Password": hash_password(new_pass),
                    "Pseudo": new_pseudo,
                    "Role": "Recluta"
                }])

                users_df = pd.concat([users_df, new_row], ignore_index=True)

                conn.update(
                    worksheet="USERS",
                    data=users_df
                )

                st.success("Compte créé.")

# =========================================================
# ⚫️ DASHBOARD
# =========================================================

else:

    pseudo = st.session_state.pseudo
    role = st.session_state.role

    # =====================================================
    # SIDEBAR
    # =====================================================

    with st.sidebar:

        st.markdown(f"## ⚫️ {pseudo}")
        st.write(f"**Rôle :** {role}")

        st.write("---")

        menu = st.radio(
            "Navigation",
            [
                "📡 Dashboard",
                "🎯 Activités",
                "📦 Stocks",
                "💰 Finance",
                "👥 Membres"
            ]
        )

        st.write("---")

        if st.button("Déconnexion"):
            st.session_state.clear()
            st.rerun()

    # =====================================================
    # DASHBOARD
    # =====================================================

    if menu == "📡 Dashboard":

        st.markdown("<div class='main-title'>LA DIVISIÓN</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-title'>DIVISION NETWORK</div>", unsafe_allow_html=True)

        total_gain = reports_df["Gain"].sum() if not reports_df.empty else 0
        total_reports = len(reports_df)
        total_members = len(users_df)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class='metric-card'>
            <h3>💰 Revenus</h3>
            <h1>{int(total_gain):,} $</h1>
            </div>
            """.replace(",", " "), unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class='metric-card'>
            <h3>🎯 Activités</h3>
            <h1>{total_reports}</h1>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class='metric-card'>
            <h3>👥 Membres</h3>
            <h1>{total_members}</h1>
            </div>
            """, unsafe_allow_html=True)

        st.write("")

        st.markdown("""
        <div class='card'>
        ⚫️ Bienvenue dans le réseau interne sécurisé de La División.
        <br><br>
        “Le pouvoir appartient à ceux capables de rester dans l’ombre.”
        </div>
        """, unsafe_allow_html=True)

    # =====================================================
    # ACTIVITÉS
    # =====================================================

    elif menu == "🎯 Activités":

        st.title("🎯 Activités Terrain")

        with st.form("activity_form"):

            action = st.selectbox(
                "Type d'activité",
                [
                    "ATM",
                    "Supérette",
                    "Go Fast",
                    "Cambriolage",
                    "Drogue",
                    "Transport",
                    "Renseignement"
                ]
            )

            gain = st.number_input(
                "Revenus ($)",
                min_value=0
            )

            submit = st.form_submit_button("ENREGISTRER")

            if submit:

                new_row = pd.DataFrame([{
                    "Date": now(),
                    "Membre": pseudo,
                    "Action": action,
                    "Gain": gain
                }])

                reports_df = pd.concat(
                    [reports_df, new_row],
                    ignore_index=True
                )

                conn.update(
                    worksheet="RAPPORTS",
                    data=reports_df
                )

                st.success("Activité enregistrée.")
                time.sleep(1)
                st.rerun()

        st.write("---")

        st.subheader("🏆 Influence interne")

        ranking = reports_df.groupby("Membre")["Gain"].sum().reset_index()

        ranking = ranking.sort_values(
            by="Gain",
            ascending=False
        )

        st.dataframe(ranking, use_container_width=True)

        st.write("---")

        st.subheader("🕒 Dernières activités")

        st.dataframe(
            reports_df.sort_index(ascending=False),
            use_container_width=True
        )

    # =====================================================
    # STOCKS
    # =====================================================

    elif menu == "📦 Stocks":

        st.title("📦 Réserves")

        st.dataframe(
            stocks_df,
            use_container_width=True
        )

        with st.form("stock_form"):

            produit = st.text_input("Produit")
            quantite = st.number_input("Quantité")

            submit = st.form_submit_button("AJOUTER")

            if submit:

                new_stock = pd.DataFrame([{
                    "Produit": produit,
                    "Quantite": quantite
                }])

                stocks_df = pd.concat(
                    [stocks_df, new_stock],
                    ignore_index=True
                )

                conn.update(
                    worksheet="STOCKS",
                    data=stocks_df
                )

                st.success("Stock ajouté.")
                time.sleep(1)
                st.rerun()

    # =====================================================
    # FINANCE
    # =====================================================

    elif menu == "💰 Finance":

        st.title("💰 Finance")

        total_money = finance_df["Montant"].sum() if not finance_df.empty else 0

        st.metric(
            "Trésorerie",
            f"{int(total_money):,} $".replace(",", " ")
        )

        with st.form("finance_form"):

            transaction_type = st.selectbox(
                "Type",
                ["Recette", "Dépense"]
            )

            amount = st.number_input(
                "Montant",
                min_value=0
            )

            submit = st.form_submit_button("VALIDER")

            if submit:

                value = amount if transaction_type == "Recette" else -amount

                new_finance = pd.DataFrame([{
                    "Date": now(),
                    "Type": transaction_type,
                    "Montant": value,
                    "Auteur": pseudo
                }])

                finance_df = pd.concat(
                    [finance_df, new_finance],
                    ignore_index=True
                )

                conn.update(
                    worksheet="FINANCE",
                    data=finance_df
                )

                st.success("Transaction enregistrée.")
                time.sleep(1)
                st.rerun()

        st.dataframe(
            finance_df.sort_index(ascending=False),
            use_container_width=True
        )

    # =====================================================
    # MEMBRES
    # =====================================================

    elif menu == "👥 Membres":

        st.title("👥 Membres")

        st.dataframe(
            users_df[["Pseudo", "Role"]],
            use_container_width=True
        )
