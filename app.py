# =========================================================
# ⚫️ LA DIVISIÓN NETWORK
# ⚫️ VERSION CINÉMATIQUE FIXÉE
# =========================================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import hashlib
import time

# =========================================================
# ⚫️ CONFIG
# =========================================================

st.set_page_config(
    page_title="La División Network",
    page_icon="⚫️",
    layout="wide"
)
import time

# =========================================================
# ⚫️ INTRO CINÉMATIQUE
# =========================================================

if "intro_played" not in st.session_state:

    st.session_state.intro_played = False

if not st.session_state.intro_played:

    st.markdown("""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&display=swap');

    .intro-container {

        height: 100vh;

        display: flex;

        justify-content: center;

        align-items: center;

        flex-direction: column;

        background: linear-gradient(
            135deg,
            #050505 0%,
            #120814 50%,
            #1d0d24 100%
        );
    }

    .intro-title {

        font-size: 72px;

        font-family: 'Orbitron', sans-serif;

        font-weight: 900;

        color: white;

        letter-spacing: 12px;

        animation: glow 2s infinite alternate;
    }

    .intro-sub {

        margin-top: 20px;

        color: #8f214d;

        letter-spacing: 5px;

        animation: pulse 2s infinite;
    }

    .intro-line {

        width: 320px;

        height: 2px;

        background: rgba(255,255,255,0.08);

        margin-top: 30px;

        overflow: hidden;

        position: relative;
    }

    .intro-line::before {

        content: '';

        position: absolute;

        width: 140px;

        height: 100%;

        background: linear-gradient(
            90deg,
            transparent,
            #8f214d,
            transparent
        );

        animation: loading 2s infinite;
    }

    @keyframes loading {

        0% {
            left: -140px;
        }

        100% {
            left: 320px;
        }
    }

    @keyframes glow {

        from {

            text-shadow:
            0 0 10px rgba(143,33,77,0.3),
            0 0 20px rgba(143,33,77,0.2);
        }

        to {

            text-shadow:
            0 0 20px rgba(143,33,77,0.9),
            0 0 40px rgba(143,33,77,0.7),
            0 0 60px rgba(143,33,77,0.4);
        }
    }

    @keyframes pulse {

        0% {
            opacity: 0.4;
        }

        50% {
            opacity: 1;
        }

        100% {
            opacity: 0.4;
        }
    }

    </style>

    <div class="intro-container">

        <div class="intro-title">
            LA DIVISIÓN
        </div>

        <div class="intro-line"></div>

        <div class="intro-sub">
            INITIALISATION DU RÉSEAU...
        </div>

    </div>

    """, unsafe_allow_html=True)

    time.sleep(3)

    st.session_state.intro_played = True

    st.rerun()

# =========================================================
# ⚫️ GOOGLE SHEETS
# =========================================================

conn = st.connection("gsheets", type=GSheetsConnection)

# =========================================================
# ⚫️ SESSION
# =========================================================

if "connected" not in st.session_state:
    st.session_state.connected = False

# =========================================================
# ⚫️ FUNCTIONS
# =========================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# =========================================================
# ⚫️ LOAD DATA
# =========================================================

try:
    users_df = conn.read(worksheet="USERS", ttl=0)
    users_df.columns = users_df.columns.str.strip()
except:
    users_df = pd.DataFrame(
        columns=["Username", "Password", "Pseudo", "Role"]
    )

try:
    reports_df = conn.read(worksheet="RAPPORTS", ttl=0)
except:
    reports_df = pd.DataFrame(
        columns=["Date", "Membre", "Action", "Gain"]
    )

try:
    finance_df = conn.read(worksheet="FINANCE", ttl=0)
except:
    finance_df = pd.DataFrame(
        columns=["Date", "Type", "Montant", "Auteur"]
    )

# =========================================================
# ⚫️ LOGIN
# =========================================================

if not st.session_state.connected:

    st.markdown(
        "<div class='main-title'>LA DIVISIÓN</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='sub-title'>DIVISION NETWORK</div>",
        unsafe_allow_html=True
    )

    st.subheader("🔐 Connexion sécurisée")

    username = st.text_input("Nom de code")
    password = st.text_input("Mot de passe", type="password")

    if st.button("ACCÉDER AU RÉSEAU"):

        hashed = hash_password(password)

        user = users_df[
            (
                users_df["Username"]
                .astype(str)
                .str.strip()
                == username.strip()
            )
            &
            (
                users_df["Password"]
                .astype(str)
                .str.strip()
                == hashed.strip()
            )
        ]

        if not user.empty:

            st.session_state.connected = True
            st.session_state.username = username
            st.session_state.pseudo = user.iloc[0]["Pseudo"]
            st.session_state.role = user.iloc[0]["Role"]

            st.rerun()

        else:
            st.error("Accès refusé.")

# =========================================================
# ⚫️ DASHBOARD
# =========================================================

else:

    pseudo = st.session_state.pseudo
    role = st.session_state.role

    with st.sidebar:

        st.markdown(f"## ⚫️ {pseudo}")
        st.write(f"**Rôle :** {role}")

        st.write("---")

        menu = st.radio(
            "Navigation",
            [
                "📡 Dashboard",
                "🎯 Activités",
                "💰 Finance"
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

        st.markdown(
            "<div class='main-title'>LA DIVISIÓN</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<div class='sub-title'>DIVISION NETWORK</div>",
            unsafe_allow_html=True
        )

        total_gain = (
            reports_df["Gain"].sum()
            if not reports_df.empty else 0
        )

        total_reports = len(reports_df)

        col1, col2 = st.columns(2)

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

        st.write("")

        st.markdown("""
        <div class='card'>
        ⚫️ Réseau interne sécurisé de La División.
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

            submit = st.form_submit_button(
                "ENREGISTRER"
            )

            if submit:

                new_row = pd.DataFrame([{
                    "Date": get_now(),
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

    # =====================================================
    # FINANCE
    # =====================================================

    elif menu == "💰 Finance":

        st.title("💰 Finance")

        total_money = (
            finance_df["Montant"].sum()
            if not finance_df.empty else 0
        )

        st.metric(
            "Trésorerie",
            f"{int(total_money):,} $".replace(",", " ")
        )

        st.dataframe(
            finance_df.sort_index(
                ascending=False
            ),
            use_container_width=True
        )
