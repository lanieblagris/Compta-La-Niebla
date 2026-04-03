import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="La Niebla - Safe House", page_icon="🥷", layout="wide")

# --- BASE DE DONNÉES DES MEMBRES ---
USERS = {
    "Admin": {"password": "0000", "pseudo": "Le Patron"},
    "Alex": {"password": "1234", "pseudo": "Alex Smith"},
    "Dany": {"password": "081219", "pseudo": "Dany Smith"},
}

# --- STYLE CSS GÉNÉRAL ---
st.markdown("""
    <style>
    /* Fond noir total */
    .stApp { background-color: #000000 !important; }

    /* ANIMATION DE LA BRUME (FOG) */
    .fogwrapper {
        height: 100%;
        position: fixed;
        top: 0;
        width: 100%;
        -webkit-filter: blur(1px);
        filter: blur(1px);
        z-index: 0;
    }
    #foglayer_01, #foglayer_02, #foglayer_03 {
        height: 100%;
        position: absolute;
        width: 200%;
    }
    #foglayer_01 .image01, #foglayer_01 .image02,
    #foglayer_02 .image01, #foglayer_02 .image02,
    #foglayer_03 .image01, #foglayer_03 .image02 {
        float: left;
        height: 100%;
        width: 50%;
    }
    #foglayer_01 { -webkit-animation: foglayer_01_opacity 10s linear infinite, foglayer_moveme 15s linear infinite; animation: foglayer_01_opacity 10s linear infinite, foglayer_moveme 15s linear infinite; }
    #foglayer_02 { -webkit-animation: foglayer_02_opacity 15s linear infinite, foglayer_moveme 13s linear infinite; animation: foglayer_02_opacity 15s linear infinite, foglayer_moveme 13s linear infinite; }
    #foglayer_03 { -webkit-animation: foglayer_03_opacity 20s linear infinite, foglayer_moveme 11s linear infinite; animation: foglayer_03_opacity 20s linear infinite, foglayer_moveme 11s linear infinite; }

    .image01, .image02 {
        background: url("https://raw.githubusercontent.com/Anemolo/Fog-Effect/master/fog1.png") center center / cover no-repeat transparent;
    }

    @-webkit-keyframes foglayer_moveme { 0% { left: 0; } 100% { left: -100%; } }
    @keyframes foglayer_moveme { 0% { left: 0; } 100% { left: -100%; } }

    @-webkit-keyframes foglayer_01_opacity { 0% { opacity: .1; } 22% { opacity: .5; } 40% { opacity: .28; } 58% { opacity: .4; } 80% { opacity: .16; } 100% { opacity: .1; } }
    @keyframes foglayer_01_opacity { 0% { opacity: .1; } 22% { opacity: .5; } 40% { opacity: .28; } 58% { opacity: .4; } 80% { opacity: .16; } 100% { opacity: .1; } }
    
    /* Autres Styles UI */
    .brouillard-text { font-family: 'Courier New', monospace; color: rgba(255, 255, 255, 0.6); font-size: 18px; text-align: center; }
    h1, h2, h3 { color: #ffffff !important; text-align: center; font-family: 'Courier New'; }
    .stForm { border: 1px solid #333; border-radius: 15px; background-color: rgba(10, 10, 10, 0.85); position: relative; z-index: 100; }
    .stButton>button { background-color: #ff4b4b; color: white; font-weight: bold; border-radius: 10px; border: none; width: 100%; }
    .stProgress > div > div > div > div { background-color: #ff4b4b; }
    [data-
