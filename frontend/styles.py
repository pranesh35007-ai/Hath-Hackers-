import streamlit as st


def apply_theme():
    st.markdown("""
    <style>
    /* ===== NEON DARK THEME ===== */
    :root {
        --bg: #070B16;
        --navy: #0B1020;
        --panel: #10182B;
        --cyan: #00F5FF;
        --blue: #367BFF;
        --purple: #A855F7;
        --pink: #FF38B8;
        --green: #00FFB2;
        --ink: #F0F6FF;
        --muted: #91A3BD;
        --border: rgba(0,245,255,.18);
    }

    /* ===== MAIN BACKGROUND ===== */
    .stApp {
        background:
            radial-gradient(ellipse at 10% 10%,
                rgba(0,245,255,.09), transparent 35%),
            radial-gradient(ellipse at 90% 15%,
                rgba(168,85,247,.12), transparent 35%),
            radial-gradient(ellipse at 50% 100%,
                rgba(54,123,255,.08), transparent 45%),
            #070B16;
        color: var(--ink);
    }

    /* ===== MAIN CONTENT ===== */
    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    /* ===== HEADINGS ===== */
    h1, h2, h3, h4 {
        color: #F0F6FF !important;
        letter-spacing: -.035em;
    }

    h1 {
        text-shadow: 0 0 22px rgba(0,245,255,.22);
    }

    p, label, .stMarkdown, li {
        color: #D4E0F2;
    }

    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background:
            radial-gradient(ellipse at 0% 0%,
                rgba(0,245,255,.13), transparent 45%),
            linear-gradient(180deg,#0B1020 0%,#10152A 55%,#11102A 100%);
        border-right: 1px solid rgba(0,245,255,.28);
        box-shadow: 5px 0 30px rgba(0,245,255,.06);
    }

    [data-testid="stSidebar"] * {
        color: #EAF5FF;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
    }

    .side-brand {
        font-size: 1.28rem;
        font-weight: 950;
        letter-spacing: 2px;
        padding: 12px 0 20px;
        color: #FFFFFF;
        text-shadow: 0 0 15px rgba(0,245,255,.55);
    }

    .side-brand span {
        color: var(--cyan);
        text-shadow: 0 0 12px var(--cyan);
    }

    .side-brand small {
        display: block;
        font-size: .62rem;
        letter-spacing: 3px;
        color: #91A3BD;
        margin-top: 5px;
        font-weight: 600;
    }

    /* ===== METRIC CARDS ===== */
    [data-testid="stMetric"] {
        background: linear-gradient(
            145deg,
            rgba(19,29,51,.96),
            rgba(11,17,34,.96)
        );
        border: 1px solid rgba(0,245,255,.24);
        padding: 18px 20px;
        border-radius: 16px;
        box-shadow:
            0 0 12px rgba(0,245,255,.06),
            inset 0 0 18px rgba(0,245,255,.025);
        transition: all .25s ease;
    }

    [data-testid="stMetric"]:hover {
        border-color: var(--cyan);
        transform: translateY(-3px);
        box-shadow:
            0 0 10px rgba(0,245,255,.2),
            0 0 28px rgba(0,245,255,.10);
    }

    [data-testid="stMetricLabel"] {
        color: #91A3BD !important;
    }

    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        text-shadow: 0 0 12px rgba(0,245,255,.25);
    }

    [data-testid="stMetricDelta"] {
        color: var(--green) !important;
    }

    /* ===== GLASS PANELS ===== */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(16,24,43,.72);
        border: 1px solid rgba(0,245,255,.17) !important;
        border-radius: 18px !important;
        box-shadow:
            0 8px 32px rgba(0,0,0,.24),
            inset 0 0 20px rgba(0,245,255,.025);
        backdrop-filter: blur(14px);
    }

    /* ===== BUTTONS ===== */
    .stButton > button,
    .stDownloadButton > button {
        background: linear-gradient(
            110deg,
            #111B30,
            #17233C
        );
        color: #EAFBFF !important;
        border: 1px solid rgba(0,245,255,.4);
        border-radius: 11px;
        font-weight: 700;
        padding: .55rem 1.1rem;
        transition: all .22s ease;
        box-shadow: 0 0 10px rgba(0,245,255,.04);
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        border-color: var(--cyan);
        color: var(--cyan) !important;
        transform: translateY(-2px);
        box-shadow:
            0 0 12px rgba(0,245,255,.25),
            0 0 28px rgba(0,245,255,.12);
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(
            100deg,
            #1769FF,
            #00BFCB,
            #8B5CF6
        );
        color: #FFFFFF !important;
        border: 0;
        box-shadow:
            0 0 15px rgba(0,245,255,.22),
            0 0 30px rgba(54,123,255,.12);
    }

    .stButton > button[kind="primary"]:hover {
        filter: brightness(1.2);
        box-shadow:
            0 0 18px rgba(0,245,255,.42),
            0 0 35px rgba(168,85,247,.22);
    }

    /* ===== INPUT FIELDS ===== */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    .stDateInput input {
        background: #0B1222 !important;
        color: #F0F6FF !important;
        border: 1px solid rgba(0,245,255,.25) !important;
        border-radius: 10px !important;
    }

    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stTextArea textarea:focus {
        border-color: var(--cyan) !important;
        box-shadow: 0 0 12px rgba(0,245,255,.18) !important;
    }

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #71839E !important;
    }

    /* ===== SELECT BOX ===== */
    [data-baseweb="select"] > div {
        background: #10182B !important;
        border-color: rgba(0,245,255,.25) !important;
        color: #F0F6FF !important;
        border-radius: 10px !important;
    }

    [data-baseweb="popover"],
    [data-baseweb="menu"] {
        background: #10182B !important;
        border: 1px solid rgba(0,245,255,.3) !important;
    }

    [role="option"] {
        color: #EAF5FF !important;
    }

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 1px solid rgba(0,245,255,.18);
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(16,24,43,.75);
        color: #A9B9D0 !important;
        border-radius: 10px 10px 0 0;
        padding: 10px 18px;
    }

    .stTabs [aria-selected="true"] {
        color: var(--cyan) !important;
        border-bottom: 2px solid var(--cyan) !important;
        text-shadow: 0 0 10px rgba(0,245,255,.5);
    }

    /* ===== DATAFRAMES ===== */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(0,245,255,.2);
        border-radius: 12px;
        overflow: hidden;
    }

    /* ===== FILE UPLOADER ===== */
    [data-testid="stFileUploader"] {
        background: rgba(13,21,39,.8);
        border: 1px dashed rgba(0,245,255,.45);
        border-radius: 14px;
        padding: 12px;
        box-shadow: inset 0 0 20px rgba(0,245,255,.025);
    }

    [data-testid="stFileUploader"] section {
        background: transparent;
    }

    /* ===== LOGIN CARD ===== */
    .login-card {
        max-width: 720px;
        margin: 3rem auto 1rem;
        padding: 34px;
        border-radius: 24px;
        background:
            radial-gradient(ellipse at 5% 5%,
                rgba(0,245,255,.16), transparent 45%),
            radial-gradient(ellipse at 95% 90%,
                rgba(168,85,247,.18), transparent 45%),
            linear-gradient(135deg,#10182B,#11152C);
        border: 1px solid rgba(0,245,255,.38);
        color: white;
        box-shadow:
            0 0 20px rgba(0,245,255,.12),
            0 0 65px rgba(54,123,255,.09),
            inset 0 0 30px rgba(0,245,255,.035);
    }

    .login-card h1 {
        color: #FFFFFF !important;
        margin: .5rem 0;
        text-shadow:
            0 0 10px rgba(0,245,255,.6),
            0 0 30px rgba(0,245,255,.18);
    }

    .login-card p {
        color: #B8C9DF;
    }

    .login-brand {
        color: var(--cyan);
        letter-spacing: 4px;
        font-weight: 900;
        font-size: .85rem;
        text-shadow: 0 0 12px rgba(0,245,255,.7);
    }

    /* ===== CHECKBOX / RADIO ===== */
    [data-testid="stCheckbox"] label,
    [data-testid="stRadio"] label {
        color: #DCE8F8 !important;
    }

    /* ===== EXPANDERS ===== */
    [data-testid="stExpander"] {
        background: rgba(16,24,43,.8);
        border: 1px solid rgba(0,245,255,.18);
        border-radius: 14px;
    }

    /* ===== ALERTS ===== */
    [data-testid="stAlert"] {
        background: rgba(16,24,43,.92);
        border: 1px solid rgba(0,245,255,.24);
        border-radius: 12px;
        color: #EAF5FF;
    }

    /* ===== PROGRESS ===== */
    .stProgress > div > div > div {
        background: linear-gradient(
            90deg,
            #1769FF,
            #00F5FF,
            #A855F7
        );
        box-shadow: 0 0 12px rgba(0,245,255,.55);
    }

    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #080D19;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(
            180deg,#00F5FF,#8B5CF6
        );
        border-radius: 10px;
    }

    /* ===== ANIMATED NEON ACCENT ===== */
    @keyframes neonPulse {
        0%, 100% {
            box-shadow: 0 0 8px rgba(0,245,255,.12);
        }
        50% {
            box-shadow: 0 0 18px rgba(0,245,255,.28);
        }
    }

    .neon-panel {
        border: 1px solid rgba(0,245,255,.35);
        border-radius: 16px;
        animation: neonPulse 3s ease-in-out infinite;
    }

    /* ===== HIDE STREAMLIT CHROME ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    </style>
    """, unsafe_allow_html=True)
