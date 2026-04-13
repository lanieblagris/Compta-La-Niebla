import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import time

# --- 1. CONFIGURATION ET CONSTANTES GLOBALES ---
st.set_page_config(page_title="La Niebla - FlashBack FA", page_icon="🥷", layout="wide")

DRUG_LIST = ["Marijuana", "Cocaine", "Meth", "Heroine", "Tranq", "Carte Prépayer", "B-magic", "Crack", "Autre"]

USERS = {
    "Admin": {"password": "0000", "pseudo": "El Patron"},
    "Alex": {"password": "Alx220717", "pseudo": "Alex Smith"},
    "Dany": {"password": "081219", "pseudo": "Dany Smith"},
    "Emilio": {"password": "azertyuiop123", "pseudo": "Emilio Montoya"},
    "Aziz": {"password": "asmith", "pseudo": "Aziz Smith"},
    "Alain": {"password": "999cww59", "pseudo": "Alain Bourdin"},
}

# --- 2. STYLE CSS & BACKGROUND ---
VIDEO_URL = "https://assets.mixkit.co/videos/preview/mixkit-mysterious-pale-fog-moving-slowly-over-the-ground-44130-large.mp4"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&display=swap');
    .stApp {{ background: transparent !important; }}
    body {{ background-color: #000000; }}
    .gta-title {{
        font-family: 'UnifrakturMaguntia', cursive; font-size: 85px; color: white;
        text-align: center; text-shadow: 5px 5px 15px #000, 0 0 25px #555;
        margin-top: -60px; margin-bottom: 0px; letter-spacing: 3px;
    }}
    .lore-quote {{
        font-family: 'Courier New', monospace; color: #888; font-size: 18px;
        text-align: center; letter-spacing: 2px; text-transform: uppercase;
        margin-bottom: 30px; opacity: 0.8; font-style: italic;
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

# --- 3. CONNEXION ET LOGS INVISIBLES ---
conn = st.connection("gsheets", type=GSheetsConnection)

def log_invisible(action, details=""):
    try:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        df_r = conn.read(worksheet="Rapports", ttl=0)
        new_log = pd.DataFrame([{
            "Date": ts,
            "Membre": st.session_state.get('user_pseudo', 'Système'),
            "Action": f"[LOG] {action}",
            "Drogue": "N/A", "Quantite": 0, "Butin": 0, "Note": details
        }])
        conn.update(worksheet="Rapports", data=pd.concat([df_r, new_log], ignore_index=True))
    except:
        pass

if 'connected' not in st.session_state:
    st.session_state['connected'] = False
if "form_key" not in st.session_state:
    st.session_state.form_key = 0

def
