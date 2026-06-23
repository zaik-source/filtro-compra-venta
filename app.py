import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import requests
from textblob import TextBlob
from datetime import datetime
from dateutil.relativedelta import relativedelta
import warnings
warnings.filterwarnings('ignore')
import logging
logging.getLogger("yfinance").setLevel(logging.CRITICAL)
logging.getLogger("peewee").setLevel(logging.CRITICAL)

st.set_page_config(
    page_title="Swing Screener",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@400;600;800&family=IBM+Plex+Mono:wght@300;400;600;700&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'JetBrains Mono', monospace; }
    .stApp { background-color: #0a0e1a; color: #e0e6f0; }
    [data-testid="stSidebar"] { background-color: #0d1220; border-right: 1px solid #1e2d4a; }
    [data-testid="stSidebar"] * { color: #c8d4e8 !important; }

    .main-header { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 2.2rem;
                   color: #4fc3f7; letter-spacing: -0.02em; margin-bottom: 0; line-height: 1.1; }
    .sub-header { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #4a6080;
                  letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 1.5rem; }
    .metric-card { background: linear-gradient(135deg, #0f1828 0%, #121e30 100%);
                   border: 1px solid #1a2d45; border-radius: 8px; padding: 1rem 1.2rem; text-align: center; }
    .metric-value { font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800; line-height: 1; }
    .metric-label { font-size: 0.7rem; letter-spacing: 0.1em; text-transform: uppercase;
                    color: #4a6080; margin-top: 0.3rem; }

    /* ── Screener table ── */
    .screener-table { width: 100%; border-collapse: collapse; font-size: 0.78rem;
                      font-family: 'JetBrains Mono', monospace; }
    .screener-table th { background-color: #0d1828; color: #4a7aaa; font-size: 0.68rem;
                         letter-spacing: 0.1em; text-transform: uppercase; padding: 0.6rem 0.8rem;
                         border-bottom: 1px solid #1a2d45; text-align: right; white-space: nowrap; }
    .screener-table th:first-child, .screener-table th:nth-child(2) { text-align: left; }
    .screener-table td { padding: 0.5rem 0.8rem; border-bottom: 1px solid #111c2d;
                         text-align: right; color: #c0ccd8; white-space: nowrap; }
    .screener-table td:first-child, .screener-table td:nth-child(2) { text-align: left; }
    .screener-table tr:hover td { background-color: #0f1e30; }

    /* ── Ticker badge — clickable ── */
    .ticker-badge {
        background-color: #1a2d45; color: #4fc3f7; padding: 0.15rem 0.45rem;
        border-radius: 4px; font-weight: 600; font-size: 0.75rem; letter-spacing: 0.05em;
        cursor: pointer; transition: background 0.15s, color 0.15s;
        border: 1px solid transparent;
    }
    .ticker-badge:hover {
        background-color: #4fc3f7; color: #0a0e1a;
        border-color: #4fc3f7;
    }
    .ticker-badge.active {
        background-color: #00e676; color: #0a0e1a;
        border-color: #00e676;
    }

    .signal-buy    { color: #00e676; font-weight: 700; font-size: 0.75rem; }
    .signal-sell   { color: #ff5252; font-weight: 700; font-size: 0.75rem; }
    .signal-neutral{ color: #ffd740; font-weight: 600; font-size: 0.75rem; }
    .rsi-oversold  { color: #00e676; font-weight: 600; }
    .rsi-overbought{ color: #ff5252; font-weight: 600; }
    .rsi-neutral   { color: #ffd740; }
    .pct-pos { color: #00e676; }
    .pct-neg { color: #ff5252; }
    .vol-high{ color: #00e676; }
    .vol-low { color: #ff5252; }
    .macd-cross-up   { color: #00e676; font-weight: 700; }
    .macd-cross-down { color: #ff5252; font-weight: 700; }
    .macd-above      { color: #69f0ae; }
    .macd-below      { color: #ff8a80; }

    .stRadio > div { gap: 0.3rem; }
    .stButton > button { background: linear-gradient(135deg, #1565c0, #1976d2); color: white;
                         border: none; border-radius: 6px; font-family: 'JetBrains Mono', monospace;
                         font-weight: 600; font-size: 0.8rem; letter-spacing: 0.08em;
                         padding: 0.6rem 1.2rem; width: 100%; transition: all 0.2s; }
    .stButton > button:hover { background: linear-gradient(135deg, #1976d2, #2196f3); transform: translateY(-1px); }
    hr { border-color: #1a2d45; margin: 1rem 0; }
    .stSelectbox > div > div { background-color: #0d1828; border-color: #1a2d45; color: #c8d4e8; }
    .stSlider > div > div > div { background-color: #1976d2; }
    .info-box { background-color: #0d1e30; border-left: 3px solid #4fc3f7; padding: 0.6rem 1rem;
                border-radius: 0 6px 6px 0; font-size: 0.75rem; color: #7090b0; margin-bottom: 1rem; }
    .filter-bar { background: linear-gradient(135deg, #0d1828 0%, #101e30 100%);
                  border: 1px solid #1a2d45; border-radius: 8px;
                  padding: 0.9rem 1.2rem 0.6rem 1.2rem; margin: 1rem 0 0.5rem 0; }
    .filter-title { font-size:0.68rem; letter-spacing:0.14em; text-transform:uppercase;
                    color:#4a7aaa; margin-bottom:0.6rem; }
    .result-count { font-size:0.72rem; color:#4a7aaa; letter-spacing:0.08em; margin-bottom:0.5rem; }

    /* ── Terminal panel ── */
    .terminal-panel {
        background: linear-gradient(135deg, #0a0e1a 0%, #0d1421 100%);
        border: 1px solid #00b4d8;
        border-radius: 8px;
        padding: 1.5rem;
        margin-top: 1.5rem;
    }
    .terminal-panel-header {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem; letter-spacing: 3px; color: #00b4d8;
        text-transform: uppercase; border-bottom: 1px solid #1e3a5f;
        padding-bottom: 0.5rem; margin-bottom: 1.2rem;
    }
    .term-metric-card {
        background: linear-gradient(135deg, #0d1421, #111827);
        border: 1px solid #1e3a5f; border-radius: 6px;
        padding: 0.9rem 1rem; margin-bottom: 0.6rem; position: relative;
    }
    .term-metric-card::before {
        content: ''; position: absolute; top: 0; left: 0;
        width: 3px; height: 100%; background: #00b4d8;
        border-radius: 3px 0 0 3px;
    }
    .term-metric-label {
        font-family: 'IBM Plex Mono', monospace; font-size: 0.62rem;
        color: #4a6fa5; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 0.25rem;
    }
    .term-metric-value { font-family: 'IBM Plex Mono', monospace; font-size: 1.2rem; font-weight: 700; color: #e2e8f0; }
    .term-metric-value.positive { color: #00e676; }
    .term-metric-value.negative { color: #ff5252; }
    .term-metric-value.neutral  { color: #ffd740; }
    .term-metric-sub { font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; color: #64748b; margin-top: 0.15rem; }
    .term-section-header {
        font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem;
        letter-spacing: 3px; color: #00b4d8; text-transform: uppercase;
        border-bottom: 1px solid #1e3a5f; padding-bottom: 0.4rem; margin: 1.2rem 0 0.8rem 0;
    }
    .levels-table { width:100%; border-collapse:collapse; font-family:'IBM Plex Mono',monospace; font-size:0.75rem; }
    .levels-table th { color:#4a6fa5; font-weight:400; text-transform:uppercase; letter-spacing:2px;
                       padding:0.4rem 0.6rem; border-bottom:1px solid #1e3a5f; text-align:left; }
    .levels-table td { padding:0.4rem 0.6rem; border-bottom:1px solid #0d1421; }
    .lvl-soporte    { color:#00e676; }
    .lvl-resistencia{ color:#ff5252; }
    .warn-box { background: rgba(255,215,64,0.08); border: 1px solid #ffd740;
                border-radius: 4px; padding: 0.8rem 1rem; margin: 0.5rem 0;
                font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; color: #ffd740; }
    .click-hint {
        font-size: 0.68rem; color: #4a6080; letter-spacing: 0.1em;
        text-align: center; margin: 0.4rem 0 0.8rem 0;
        font-family: 'JetBrains Mono', monospace;
    }
    .sentiment-badge {
        display: inline-block; padding: 0.25rem 0.6rem;
        border-radius: 3px; font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem; font-weight: 600; letter-spacing: 1px;
    }
    .sent-positive { background: rgba(0,230,118,0.15); color: #00e676; border: 1px solid #00e676; }
    .sent-negative { background: rgba(255,82,82,0.15);  color: #ff5252; border: 1px solid #ff5252; }
    .sent-neutral  { background: rgba(255,215,64,0.15); color: #ffd740; border: 1px solid #ffd740; }
    .score-bar-bg { background: #1e3a5f; border-radius: 3px; height: 8px; margin-top: 4px; overflow: hidden; }
    .score-bar-fill { height: 100%; border-radius: 3px; background: linear-gradient(90deg, #0077b6, #00b4d8); }
    .score-row { display: flex; align-items: center; padding: 0.45rem 0; border-bottom: 1px solid #1a2a3a; }
    .score-name { font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; color: #8eacc8; width: 120px; flex-shrink: 0; }
    .score-num { font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; font-weight: 700; color: #00b4d8; width: 45px; text-align: right; flex-shrink: 0; margin-right: 10px; }
    .score-bar-wrap { flex: 1; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# TICKERS POR SECTOR
# ══════════════════════════════════════════════════════════════════════════

SECTORES = {
    "Communication Services": [
        "ACCS", "AD", "ADV", "AENT", "AGAE", "AMC", "AMCX", "AMX", "ANGH", "ANGI",
        "APP", "AREN", "ATEX", "ATHM", "ATNI", "BATRA", "BATRK", "BCE", "BIDU", "BILI",
        "BMBL", "BZ", "CABO", "CARS", "CAST", "CHTR", "CMCSA", "CNK", "DIS", "DJT",
        "DV", "EA", "EVC", "EVER", "FOX", "FOXA", "FUBO", "FVRR", "FWONA", "FWONK",
        "GOOG", "GOOGL", "GRPN", "GSAT", "GTN", "IAC", "IDT", "IHRT", "IMAX", "IQ",
        "IRDM", "JOYY", "KT", "LBRDA", "LBRDK", "LBTYA", "LBTYK", "LEE", "LILA", "LILAK",
        "LUMN", "LYV", "MANU", "MAX", "META", "MGNI", "MOMO", "MTCH", "NFLX", "NTES",
        "NWS", "NWSA", "NXST", "NYT", "OMC", "PINS", "PLAY", "PLTK", "RDDT", "RBLX",
        "RCI", "ROKU", "RUM", "SATS", "SBGI", "SIRI", "SNAP", "SPOT", "SSP", "T",
        "TBLA", "TDS", "TEO", "TIGO", "TIMB", "TKO", "TLK", "TME", "TMUS", "TTD",
        "TTWO", "TU", "TV", "TZOO", "UPWK", "VEON", "VIV", "VOD", "VZ", "WB",
        "WBD", "WMG", "WPP", "YELP", "Z", "ZD", "ZG", "ZH", "ZIP",
    ],
    "Technology": [
        "AAOI", "AAPL", "ACIW", "ACLS", "ACMR", "ACN", "ADBE", "ADI", "ADP", "ADSK",
        "ADTN", "AEHR", "AI", "AKAM", "ALAB", "ALGM", "AMD", "AMKR", "ANET", "APH",
        "APPF", "APPN", "ARBE", "ARM", "ARQQ", "ARW", "ASAN", "ASML", "ASTS", "AVGO",
        "BB", "BBAI", "BDC", "BILL", "BLKB", "BLND", "BLZE", "BMI", "BOX", "BR",
        "BRZE", "BSY", "CACI", "CALX", "CAMT", "CDNS", "CDW", "CEVA", "CGNX", "CHKP",
        "CIEN", "CLBT", "CLFD", "CLMB", "CLS", "CLVT", "CNDT", "CNXC", "COHR", "COHU",
        "CORZ", "CPAY", "CRDO", "CRM", "CRWD", "CRWV", "CSCO", "CSGS", "CSIQ", "CTSH",
        "CVLT", "CWAN", "CXM", "DDOG", "DELL", "DFIN", "DGII", "DLO", "DOCN", "DOCU",
        "DOMO", "DOX", "DQ", "DSGX", "DSP", "DT", "DUOL", "DXC", "EEFT", "EGAN",
        "EGHT", "ENTG", "EPAM", "ERIC", "ESE", "ESTC", "EVCM", "EVTC", "EXLS", "EXOD",
        "EXTR", "FFIV", "FICO", "FIS", "FISV", "FIVN", "FLEX", "FLYW", "FN", "FORM",
        "FOUR", "FRSH", "FSLR", "FSLY", "FTNT", "FTV", "G", "GDDY", "GDS", "GEN",
        "GFS", "GLOB", "GLW", "GPN", "GPRO", "GRAB", "GRMN", "GTLB", "GWRE", "HIMX",
        "HPE", "HPQ", "HUBS", "IBM", "ICHR", "IDCC", "IFBD", "III", "IIIV", "IMMR",
        "IMOS", "INFY", "INGM", "INLX", "INOD", "INSG", "INTA", "INTC", "INTU", "INTZ",
        "INUV", "IONQ", "IOT", "IPGP", "IT", "ITRI", "JBL", "JKHY", "JKS", "KEYS",
        "KLAC", "KLIC", "KLTR", "KSPI", "KVYO", "LASR", "LAW", "LDOS", "LFUS", "LITE",
        "LOGI", "LPL", "LPSN", "LRCX", "LSCC", "LSPD", "LTRX", "LYFT", "MANH", "MCHP",
        "MDB", "MKSI", "MNDY", "MPWR", "MQ", "MRVL", "MSFT", "MSI", "MSTR", "MTC",
        "MTLS", "MTSI", "MU", "MXL", "NABL", "NBIS", "NCNO", "NET", "NICE", "NOK",
        "NOVT", "NOW", "NTAP", "NTCT", "NTGR", "NTNX", "NVDA", "NVEC", "NVMI", "NVTS",
        "NXPI", "NXT", "OKTA", "ON", "ONTO", "OOMA", "ORCL", "OTEX", "PANW", "PAR",
        "PATH", "PAY", "PAYC", "PAYX", "PCOR", "PCTY", "PD", "PDFS", "PEGA", "PLTR",
        "PLXS", "POWI", "PRGS", "PRTH", "PSFE", "PSN", "PTC", "QBTS", "QCOM", "QLYS",
        "QMCO", "QTWO", "QUBT", "RBRK", "RDWR", "RFMZ", "RGTI", "RMBS", "RMNI", "RNG",
        "ROP", "RPD", "RTB", "SABR", "SAIC", "SANM", "SAP", "SCOR", "SEDG", "SHOP",
        "SILC", "SIMO", "SITM", "SLAB", "SMCI", "SMTC", "SNDK", "SNOW", "SNPS", "SNX",
        "SOUN", "SPSC", "SPT", "SQNS", "SRAD", "SSNC", "SSYS", "STM", "STNE", "STX",
        "SWKS", "SYNA", "TASK", "TDC", "TDY", "TEAM", "TEL", "TENB", "TER", "TLS",
        "TOST", "TRMB", "TSM", "TTMI", "TWLO", "TXN", "TYL", "U", "UBER", "UCTT",
        "UI", "UIS", "UMC", "UPLD", "USIO", "VECO", "VERI", "VERX", "VIAV", "VICR",
        "VNET", "VNT", "VRNS", "VRRM", "VRSN", "VSAT", "VSH", "VTEX", "WDAY", "WDC",
        "WEX", "WIT", "WIX", "WK", "WLDS", "WRD", "XPER", "XYZ", "YEXT", "YMM",
        "ZBRA", "ZETA", "ZM", "ZS",
    ],
    "Consumer Cyclical": [
        "AAP", "ABG", "ABNB", "AEO", "ALSN", "ALV", "AMZN", "AN", "ANF", "APTV",
        "ARCO", "AS", "ASO", "AZO", "BABA", "BALY", "BARK", "BBWI", "BBY", "BC",
        "BKNG", "BLMN", "BOOT", "BURL", "BWA", "BWMX", "BYD", "BZH", "CAKE", "CAL",
        "CARG", "CART", "CASY", "CATO", "CAVA", "CBRL", "CCL", "CMG", "COLM", "CPNG",
        "CPRI", "CRI", "CRMT", "CROX", "CVNA", "CZR", "DAN", "DASH", "DBI", "DDS",
        "DECK", "DFH", "DHI", "DIN", "DKNG", "DKS", "DPZ", "DRI", "DRVN", "EAT",
        "EBAY", "ETSY", "EXPE", "F", "FIVE", "FLUT", "FND", "FNKO", "FOXF", "FUN",
        "GAP", "GBTG", "GCO", "GIII", "GIL", "GLBE", "GM", "GME", "GNTX", "GOLF",
        "GOOS", "GPC", "GPI", "GT", "H", "HAS", "HD", "HGV", "HLT", "HMC",
        "HOG", "HRB", "HTHT", "HZO", "IBP", "IHG", "JACK", "JD", "JILL", "JOUT",
        "KBH", "KMX", "KSS", "LAD", "LCID", "LCII", "LEA", "LEG", "LEN", "LESL",
        "LEVI", "LI", "LKQ", "LOCO", "LOW", "LTH", "LULU", "LVS", "LZB", "M",
        "MAR", "MAT", "MBC", "MBLY", "MCD", "MCRI", "MCW", "MED", "MELI", "MGA",
        "MGM", "MHK", "MHO", "MLCO", "MLKN", "MNSO", "MOV", "MTH", "MTN", "MUSA",
        "NCI", "NCL", "NCLH", "NDLS", "NIO", "NIU", "NKE", "NVR", "ONON", "ORLY",
        "OXM", "PAG", "PDD", "PENN", "PETZ", "PHM", "PII", "PLBL", "PLNT", "PRKS",
        "PRTS", "PTON", "PVH", "PZZA", "QSR", "RACE", "RCKY", "RCL", "REAL", "RENT",
        "RGS", "RH", "RICK", "RIVN", "RL", "ROL", "ROST", "RRR", "RUSHA", "RVLV",
        "SAH", "SBUX", "SCI", "SE", "SFIX", "SG", "SHAK", "SHOO", "SIG", "SKY",
        "SMP", "SNBR", "STLA", "TJX", "TM", "TMHC", "TNL", "TOL", "TOUR", "TPR",
        "TRIP", "TSCO", "TSLA", "TXRH", "UA", "UAA", "ULTA", "URBN", "VAC", "VC",
        "VFC", "VIK", "VIPS", "VRA", "VSCO", "VVV", "W", "WEN", "WEYS", "WGO",
        "WH", "WHR", "WING", "WSM", "WWW", "WYNN", "XPEV", "YETI", "YUM", "YUMC",
        "ZUMZ",
    ],
    "Consumer Defensive": [
        "ABEV", "ADM", "ACI", "AVO", "BF-B", "BG", "BGS", "BJ", "BRBR", "BTI",
        "BUD", "BYND", "CAG", "CALM", "CCEP", "CELH", "CHD", "CL", "CLX", "COCO",
        "COST", "CPB", "DAR", "DEO", "DG", "DLTR", "DNUT", "DOLE", "EL", "ELF",
        "EPC", "FIZZ", "FLO", "FMX", "FRPT", "GIS", "GO", "HAIN", "HELE", "HLF",
        "HNST", "HRL", "HSY", "INGR", "IPAR", "JBS", "JBSS", "JJSF", "KDP", "KHC",
        "KMB", "KO", "KOF", "KR", "KVUE", "LW", "LWAY", "MDLZ", "MKC", "MNST",
        "MO", "NATR", "NGVC", "NOMD", "NUS", "OLLI", "OTLY", "PEP", "PFGC", "PG",
        "PM", "POST", "PPC", "PSMT", "SAM", "SENEA", "SFD", "SFM", "SJM", "SMPL",
        "SPB", "STZ", "SYY", "TAP", "TGT", "TPB", "TR", "TSN", "UL", "UNFI",
        "USFD", "USNA", "UTZ", "UVV", "VFF", "WMK", "WMT",
    ],
    "Energy": [
        "AESI", "AM", "APA", "AR", "ARLP", "AROC", "BKR", "BKV", "BP", "BSM",
        "BTE", "BTU", "CCJ", "CHRD", "CLB", "CLNE", "CNQ", "CNX", "COP", "CQP",
        "CRC", "CRGY", "CRK", "CTRA", "CVE", "CVI", "CVX", "DHT", "DINO", "DK",
        "DKL", "DNN", "DTM", "DVN", "E", "EC", "EE", "ENB", "EOG", "EPD",
        "EQNR", "EQT", "ET", "EXE", "FANG", "FET", "FTI", "GEL", "GEOS", "GLP",
        "GPOR", "GTE", "HAL", "HLX", "HP", "IEP", "IMO", "INSW", "KMI", "KLXE",
        "KOS", "KRP", "LBRT", "LEU", "LNG", "LPG", "MGY", "MPC", "MPLX", "MTDR",
        "MUR", "NAT", "NBR", "NE", "NESR", "NFE", "NFG", "NGL", "NOG", "NOV",
        "NXE", "OII", "OKE", "OVV", "OXY", "PAA", "PAGP", "PARR", "PBF", "PBR",
        "PSX", "PTEN", "PUMP", "RIG", "RNGR", "RRC", "SBR", "SD", "SDRL", "SEI",
        "SHEL", "SJT", "SLB", "SM", "SND", "STNG", "SU", "SUN", "TALO", "TDW",
        "TGS", "TK", "TNK", "TPL", "TRGP", "TRP", "TS", "TTE", "UEC", "UGP",
        "URG", "UROY", "USAC", "VAL", "VET", "VLO", "VNOM", "VOC", "WDS", "WES",
        "WFRD", "WHD", "WMB", "WTI", "WTTR", "XOM", "YPF",
    ],
    "Financial": [
        "AB", "AFCG", "AMG", "AMP", "APAM", "APO", "ARCC", "ARES", "BAC", "BAM",
        "BBVA", "BCS", "BEN", "BLK", "BN", "BNS", "BNY", "BX", "BXSL", "C",
        "CBOE", "CG", "CINF", "CME", "COIN", "CNA", "COF", "CRD-A", "DB", "ERIE",
        "EVR", "FDS", "FG", "FHI", "GS", "HSBC", "HIG", "HOOD", "HTGC", "IBKR",
        "ICE", "ING", "IVZ", "JEF", "JHG", "JPM", "KKR", "L", "LAZ", "LNC",
        "LMND", "LPLA", "MA", "MAIN", "MARA", "MET", "MFC", "MKL", "MKTX", "MCO",
        "MRX", "MS", "MSCI", "NDAQ", "NLY", "NMFC", "NMR", "OBDC", "OWL", "PGR",
        "PNC", "PRU", "PSEC", "PYPL", "RJF", "RIOT", "RKT", "RLI", "RY", "RYAN",
        "SAN", "SCHW", "SEIC", "SF", "SMFG", "SOFI", "SPGI", "STC", "STT", "SYF",
        "TD", "TFC", "TROW", "TRV", "TW", "UBS", "USB", "V", "VIRT", "VOYA",
        "WAL", "WBS", "WFC", "WTW", "XP", "ZION",
    ],
    "ETFs": [
        "SPY", "VOO", "IVV", "QQQ", "QQQM", "IWM", "TLT", "GLD", "AGG", "IAU",
        "IAT", "IBB", "IGV", "IWB", "IWD", "IWF", "IWO", "IWR", "IWS", "IWV",
        "IXC", "IYF", "IYH", "IYK", "IYM", "IYR", "IYT", "IYW", "JETS", "KRE",
        "KWEB", "LIT", "LQD", "MBB", "MCHI", "MDY", "MTUM", "MUB", "NOBL",
        "OEF", "OIH", "QAT", "QCLN", "ROBO", "SCHA", "SCHB", "SCHD", "SCHE",
        "SCHF", "SCHG", "SCHH", "SCHM", "SCHV", "SCHX", "SDY", "SHV", "SHY",
        "SIL", "SKYY", "SLV", "SMH", "SOXX", "SPIB", "SPLG", "SPYD", "SPYG",
        "SPYV", "TAN", "TIP", "UNG", "URA", "USMV", "USO", "VAW", "VB", "VBK",
        "VBR", "VCIT", "VCR", "VCSH", "VDC", "VDE", "VEA", "VFH", "VGK", "VGT",
        "VHT", "VIG", "VIS", "VNQ", "VTI", "VTV", "VUG", "VXUS", "XAR", "XBI",
        "XLB", "XLC", "XLE", "XLF", "XLI", "XLK", "XLP", "XLRE", "XLU", "XLV",
        "XLY", "XOP",
    ],
    "Healthcare": [
        "ABBV", "ABCL", "ABEO", "ABT", "ACAD", "ACRS", "ADMA", "ADUS", "AGEN",
        "AGIO", "ALGN", "ALKS", "ALNY", "AMGN", "AMLX", "AMN", "ANAB", "ANGO",
        "ANIP", "ANTX", "APLS", "ARAY", "ARCT", "ARDX", "ARGX", "ARQT", "ARVN",
        "ARWR", "ASND", "ASRT", "ATAI", "ATEC", "ATRA", "ATRC", "AUPH", "AVNS",
        "AVTR", "AVXL", "AXGN", "AXSM", "AZN", "AZTA", "BAX", "BBIO", "BCRX",
        "BDX", "BEAM", "BHVN", "BIIB", "BIO", "BLCO", "BLFS", "BLRX", "BLTE",
        "BMRN", "BMY", "BNGO", "BNTX", "BRKR", "BSX", "BTAI", "BTMD", "CAH",
        "CAMP", "CANF", "CAPR", "CATX", "CCCC", "CCEL", "CDNA", "CELC", "CERS",
        "CHE", "CHRS", "CI", "CLDX", "CLLS", "CLOV", "CLRB", "CMPS", "CNC",
        "CNMD", "CNSP", "CNTX", "COO", "COR", "CORT", "COT", "CPHI", "CPRX",
        "CRBU", "CRDF", "CRDL", "CRIS", "CRL", "CRMD", "CRNX", "CRSP", "CRVS",
        "CSTL", "CTMX", "CVS", "CYTK", "DGX", "DHR", "DNLI", "DOCS", "DRIO",
        "DXCM", "DYN", "EBS", "EDIT", "ELAN", "ELMD", "ELV", "EMBC", "ENGN",
        "ENOV", "ENSG", "ENTA", "EVGN", "EVH", "EVO", "EW", "EXEL", "FATE",
        "FBIO", "FBRX", "FDMT", "FEMY", "FHTX", "FLGT", "FMS", "FTRE", "FULC",
        "GANX", "GDRX", "GEHC", "GERN", "GH", "GHRS", "GILD", "GKOS", "GMAB",
        "GMED", "GNLX", "GOVX", "GPCR", "GRAL", "GSK", "HAE", "HALO", "HCA",
        "HCAT", "HCSG", "HIMS", "HLN", "HQY", "HRMY", "HROW", "HRTX", "HSIC",
        "HUM", "IART", "ICLR", "ICUI", "IDXX", "IDYA", "ILMN", "IMCR", "IMMP",
        "IMNM", "IMRX", "IMTX", "IMVT", "INABS", "INBS", "INCR", "INCY", "INDP",
        "INFU", "INGN", "INO", "INSM", "INSP", "IONS", "IOVA", "IQV", "IRTC",
        "IRWD", "ISRG", "JAGX", "JAZZ", "JNJ", "JYNT", "KALV", "KIDS", "KNSA",
        "KOD", "KPRX", "KPTI", "KRYS", "KURA", "KYMR", "LH", "LGND", "LGVN",
        "LLY", "LMAT", "LNTH", "LQDA", "LSTA", "LYEL", "MAIA", "MANE", "MASI",
        "MAZE", "MBIO", "MBOT", "MCK", "MCRB", "MD", "MDGL", "MDT", "MEDP",
        "MESO", "MGNX", "MGTX", "MIRM", "MMSI", "MNKD", "MNOV", "MOH", "MOLN",
        "MRK", "MRNA", "MRVI", "MTD", "MYGN", "MYO", "NBIX", "NBTX", "NCEL",
        "NEO", "NEOG", "NERV", "NGNE", "NHC", "NKTR", "NKTX", "NMRA", "NNOX",
        "NTLA", "NTRA", "NUVL", "NVAX", "NVCR", "NVO", "NVS", "NVST", "NXTC",
        "OCGN", "OCUL", "OFIX", "OGN", "OMCL", "OMER", "OPCH", "OPK", "ORGO",
        "ORIC", "ORMP", "OSCR", "OSUR", "OTLK", "OVID", "PACB", "PACS", "PAHC",
        "PARK", "PASG", "PBH", "PCVX", "PEN", "PEPG", "PETS", "PFE", "PGEN",
        "PGNY", "PHG", "PHR", "PLSE", "PLX", "PODD", "PPBT", "PRAX", "PRCT",
        "PRGO", "PRLD", "PROF", "PRTC", "PRVA", "PTCT", "PTGX", "PTN", "PULM",
        "QDEL", "QGEN", "QNCX", "QURE", "RDNT", "RDY", "REGN", "REPL", "RGEN",
        "RGNT", "RGNX", "RIGL", "RLAY", "RLMD", "RLYB", "RMD", "RMTI", "RNA",
        "ROIV", "RPRX", "RVMD", "RVTY", "RXRX", "RYTM", "RZLT", "SANA", "SDGR",
        "SEER", "SEM", "SENS", "SER", "SERA", "SGHT", "SGMT", "SGRY", "SHC",
        "SIGA", "SION", "SNDX", "SNGX", "SNN", "SNY", "SOLV", "SPOK", "SPRB",
        "SPRC", "SPRO", "SRPT", "SRRK", "STE", "STIM", "STOK", "STRO", "STVN",
        "SUPN", "SYK", "SYRE", "TAK", "TARA", "TARS", "TBPH", "TDOC", "TECH",
        "TELA", "TELO", "TEM", "TEVA", "TFX", "TGTX", "THC", "TLRY", "TMDX",
        "TMO", "TNDM", "TNGX", "TOI", "TPST", "TRAW", "TRDA", "TRVI", "TSHA",
        "TVTX", "TXG", "TYRA", "UFPT", "UHS", "UNH", "URGN", "USPH", "UTHR",
        "VALN", "VBIO", "VCEL", "VCYT", "VEEV", "VERU", "VIR", "VKTX", "VNDA",
        "VOR", "VRTX", "VSTM", "VTRS", "WAT", "WEAV", "WGS", "WST", "WVE",
        "XENE", "XERS", "XFOR", "XNCR", "XOMA", "XRAY", "YI", "ZBH", "ZLAB",
        "ZNTL", "ZTS", "ZURA", "ZVRA", "ZYME",
    ],
    "Industrials": [
        "AAL", "AAON", "ABM", "ACA", "ACCO", "ACHR", "ACM", "ADT", "AER", "AERO",
        "AGCO", "AGX", "AIR", "AIT", "ALG", "ALGT", "ALK", "ALLE", "AME", "AMRC",
        "AMSC", "AMTM", "AOS", "APG", "APOG", "ARCB", "ARMK", "ARQ", "ASC",
        "ASLE", "ASPN", "ASR", "ASTE", "ATI", "ATKR", "ATRO", "ATS", "AVAV",
        "AWI", "AXON", "AYI", "AZZ", "BA", "BAH", "BCO", "BLD", "BLDR", "BNC",
        "BOC", "BOOM", "BRC", "BV", "BW", "BWXT", "BXC", "CAE", "CAR", "CARR",
        "CASS", "CAT", "CBZ", "CDRE", "CECO", "CHRW", "CLH", "CMC", "CMCO",
        "CMI", "CMPR", "CMRE", "CNH", "CNI", "CNM", "CODI", "CP", "CPA", "CPRT",
        "CR", "CRAI", "CRS", "CSL", "CSX", "CTAS", "CTRM", "CVR", "CW", "CWST",
        "CXT", "CXW", "DAC", "DAL", "DCI", "DCO", "DE", "DFNS", "DLX", "DNOW",
        "DOV", "DRS", "DSGR", "DSX", "DY", "EAF", "EFX", "EGG", "EH", "EME",
        "EML", "EMR", "ENGS", "ENR", "ENS", "ENVX", "EPAC", "ERII", "ESAB",
        "ESEA", "ESLT", "ESP", "ETN", "ETS", "EXPD", "EXPO", "FAST", "FBIN",
        "FCEL", "FCN", "FDX", "FELE", "FERG", "FIP", "FIX", "FLR", "FLS",
        "FLUX", "FLX", "FLY", "FSS", "FSTR", "FTAI", "FTEK", "FWRD", "GATX",
        "GBX", "GD", "GE", "GEO", "GEV", "GFF", "GFL", "GGG", "GHM", "GIC",
        "GLBS", "GNK", "GNRC", "GP", "GRC", "GSL", "GTES", "GTLS", "GVA", "GWW",
        "GXO", "HAFN", "HAYW", "HEI", "HII", "HLMN", "HON", "HOVR", "HRI",
        "HUBG", "HURC", "HURN", "HWM", "HXL", "HY", "ICFI", "IEX", "IIIN",
        "IR", "ISSC", "ITT", "ITW", "J", "JBHT", "JBLU", "JBTM", "JCI", "JELD",
        "JOBY", "KAI", "KBR", "KELYA", "KEX", "KFRC", "KFY", "KMT", "KNX",
        "KODK", "KRMN", "KRNT", "KTOS", "LASE", "LECO", "LGN", "LGPS", "LHX",
        "LII", "LMB", "LMT", "LNN", "LNZA", "LOAR", "LPX", "LSTR", "LTBR",
        "LTM", "LUNR", "LUV", "LZ", "MAN", "MAS", "MATW", "MATX", "MEC", "MG",
        "MGRC", "MHH", "MIDD", "MIR", "MLI", "MMM", "MMS", "MNTS", "MOG-A",
        "MRCY", "MRTN", "MSA", "MSM", "MTEN", "MTRX", "MTW", "MTZ", "MWA",
        "MYRG", "NDSN", "NNE", "NOC", "NOG", "NOV", "NSC", "NSP", "NSSC",
        "NVRI", "NVT", "OC", "ODFL", "OFAL", "OFLX", "OMAB", "ONT", "OSK",
        "OTIS", "PAC", "PAL", "PAM", "PAMT", "PCAR", "PCT", "PESI", "PH",
        "PKE", "PKOH", "PL", "PLPC", "PLUG", "PNR", "POOL", "POWL", "POWW",
        "PPSI", "PRG", "PRIM", "PRLB", "PWR", "QUAD", "QXO", "R", "RAIL",
        "RAIN", "RBA", "RBC", "RCMT", "RDW", "REZI", "RFIL", "RGP", "RGR",
        "RHI", "RKLB", "ROAD", "ROCK", "ROK", "ROP", "RR", "RRX", "RSG", "RTX",
        "RXO", "RYAAY", "SAIA", "SARO", "SATL", "SB", "SBLK", "SEB", "SERV",
        "SFL", "SGLY", "SHIP", "SHMD", "SIDU", "SIF", "SITE", "SKYW", "SKYX",
        "SLND", "SMHI", "SMR", "SMX", "SNA", "SNCY", "SNDR", "SNT", "SOAR",
        "SPAI", "SPCE", "SPIR", "SPXC", "SST", "STN", "STRL", "SWK", "SXI",
        "SYM", "TATT", "TBI", "TDG", "TE", "TEX", "TFII", "TG", "THR", "TIC",
        "TISI", "TITN", "TKR", "TNC", "TNET", "TOMZ", "TPC", "TPCS", "TRC",
        "TREX", "TRI", "TRN", "TRNS", "TT", "TTC", "TTEK", "TTI", "TWI",
        "TWIN", "TXT", "UAL", "UHAL", "ULH", "ULS", "UNF", "UNP", "UP", "UPS",
        "URI", "VATE", "VLRS", "VLTO", "VMI", "VRSK", "VRT", "VSEC", "WAB",
        "WCC", "WCN", "WERN", "WLDN", "WLFC", "WM", "WMS", "WNC", "WOR", "WSC",
        "WSO", "WTS", "WWD", "XCH", "XE", "XMTR", "XPO", "XRX", "XYL",
        "ZIM", "ZJK", "ZTO", "ZWS",
    ],
    "Real Estate": [
        "AAT", "ABR", "ACR", "ACRE", "ADC", "AGNC", "AHR", "AHT", "AIV", "AKR",
        "ALX", "AMH", "AMT", "APLE", "ARE", "ARI", "ARR", "AVB", "BDN", "BEKE",
        "BFS", "BHR", "BNL", "BRT", "BRX", "BXMT", "BXP", "CBL", "CBRE", "CCI",
        "CDP", "CHCT", "CIM", "CLDT", "CLPR", "COLD", "COMP", "CPT", "CSGP",
        "CTO", "CTRE", "CUBE", "CUZ", "CWK", "DEA", "DEI", "DHC", "DLR", "DOC",
        "DRH", "DX", "EFC", "EGP", "ELME", "ELS", "EPR", "EPRT", "EQIX", "EQR",
        "ESRT", "ESS", "EXR", "FBRT", "FCPT", "FOR", "FPH", "FPI", "FR", "FRT",
        "FSP", "FSV", "FVR", "GIPR", "GLPI", "GNL", "GOOD", "GPMT", "GTY",
        "HIW", "HPP", "HR", "HST", "IHT", "IIPR", "ILPT", "INN", "INVH", "IRM",
        "IRT", "IVR", "IVT", "JBGS", "JLL", "JOE", "KIM", "KRC", "KREF", "KRG",
        "KW", "LADR", "LAMR", "LAND", "LFT", "LPA", "LRE", "LTC", "LXP", "MAA",
        "MAC", "MDV", "MFA", "MITT", "MLP", "MPT", "MRP", "NEN", "NHI", "NHP",
        "NLOP", "NLY", "NMRK", "NNN", "NREF", "NSA", "NTST", "NXRT", "NYC",
        "O", "OHI", "OLP", "ONL", "OPAD", "OPEN", "ORC", "OUT", "PDM", "PEB",
        "PECO", "PINE", "PK", "PLD", "PMT", "PSA", "PSTL", "PW", "RC", "REG",
        "RENX", "REXR", "RHP", "RITM", "RLJ", "RMAX", "RMR", "RWT", "RYN",
        "SAFE", "SBAC", "SBRA", "SEG", "SELF", "SEVN", "SHO", "SILA", "SITC",
        "SKT", "SLG", "SPG", "SQFT", "SRG", "STAG", "STWD", "SUI", "SVC", "TCI",
        "TRNO", "TRTX", "TWO", "UDR", "UE", "UHT", "UMH", "UNIT", "VICI", "VNO",
        "VRE", "VTMX", "VTR", "WELL", "WHLR", "WPC", "WSR", "WY", "XHR",
    ],
    "Utilities": [
        "AEE", "AEP", "AES", "AQN", "ARTNA", "ATO", "AVA", "AWK", "AWR", "BEP",
        "BEPC", "BIP", "BIPC", "BKH", "BNRG", "CEG", "CEPU", "CIG", "CMS", "CNP",
        "CPK", "CREG", "CWCO", "CWEN", "CWT", "D", "DTE", "DUK", "ED", "EDN",
        "EIX", "ELPC", "EMA", "ENIC", "ENLT", "ES", "ETR", "EVRG", "EXC", "FE",
        "FLNC", "FTS", "GNE", "GWRS", "HE", "HTOO", "IDA", "KEP", "LNT", "MDU",
        "MGEE", "MSEX", "NEE", "NGG", "NI", "NJR", "NRG", "NWE", "NWN", "OGE",
        "OGS", "OKLO", "OPAL", "ORA", "PCG", "PEG", "PNW", "POR", "PPL", "RNW",
        "SAFX", "SBS", "SO", "SPH", "SR", "SRE", "STEM", "SUUN", "SWX", "TAC",
        "TLN", "UGI", "VST", "WAVE", "WEC", "WTRG", "XEL",
    ],
    "BMV": [
        "AC.MX", "AERO.MX", "ACTINVRB.MX", "AGUA.MX", "AGUILASCPO.MX",
        "ALPEKA.MX", "ALSEA.MX", "AMXB.MX", "ARA.MX", "ASURB.MX",
        "AUTLANB.MX", "AXTELCPO.MX", "BBAJIOO.MX", "BIMBOA.MX", "BOLSAA.MX",
        "CEMEXCPO.MX", "CHDRAUIB.MX", "CIDMEGA.MX", "CIEB.MX", "CMOCTEZ.MX", "CADUA.MX",
        "CMRB.MX", "CUERVO.MX", "CULTIBAB.MX", "CYDSASAA.MX",
        "DINEB.MX", "FEMSAUB.MX", "FINAMEXO.MX", "FRAGUAB.MX", "GAPB.MX",
        "GCARSOA1.MX", "GCC.MX", "GENTERA.MX", "GFINBURO.MX", "GFNORTEO.MX",
        "GIGANTE.MX", "GISSAA.MX", "GMEXICOB.MX", "GNP.MX",
        "GRUMAB.MX", "HERDEZ.MX", "HOTEL.MX", "ICHB.MX",
        "INVEXA.MX", "KIMBERA.MX", "KOFUBL.MX", "KUOB.MX", "LABB.MX",
        "LACOMERUBC.MX", "LAMOSA.MX", "LASITE.MX", "LIVEPOLC-1.MX", "MEDICAB.MX",
        "MEGACPO.MX", "MFRISCOA-1.MX", "NEMAKA.MX", "OMAB.MX", "ORBIA.MX",
        "PE&OLES.MX", "PINFRA.MX", "POSADASA.MX", "Q.MX", "RA.MX",
        "RLHA.MX", "ROBOTIKFF.MX", "SIMECB.MX", "SORIANAB.MX", "TLEVISACPO.MX", "TRAXIONA.MX",
        "VESTA.MX", "VINTE.MX", "VISTAA.MX", "VITROA.MX", "VOLARA.MX", "WALMEX.MX",
        "FIBRAPL14.MX", "FIHO12.MX", "FINN13.MX", "FMTY14.MX",
        "FIBRAMQ12.MX", "FUNO11.MX",
        "FIBRAHD15.MX", "FIBRAUP18.MX", "FPLUS16.MX",
        "FVIA16.MX", "DANHOS13.MX",
    ],
    "FIBRAS": [
        "FIBRAPL14.MX", "FIHO12.MX", "FINN13.MX", "FMTY14.MX",
        "FIBRAMQ12.MX", "FUNO11.MX", "FIBRAHD15.MX", "FIBRAUP18.MX",
        "FPLUS16.MX", "FVIA16.MX", "DANHOS13.MX",
    ],
    "ZAIK": [
        "QQQ.MX", "VOO.MX", "IAU.MX", "IBIT", "TSLA.MX", "AMZN.MX", "META.MX", "ORCL.MX", "NFLX.MX", "FIBRAPL14.MX",
        "FMTY14.MX", "DANHOS13.MX", "NVDA.MX", "WMT.MX", "NEM.MX", "LAES", "RGTI", "1211N.MX", "BBAI", "DPZ.MX",
        "XOM.MX", "PDDN.MX", "LCID", "CVX.MX", "SPOTN.MX", "NUN.MX", "BABAN.MX", "KO.MX", "MSFT.MX", "AAPL.MX",
        "MU.MX", "TSMN.MX", "PLTR.MX", "GOOGL.MX", "AEM.MX", "CRWV.MX", "BRKB.MX", "ASMLN.MX", "GS.MX", "BLK.MX", "REGN.MX",
        "JNJ.MX", "MELIN.MX", "INTC.MX", "APLD", "ZJK", "WATT", "AVGO.MX", "XYZ.MX", "AMD.MX", "FTV", "SHOPN.MX", "UBER.MX",
        "MSTR.MX", "SMCI.MX", "WDC.MX", "CRM.MX", "INUV", "HOOD.MX", "V.MX", "BAC.MX", "AXP.MX", "PM.MX", "DIS.MX",
        "BVS", "FUNO11.MX", "QTEX", "FULT", "CYPH", "LLY.MX", "JPM.MX", "CSCO.MX", "COST.MX", "MA.MX", "SPCX",
    ],
}

_todos, _seen = [], set()
for _tickers in SECTORES.values():
    for _t in _tickers:
        if _t not in _seen:
            _seen.add(_t)
            _todos.append(_t)
SECTORES["TODOS"] = _todos


# ══════════════════════════════════════════════════════════════════════════
# FUNCIONES SCREENER
# ══════════════════════════════════════════════════════════════════════════

def calcular_rsi_serie(serie, periodo):
    delta = serie.diff()
    ganancia = delta.clip(lower=0)
    perdida = -delta.clip(upper=0)
    mg = ganancia.ewm(com=periodo - 1, min_periods=periodo).mean()
    mp = perdida.ewm(com=periodo - 1, min_periods=periodo).mean()
    rs = mg / mp
    return 100 - (100 / (1 + rs))


def calcular_macd(serie, fast=12, slow=26, signal=9):
    ema_fast = serie.ewm(span=fast, adjust=False).mean()
    ema_slow = serie.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def clasificar_macd_estado(macd_line, signal_line):
    if len(macd_line) < 2 or len(signal_line) < 2:
        return "N/A"
    macd_hoy    = macd_line.iloc[-1]
    signal_hoy  = signal_line.iloc[-1]
    macd_ayer   = macd_line.iloc[-2]
    signal_ayer = signal_line.iloc[-2]
    if (macd_ayer < signal_ayer) and (macd_hoy > signal_hoy):
        return "CRUCE ARRIBA"
    elif (macd_ayer > signal_ayer) and (macd_hoy < signal_hoy):
        return "CRUCE ABAJO"
    elif macd_hoy > signal_hoy:
        return "SOBRE"
    else:
        return "BAJO"


def formatear_volumen(valor):
    if valor is None or pd.isna(valor):
        return "N/A"
    if valor >= 1e9:
        return f"{valor/1e9:.2f}B"
    elif valor >= 1e6:
        return f"{valor/1e6:.2f}M"
    elif valor >= 1e3:
        return f"{valor/1e3:.2f}K"
    return str(int(valor))


def descargar_lotes(tickers, historia, lote, progress_bar, status_text):
    frames_close, frames_vol = [], []
    total_lotes = -(-len(tickers) // lote)
    for i in range(0, len(tickers), lote):
        grupo = tickers[i:i + lote]
        lote_num = i // lote + 1
        status_text.text(f"⬇️  Descargando lote {lote_num}/{total_lotes}: {grupo[0]} … {grupo[-1]}")
        progress_bar.progress(int((lote_num / total_lotes) * 100))
        df = yf.download(grupo, period=historia, auto_adjust=True, progress=False, threads=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                frames_close.append(df["Close"])
                frames_vol.append(df["Volume"])
            else:
                frames_close.append(df[["Close"]].rename(columns={"Close": grupo[0]}))
                frames_vol.append(df[["Volume"]].rename(columns={"Volume": grupo[0]}))
    close_df = pd.concat(frames_close, axis=1) if frames_close else pd.DataFrame()
    vol_df   = pd.concat(frames_vol,  axis=1) if frames_vol   else pd.DataFrame()
    return close_df, vol_df


def correr_analisis(tickers, config, progress_bar, status_text):
    precios_df, volumen_df = descargar_lotes(
        tickers, config["historia"], config["lote"], progress_bar, status_text
    )
    if precios_df.empty:
        return pd.DataFrame()

    resultados = []
    for ticker in precios_df.columns:
        serie_close = precios_df[ticker].dropna()
        serie_vol   = volumen_df[ticker].dropna() if ticker in volumen_df.columns else None
        if len(serie_close) < 210:
            continue

        precio = serie_close.iloc[-1]
        sma20  = serie_close.rolling(20).mean().iloc[-1]
        sma50  = serie_close.rolling(50).mean().iloc[-1]
        sma200 = serie_close.rolling(200).mean().iloc[-1]
        pct_sma20  = ((precio - sma20)  / sma20)  * 100
        pct_sma50  = ((precio - sma50)  / sma50)  * 100
        pct_sma200 = ((precio - sma200) / sma200) * 100

        rsi_serie = calcular_rsi_serie(serie_close, config["periodo_rsi"])
        rsi_hoy   = rsi_serie.iloc[-1]
        rsi_ayer  = rsi_serie.iloc[-2] if len(rsi_serie) > 2 else None
        if pd.isna(rsi_hoy) or rsi_ayer is None or pd.isna(rsi_ayer):
            continue

        macd_line, signal_line, _ = calcular_macd(serie_close)
        macd_hoy    = macd_line.iloc[-1]
        signal_hoy  = signal_line.iloc[-1]
        macd_ayer   = macd_line.iloc[-2]
        signal_ayer = signal_line.iloc[-2]
        macd_cruce  = (macd_ayer < signal_ayer) and (macd_hoy > signal_hoy)
        macd_estado = clasificar_macd_estado(macd_line, signal_line)

        vol_hoy    = serie_vol.iloc[-1] if serie_vol is not None and len(serie_vol) > 0 else None
        vol_prom20 = (
            serie_vol.rolling(config["vol_periodo"]).mean().iloc[-1]
            if serie_vol is not None and len(serie_vol) >= 20 else None
        )
        volumen_fuerte = (
            vol_hoy > vol_prom20
            if vol_hoy is not None and vol_prom20 is not None and not pd.isna(vol_prom20)
            else False
        )

        cond1 = precio > sma50
        cond2 = rsi_ayer < config["rsi_sobre_vendido"] and rsi_hoy > rsi_ayer
        cond3 = precio > sma20
        cond4 = volumen_fuerte
        cond5 = macd_cruce
        comprar = cond1 and cond2 and cond3 and cond4 and cond5

        posible_venta = (rsi_hoy > config["rsi_sobre_comprado"]) or (precio < sma20)

        if comprar:
            señal = "COMPRAR"
        elif posible_venta:
            señal = "POSIBLE VENTA"
        else:
            señal = "NEUTRAL"

        resultados.append({
            "Ticker":      ticker,
            "Precio":      round(precio, 2),
            "RSI":         round(rsi_hoy, 2),
            "RSI Ayer":    round(rsi_ayer, 2),
            "% SMA20":     round(pct_sma20, 2),
            "% SMA50":     round(pct_sma50, 2),
            "% SMA200":    round(pct_sma200, 2),
            "MACD":        round(macd_hoy, 4),
            "Signal":      round(signal_hoy, 4),
            "MACD Estado": macd_estado,
            "Vol Hoy":     int(vol_hoy)    if vol_hoy    is not None else None,
            "Vol Avg20":   int(vol_prom20) if vol_prom20 is not None else None,
            "Compra":      comprar,
            "Venta":       posible_venta,
            "Señal":       señal,
        })

    df = pd.DataFrame(resultados)
    if df.empty:
        return df
    df["_orden"] = df["Compra"].astype(int) * 2 + df["Venta"].astype(int)
    df = df.sort_values(["_orden", "RSI"], ascending=[False, True]).reset_index(drop=True)
    df.drop(columns=["_orden"], inplace=True)
    return df


# ══════════════════════════════════════════════════════════════════════════
# FILTROS
# ══════════════════════════════════════════════════════════════════════════

def aplicar_filtros(df, filtros):
    df_f = df.copy()
    if filtros["ticker_busq"]:
        df_f = df_f[df_f["Ticker"].str.upper().str.contains(filtros["ticker_busq"].upper())]
    if filtros["señal"] != "Todas":
        df_f = df_f[df_f["Señal"] == filtros["señal"]]
    if filtros["macd_estado"] != "Todos":
        df_f = df_f[df_f["MACD Estado"] == filtros["macd_estado"]]
    df_f = df_f[(df_f["RSI"] >= filtros["rsi_min"]) & (df_f["RSI"] <= filtros["rsi_max"])]
    df_f = df_f[(df_f["% SMA20"] >= filtros["sma20_min"]) & (df_f["% SMA20"] <= filtros["sma20_max"])]
    df_f = df_f[(df_f["% SMA50"] >= filtros["sma50_min"]) & (df_f["% SMA50"] <= filtros["sma50_max"])]
    df_f = df_f[(df_f["% SMA200"] >= filtros["sma200_min"]) & (df_f["% SMA200"] <= filtros["sma200_max"])]
    if filtros["precio_min"] is not None:
        df_f = df_f[df_f["Precio"] >= filtros["precio_min"]]
    if filtros["precio_max"] is not None:
        df_f = df_f[df_f["Precio"] <= filtros["precio_max"]]
    if filtros["solo_vol_alto"]:
        df_f = df_f[df_f.apply(
            lambda r: (r["Vol Hoy"] is not None and r["Vol Avg20"] is not None
                       and not pd.isna(r["Vol Hoy"]) and not pd.isna(r["Vol Avg20"])
                       and r["Vol Hoy"] > r["Vol Avg20"]), axis=1)]
    if filtros["solo_macd_pos"]:
        df_f = df_f[df_f["MACD"] > df_f["Signal"]]
    return df_f.reset_index(drop=True)


def render_filtros(df):
    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    st.markdown('<div class="filter-title">🔍 FILTROS</div>', unsafe_allow_html=True)

    c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 2, 1.5, 1.5, 1])
    with c1:
        ticker_busq = st.text_input("Ticker", placeholder="Buscar… ej. NVDA",
                                    label_visibility="collapsed", key="f_ticker")
    with c2:
        señal_opt = st.selectbox("Señal", ["Todas", "COMPRAR", "POSIBLE VENTA", "NEUTRAL"],
                                 label_visibility="collapsed", key="f_señal")
    with c3:
        macd_estado_opt = st.selectbox(
            "MACD Estado", ["Todos", "CRUCE ARRIBA", "CRUCE ABAJO", "SOBRE", "BAJO"],
            label_visibility="collapsed", key="f_macd_estado"
        )
    with c4:
        precio_min = st.number_input("Precio ≥", value=None, placeholder="Precio mín",
                                     label_visibility="collapsed", key="f_precio_min", step=1.0)
    with c5:
        precio_max = st.number_input("Precio ≤", value=None, placeholder="Precio máx",
                                     label_visibility="collapsed", key="f_precio_max", step=1.0)
    with c6:
        reset = st.button("↺ Reset", key="f_reset")

    rsi_min_v    = float(round(df["RSI"].min(),      1)) if not df.empty else 0.0
    rsi_max_v    = float(round(df["RSI"].max(),      1)) if not df.empty else 100.0
    sma20_min_v  = float(round(df["% SMA20"].min(),  1)) if not df.empty else -100.0
    sma20_max_v  = float(round(df["% SMA20"].max(),  1)) if not df.empty else  100.0
    sma50_min_v  = float(round(df["% SMA50"].min(),  1)) if not df.empty else -100.0
    sma50_max_v  = float(round(df["% SMA50"].max(),  1)) if not df.empty else  100.0
    sma200_min_v = float(round(df["% SMA200"].min(), 1)) if not df.empty else -100.0
    sma200_max_v = float(round(df["% SMA200"].max(), 1)) if not df.empty else  100.0

    c7, c8, c9, c10, c11, c12, c13, c14 = st.columns(8)
    with c7:  rsi_min    = st.number_input("RSI ≥",     value=rsi_min_v,    min_value=0.0, max_value=100.0, step=1.0, key="f_rsi_min")
    with c8:  rsi_max    = st.number_input("RSI ≤",     value=rsi_max_v,    min_value=0.0, max_value=100.0, step=1.0, key="f_rsi_max")
    with c9:  sma20_min  = st.number_input("SMA20% ≥",  value=sma20_min_v,  step=1.0, key="f_sma20_min")
    with c10: sma20_max  = st.number_input("SMA20% ≤",  value=sma20_max_v,  step=1.0, key="f_sma20_max")
    with c11: sma50_min  = st.number_input("SMA50% ≥",  value=sma50_min_v,  step=1.0, key="f_sma50_min")
    with c12: sma50_max  = st.number_input("SMA50% ≤",  value=sma50_max_v,  step=1.0, key="f_sma50_max")
    with c13: sma200_min = st.number_input("SMA200% ≥", value=sma200_min_v, step=1.0, key="f_sma200_min")
    with c14: sma200_max = st.number_input("SMA200% ≤", value=sma200_max_v, step=1.0, key="f_sma200_max")

    cc1, cc2, _ = st.columns([2, 2, 8])
    with cc1: solo_vol_alto = st.checkbox("📶 Solo Vol > Avg", key="f_vol_alto")
    with cc2: solo_macd_pos = st.checkbox("📈 MACD > Signal",  key="f_macd_pos")

    st.markdown('</div>', unsafe_allow_html=True)

    if reset:
        for k in ["f_ticker", "f_señal", "f_macd_estado", "f_precio_min", "f_precio_max",
                  "f_rsi_min", "f_rsi_max", "f_sma20_min", "f_sma20_max",
                  "f_sma50_min", "f_sma50_max", "f_sma200_min", "f_sma200_max",
                  "f_vol_alto", "f_macd_pos"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    return {
        "ticker_busq":   ticker_busq,
        "señal":         señal_opt,
        "macd_estado":   macd_estado_opt,
        "precio_min":    precio_min,
        "precio_max":    precio_max,
        "rsi_min":       rsi_min,
        "rsi_max":       rsi_max,
        "sma20_min":     sma20_min,
        "sma20_max":     sma20_max,
        "sma50_min":     sma50_min,
        "sma50_max":     sma50_max,
        "sma200_min":    sma200_min,
        "sma200_max":    sma200_max,
        "solo_vol_alto": solo_vol_alto,
        "solo_macd_pos": solo_macd_pos,
    }


# ══════════════════════════════════════════════════════════════════════════
# TABLA HTML  — tickers clickeables con Streamlit component bridge
# ══════════════════════════════════════════════════════════════════════════

def render_tabla_html(df, ticker_activo=None):
    """Genera tabla HTML con tickers que al hacer click envían postMessage."""
    def pct_html(v):
        cls = "pct-pos" if v >= 0 else "pct-neg"
        signo = "+" if v >= 0 else ""
        return f'<span class="{cls}">{signo}{v:.2f}%</span>'

    def rsi_html(v):
        if v < 30:   cls = "rsi-oversold"
        elif v > 70: cls = "rsi-overbought"
        else:        cls = "rsi-neutral"
        return f'<span class="{cls}">{v:.2f}</span>'

    def vol_html(val, avg):
        s = formatear_volumen(val)
        if val is None or avg is None:
            return s
        cls = "vol-high" if val > avg else "vol-low"
        return f'<span class="{cls}">{s}</span>'

    def macd_estado_html(estado):
        mapa = {
            "CRUCE ARRIBA": "macd-cross-up",
            "CRUCE ABAJO":  "macd-cross-down",
            "SOBRE":        "macd-above",
            "BAJO":         "macd-below",
        }
        cls = mapa.get(estado, "")
        return f'<span class="{cls}">{estado}</span>' if cls else estado

    def señal_html(s):
        if s == "COMPRAR":
            return '<span class="signal-buy">🟢 COMPRAR</span>'
        elif s == "POSIBLE VENTA":
            return '<span class="signal-sell">🔴 POSIBLE VENTA</span>'
        return '<span class="signal-neutral">🟡 NEUTRAL</span>'

    rows = ""
    for i, row in df.iterrows():
        t = row['Ticker']
        activo_cls = " active" if t == ticker_activo else ""
        rows += f"""
        <tr>
            <td>{i+1}</td>
            <td>
                <span class="ticker-badge{activo_cls}"
                      onclick="selectTicker('{t}')"
                      title="Click para analizar {t}">
                    {t}
                </span>
            </td>
            <td>${row['Precio']:.2f}</td>
            <td>{rsi_html(row['RSI'])}</td>
            <td>{row['RSI Ayer']:.2f}</td>
            <td>{pct_html(row['% SMA20'])}</td>
            <td>{pct_html(row['% SMA50'])}</td>
            <td>{pct_html(row['% SMA200'])}</td>
            <td>{row['MACD']:.4f}</td>
            <td>{row['Signal']:.4f}</td>
            <td>{macd_estado_html(row['MACD Estado'])}</td>
            <td>{vol_html(row['Vol Hoy'], row['Vol Avg20'])}</td>
            <td>{formatear_volumen(row['Vol Avg20'])}</td>
            <td>{señal_html(row['Señal'])}</td>
        </tr>"""

    return f"""
    <div style="overflow-x:auto; margin-top:0.5rem;">
    <table class="screener-table">
        <thead>
            <tr>
                <th>#</th><th>Ticker</th><th>Precio</th><th>RSI</th><th>RSI Ayer</th>
                <th>% SMA20</th><th>% SMA50</th><th>% SMA200</th>
                <th>MACD</th><th>Signal</th><th>MACD Estado</th>
                <th>Vol Hoy</th><th>Vol Avg20</th><th>Señal</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    </div>"""


def ticker_selector_component(df_filtrado, ticker_activo):
    """
    Componente HTML+JS que:
    1. Renderiza la tabla con tickers clicables
    2. Al hacer click, actualiza el query param via URL + location.reload()
    """
    import streamlit.components.v1 as components

    tabla_html = render_tabla_html(df_filtrado, ticker_activo)
    activo_escaped = ticker_activo.replace("'", "\\'") if ticker_activo else ""

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ margin: 0; background: transparent; }}
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&display=swap');
        {_tabla_css()}
    </style>
    </head>
    <body>
    {tabla_html}
    <script>
        function selectTicker(ticker) {{
            // Envía mensaje al frame padre de Streamlit
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: ticker
            }}, '*');
        }}
    </script>
    </body>
    </html>
    """

    # Calcula altura dinámica según filas
    n_rows = len(df_filtrado)
    height = min(800, max(200, 56 + n_rows * 38))

    clicked = components.html(html_code, height=height, scrolling=False)
    return clicked


def _tabla_css():
    """CSS embebido para el componente iframe de la tabla."""
    return """
    * { font-family: 'JetBrains Mono', monospace; box-sizing: border-box; }
    body { background: #0a0e1a; color: #e0e6f0; }
    .screener-table { width: 100%; border-collapse: collapse; font-size: 0.76rem; }
    .screener-table th {
        background-color: #0d1828; color: #4a7aaa; font-size: 0.66rem;
        letter-spacing: 0.1em; text-transform: uppercase; padding: 0.55rem 0.7rem;
        border-bottom: 1px solid #1a2d45; text-align: right; white-space: nowrap;
    }
    .screener-table th:first-child, .screener-table th:nth-child(2) { text-align: left; }
    .screener-table td {
        padding: 0.45rem 0.7rem; border-bottom: 1px solid #111c2d;
        text-align: right; color: #c0ccd8; white-space: nowrap;
    }
    .screener-table td:first-child, .screener-table td:nth-child(2) { text-align: left; }
    .screener-table tr:hover td { background-color: #0f1e30; }
    .ticker-badge {
        background-color: #1a2d45; color: #4fc3f7; padding: 0.15rem 0.45rem;
        border-radius: 4px; font-weight: 600; font-size: 0.73rem;
        letter-spacing: 0.05em; cursor: pointer;
        border: 1px solid transparent;
        transition: all 0.15s ease;
        user-select: none;
    }
    .ticker-badge:hover {
        background-color: #4fc3f7; color: #0a0e1a;
        border-color: #4fc3f7;
    }
    .ticker-badge.active {
        background-color: #00e676; color: #0a0e1a;
        border-color: #00e676;
    }
    .signal-buy    { color: #00e676; font-weight: 700; font-size: 0.73rem; }
    .signal-sell   { color: #ff5252; font-weight: 700; font-size: 0.73rem; }
    .signal-neutral{ color: #ffd740; font-weight: 600; font-size: 0.73rem; }
    .rsi-oversold  { color: #00e676; font-weight: 600; }
    .rsi-overbought{ color: #ff5252; font-weight: 600; }
    .rsi-neutral   { color: #ffd740; }
    .pct-pos { color: #00e676; }
    .pct-neg { color: #ff5252; }
    .vol-high{ color: #00e676; }
    .vol-low { color: #ff5252; }
    .macd-cross-up   { color: #00e676; font-weight: 700; }
    .macd-cross-down { color: #ff5252; font-weight: 700; }
    .macd-above      { color: #69f0ae; }
    .macd-below      { color: #ff8a80; }
    """


# ══════════════════════════════════════════════════════════════════════════
# TERMINAL FINANCIERA  — funciones helper
# ══════════════════════════════════════════════════════════════════════════

DARK = {
    "bg":     "#0a0e1a",
    "panel":  "#0d1421",
    "border": "#1e3a5f",
    "accent": "#00b4d8",
    "text":   "#c8d6e5",
    "grid":   "#1e3a5f",
    "green":  "#00e676",
    "red":    "#ff5252",
    "yellow": "#ffd740",
}

NEWS_API_KEY = "f525b346861347859c34dfa92d6ec99a"


def fig_style(fig, axes_list):
    fig.patch.set_facecolor(DARK["bg"])
    for ax in axes_list:
        ax.set_facecolor(DARK["panel"])
        ax.tick_params(colors=DARK["text"], labelsize=8)
        ax.xaxis.label.set_color(DARK["text"])
        ax.yaxis.label.set_color(DARK["text"])
        ax.title.set_color(DARK["accent"])
        for spine in ax.spines.values():
            spine.set_edgecolor(DARK["border"])
        ax.grid(color=DARK["grid"], alpha=0.3, linewidth=0.5)


def _flatten_columns(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


@st.cache_data(ttl=600, show_spinner=False)
def terminal_cargar_df(ticker, meses=24):
    import time
    fecha_fin    = datetime.now()
    fecha_inicio = fecha_fin - relativedelta(months=meses)
    for intento in range(4):
        try:
            if intento > 0:
                time.sleep(intento * 3)
            tkr = yf.Ticker(ticker)
            df  = tkr.history(
                start=fecha_inicio.strftime('%Y-%m-%d'),
                end=fecha_fin.strftime('%Y-%m-%d'),
                auto_adjust=True,
            )
            df = _flatten_columns(df)
            for col in ('Open', 'High', 'Low', 'Close', 'Volume'):
                if col not in df.columns:
                    raise ValueError(f"Columna '{col}' ausente")
            if not df.empty:
                return df.copy()
        except Exception:
            pass
    return pd.DataFrame()


@st.cache_data(ttl=600, show_spinner=False)
def terminal_cargar_info(ticker):
    import time
    for intento in range(4):
        try:
            if intento > 0:
                time.sleep(intento * 3)
            info = yf.Ticker(ticker).info
            if info and len(info) > 5:
                return info
        except Exception:
            pass
    return {}


def terminal_calcular_indicadores(df):
    df = df.copy()
    df['SMA20']  = df['Close'].rolling(20,  min_periods=1).mean()
    df['SMA50']  = df['Close'].rolling(50,  min_periods=1).mean()
    df['SMA200'] = df['Close'].rolling(200, min_periods=1).mean()
    df['StdDev']     = df['Close'].rolling(20, min_periods=1).std().fillna(0)
    df['Upper_Band'] = df['SMA20'] + df['StdDev'] * 2
    df['Lower_Band'] = df['SMA20'] - df['StdDev'] * 2
    delta  = df['Close'].diff()
    up     = delta.clip(lower=0)
    dn     = (-delta).clip(lower=0)
    ma_up  = up.ewm(com=13, adjust=False, min_periods=1).mean()
    ma_dn  = dn.ewm(com=13, adjust=False, min_periods=1).mean()
    rs     = ma_up / ma_dn.replace(0, np.nan)
    df['RSI'] = (100 - 100 / (1 + rs)).fillna(50)
    ema12             = df['Close'].ewm(span=12, adjust=False, min_periods=1).mean()
    ema26             = df['Close'].ewm(span=26, adjust=False, min_periods=1).mean()
    df['MACD']        = ema12 - ema26
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False, min_periods=1).mean()
    df['Histogram']   = df['MACD'] - df['Signal_Line']
    return df


def terminal_calcular_niveles(df):
    niveles = []
    n       = len(df)
    start   = max(2, n - 180)
    end     = n - 2
    lo = df['Low'].values
    hi = df['High'].values
    for i in range(start, end):
        if lo[i] < lo[i-1] and lo[i] < lo[i+1] and lo[i] < lo[i-2] and lo[i] < lo[i+2]:
            niveles.append((float(lo[i]), 'Soporte'))
        elif hi[i] > hi[i-1] and hi[i] > hi[i+1] and hi[i] > hi[i-2] and hi[i] > hi[i+2]:
            niveles.append((float(hi[i]), 'Resistencia'))
    limpios = []
    if niveles:
        niveles.sort()
        dist_min = float(df['Close'].mean()) * 0.015
        curr     = niveles[0][0]
        limpios.append(niveles[0])
        for n_val, n_tipo in niveles[1:]:
            if n_val - curr > dist_min:
                limpios.append((n_val, n_tipo))
                curr = n_val
    return limpios


def _safe_float(val, default=0.0):
    try:
        f = float(val)
        return default if (np.isnan(f) or np.isinf(f)) else f
    except (TypeError, ValueError):
        return default


def terminal_calcular_scores(info):
    pm = _safe_float(info.get('profitMargins'),  0.0)
    pe = _safe_float(info.get('forwardPE'),      25.0)
    gr = _safe_float(info.get('revenueGrowth'),  0.0)
    qr = _safe_float(info.get('quickRatio'),      1.0)
    dy = _safe_float(info.get('dividendYield'),  0.0)
    pe = pe if pe > 0 else 25.0
    return {
        'Crecimiento':  round(min(10.0, max(1.0, gr  * 50)), 2),
        'Valoración':   round(max(1.0,  min(10.0, (40 / pe) * 5)), 2),
        'Rentabilidad': round(min(10.0, max(1.0, pm  * 40)), 2),
        'Salud Deuda':  round(min(10.0, max(1.0, qr  * 5)), 2),
        'Dividendos':   round(min(10.0, max(1.0, dy  * 200)), 2),
    }


@st.cache_data(ttl=600, show_spinner=False)
def terminal_sentimiento(ticker):
    try:
        url = (
            f'https://newsapi.org/v2/everything?q={ticker}'
            f'&language=en&sortBy=publishedAt&pageSize=8&apiKey={NEWS_API_KEY}'
        )
        res  = requests.get(url, timeout=8).json()
        if res.get('status') != 'ok':
            return 0, 0, [], f"NewsAPI: {res.get('message','error')}"
        arts = res.get('articles', [])
        if not arts:
            return 0, 0, [], "Sin artículos recientes"
        scores, titulos = [], []
        for a in arts[:8]:
            pol = TextBlob(a.get('title', '') or '').sentiment.polarity
            scores.append(pol)
            titulos.append({
                'title':  a.get('title', 'Sin título'),
                'score':  pol,
                'url':    a.get('url', ''),
                'source': (a.get('source') or {}).get('name', ''),
            })
        avg = sum(scores) / len(scores) if scores else 0
        return avg, len(scores), titulos, None
    except Exception as e:
        return 0, 0, [], f"Error: {e}"


@st.cache_data(ttl=600, show_spinner=False)
def terminal_cargar_fundamentales(ticker_symbol):
    try:
        ticker     = yf.Ticker(ticker_symbol)
        financials = ticker.financials
        if financials is None or financials.empty:
            return None, "Sin estados financieros"
        required = ["Total Revenue", "Gross Profit", "Operating Income", "Net Income"]
        missing  = [c for c in required if c not in financials.index]
        if missing:
            return None, f"Cuentas faltantes: {', '.join(missing)}"
        df_f = pd.DataFrame({
            "Sales":        financials.loc["Total Revenue"],
            "Gross_Profit": financials.loc["Gross Profit"],
            "Op_Income":    financials.loc["Operating Income"],
            "Net_Income":   financials.loc["Net Income"],
        })
        eps_keys    = ["Basic EPS", "Diluted EPS", "EPS", "Normalized EBITDA"]
        shares_keys = ["Basic Average Shares", "Diluted Average Shares", "Ordinary Shares Number"]
        eps_found = next((k for k in eps_keys if k in financials.index), None)
        if not eps_found:
            return None, f"No se encontró EPS"
        df_f["EPS"] = financials.loc[eps_found]
        shares_found = next((k for k in shares_keys if k in financials.index), None)
        if not shares_found:
            return None, "No se encontraron acciones"
        df_f["Shares"] = financials.loc[shares_found]
        df_f.index = pd.to_datetime(df_f.index).year
        df_f       = df_f.sort_index().dropna()
        if df_f.empty:
            return None, "DataFrame vacío"
        df_f["Gross_Margin"] = (df_f["Gross_Profit"] / df_f["Sales"]) * 100
        df_f["Op_Margin"]    = (df_f["Op_Income"]    / df_f["Sales"]) * 100
        df_f["Net_Margin"]   = (df_f["Net_Income"]   / df_f["Sales"]) * 100
        hist = ticker.history(period="5y")
        if hist.empty:
            return None, "Sin historial de precios"
        hist["Year"] = hist.index.year
        precios      = hist.groupby("Year")["Close"].mean()
        dm           = df_f.join(precios, how="inner")
        dm = dm[dm["EPS"] != 0].copy()
        dm["PE_Ratio"]   = dm["Close"] / dm["EPS"]
        dm["Market_Cap"] = dm["Close"] * dm["Shares"]
        dm["PS_Ratio"]   = dm["Market_Cap"] / dm["Sales"]
        return dm.tail(6), None
    except Exception as e:
        return None, f"Error: {e}"


# ══════════════════════════════════════════════════════════════════════════
# TERMINAL — PLOTS
# ══════════════════════════════════════════════════════════════════════════

def plot_tecnico(df, ticker, niveles, target_price, low_52, high_52):
    df_p = df.iloc[-120:].copy()
    fig  = plt.figure(figsize=(14, 14), facecolor=DARK["bg"])
    gs   = gridspec.GridSpec(5, 1, figure=fig,
                             height_ratios=[3.0, 0.4, 0.8, 1.0, 0.8], hspace=0.08)
    ax1 = fig.add_subplot(gs[0])
    axB = fig.add_subplot(gs[1])
    ax2 = fig.add_subplot(gs[2])
    ax3 = fig.add_subplot(gs[3])
    ax4 = fig.add_subplot(gs[4])
    fig_style(fig, [ax1, axB, ax2, ax3, ax4])

    ax1.plot(df_p.index, df_p['Close'],   color=DARK["text"],   linewidth=1.5, label='Precio',   zorder=5)
    ax1.fill_between(df_p.index, df_p['Lower_Band'], df_p['Upper_Band'],
                     color=DARK["accent"], alpha=0.07, label='Bollinger')
    ax1.plot(df_p.index, df_p['SMA20'],  color='#ffd740', linestyle='--', alpha=0.8, linewidth=1,   label='SMA 20')
    ax1.plot(df_p.index, df_p['SMA50'],  color='#4fc3f7', alpha=0.8,      linewidth=1.2, label='SMA 50')
    ax1.plot(df_p.index, df_p['SMA200'], color='#ff5252', linewidth=2.0,  label='SMA 200')
    for nivel, tipo in niveles:
        ax1.axhline(nivel,
                    color=DARK["green"] if tipo == 'Soporte' else DARK["red"],
                    linestyle=':', alpha=0.5, linewidth=0.8)
    ax1.set_title(f"  {ticker}  —  ANÁLISIS TÉCNICO", fontsize=12, fontweight='bold',
                  color=DARK["accent"], loc='left', pad=8)
    ax1.legend(loc='upper left', ncol=3, fontsize=7.5,
               facecolor=DARK["panel"], edgecolor=DARK["border"], labelcolor=DARK["text"])
    ax1.set_xticklabels([])

    curr_p = float(df['Close'].iloc[-1])
    axB.set_facecolor(DARK["panel"])
    axB.barh(0, high_52, color='#1e3a5f', height=0.5)
    axB.barh(0, curr_p,  color=DARK["accent"], height=0.25)
    if target_price:
        axB.axvline(target_price, color=DARK["green"], linewidth=3, label=f'Target ${target_price:.2f}')
    axB.axvline(curr_p, color=DARK["text"], linewidth=1.5, linestyle='--')
    axB.set_yticks([])
    upper_xlim = max(high_52, target_price or 0) * 1.05
    axB.set_xlim(low_52 * 0.95, upper_xlim)
    axB.set_xticklabels([])
    axB.set_title("  Rango 52 semanas  ·  Precio actual  ·  Target analistas",
                  fontsize=7.5, color='#4a6fa5', loc='left', pad=3)
    for sp in axB.spines.values():
        sp.set_edgecolor(DARK["border"])

    ax2.plot(df_p.index, df_p['RSI'], color='#ce93d8', linewidth=1.2)
    ax2.axhline(70, color=DARK["red"],   linestyle='--', alpha=0.7, linewidth=0.8)
    ax2.axhline(30, color=DARK["green"], linestyle='--', alpha=0.7, linewidth=0.8)
    ax2.fill_between(df_p.index, df_p['RSI'], 50,
                     where=df_p['RSI'] >= 50, alpha=0.1, color=DARK["green"])
    ax2.fill_between(df_p.index, df_p['RSI'], 50,
                     where=df_p['RSI'] <  50, alpha=0.1, color=DARK["red"])
    ax2.set_ylabel("RSI", color=DARK["text"], fontsize=8)
    ax2.set_ylim(0, 100)
    ax2.set_xticklabels([])

    ax3.plot(df_p.index, df_p['MACD'],       color=DARK["accent"], linewidth=1.2, label='MACD')
    ax3.plot(df_p.index, df_p['Signal_Line'], color=DARK["yellow"], linewidth=1.0,
             linestyle='--', label='Señal')
    cols_hist = [DARK["green"] if x >= 0 else DARK["red"] for x in df_p['Histogram'].fillna(0)]
    ax3.bar(df_p.index, df_p['Histogram'].fillna(0), color=cols_hist, alpha=0.4, width=1)
    ax3.axhline(0, color=DARK["text"], linewidth=0.5)
    ax3.legend(loc='upper left', fontsize=7.5, ncol=3,
               facecolor=DARK["panel"], edgecolor=DARK["border"], labelcolor=DARK["text"])
    ax3.set_ylabel("MACD", color=DARK["text"], fontsize=8)
    ax3.set_xticklabels([])

    close_arr = df_p['Close'].values
    open_arr  = df_p['Open'].values
    cols_vol  = [DARK["green"] if close_arr[i] >= open_arr[i] else DARK["red"]
                 for i in range(len(df_p))]
    ax4.bar(df_p.index, df_p['Volume'].fillna(0), color=cols_vol, alpha=0.7, width=1)
    ax4.set_ylabel("Volumen", color=DARK["text"], fontsize=8)
    plt.xticks(rotation=30, color=DARK["text"], fontsize=7)
    plt.tight_layout()
    return fig


def plot_radar(ticker, scores_dict):
    categorias = list(scores_dict.keys())
    puntajes   = list(scores_dict.values())
    N          = len(categorias)
    angles     = [n / float(N) * 2 * np.pi for n in range(N)]
    angles    += angles[:1]
    puntajes  += puntajes[:1]
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True), facecolor=DARK["bg"])
    ax.set_facecolor(DARK["panel"])
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.plot(angles, puntajes, linewidth=2, color=DARK["accent"])
    ax.fill(angles, puntajes, color=DARK["accent"], alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categorias, color=DARK["text"], size=8, fontweight='bold')
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(['2','4','6','8','10'], color='#4a6fa5', size=6)
    ax.grid(color=DARK["border"], alpha=0.5)
    for spine in ax.spines.values():
        spine.set_edgecolor(DARK["border"])
    ax.set_title(f"Perfil Fundamental: {ticker}", size=10, fontweight='bold',
                 color=DARK["accent"], y=1.1)
    plt.tight_layout()
    return fig


def plot_matriz(dm, ticker_symbol):
    years_str = [str(y) for y in dm.index]
    plt.rcParams.update(plt.rcParamsDefault)
    fig, axes = plt.subplots(2, 4, figsize=(20, 8), facecolor=DARK["bg"])
    paleta = {
        'eps': '#4fc3f7', 'sales': '#9b67f7', 'shares': '#00e5ff',
        'mcap': '#ffd740', 'pe': '#f48fb1', 'ps': '#ff8a65', 'gm': '#a5d6a7',
    }

    def estilo_ax(ax):
        ax.set_facecolor(DARK["panel"])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        for sp in ['left', 'bottom']:
            ax.spines[sp].set_edgecolor(DARK["border"])
        ax.grid(axis="y", linestyle="--", alpha=0.3, color=DARK["border"])
        ax.tick_params(colors=DARK["text"], labelsize=7)
        ax.set_xticklabels(years_str, color=DARK["text"], fontsize=7)

    def etiquetar(ax, barras, fmt, ref, interior=False):
        max_h = ref.max() if hasattr(ref, 'max') else max(ref)
        if max_h == 0:
            return
        for b in barras:
            h = b.get_height()
            if h == 0 or np.isnan(h):
                continue
            y = (h - max_h * 0.07) if interior else (h + max_h * 0.02)
            c = '#ffffff' if interior else DARK["text"]
            ax.text(b.get_x() + b.get_width() / 2, y, fmt.format(h),
                    ha="center", va="center" if interior else "bottom",
                    color=c, fontsize=7, fontweight="bold")

    estilo_ax(axes[0, 0])
    b = axes[0, 0].bar(years_str, dm["EPS"], color=paleta['eps'], width=0.55)
    etiquetar(axes[0, 0], b, "{:.2f}", dm["EPS"])
    axes[0, 0].set_title("GAAP EPS", color=DARK["accent"], fontweight="bold", pad=6, fontsize=9, loc='left')

    estilo_ax(axes[0, 1])
    sb = dm["Sales"] / 1e9
    b  = axes[0, 1].bar(years_str, sb, color=paleta['sales'], width=0.55)
    etiquetar(axes[0, 1], b, "{:.1f}", sb)
    axes[0, 1].set_title("Sales ($bln)", color=DARK["accent"], fontweight="bold", pad=6, fontsize=9, loc='left')

    estilo_ax(axes[0, 2])
    shb = dm["Shares"] / 1e9
    axes[0, 2].set_ylim(0, shb.max() * 1.15 if shb.max() > 0 else 1)
    b   = axes[0, 2].bar(years_str, shb, color=paleta['shares'], width=0.55)
    etiquetar(axes[0, 2], b, "{:.2f}", shb, interior=True)
    axes[0, 2].set_title("Shares (bln)", color=DARK["accent"], fontweight="bold", pad=6, fontsize=9, loc='left')

    estilo_ax(axes[0, 3])
    mc = dm["Market_Cap"] / 1e9
    b  = axes[0, 3].bar(years_str, mc, color=paleta['mcap'], width=0.55)
    etiquetar(axes[0, 3], b, "{:.1f}", mc)
    axes[0, 3].set_title("Market Cap ($bln)", color=DARK["accent"], fontweight="bold", pad=6, fontsize=9, loc='left')

    estilo_ax(axes[1, 0])
    b = axes[1, 0].bar(years_str, dm["PE_Ratio"].clip(0, 200), color=paleta['pe'], width=0.55)
    etiquetar(axes[1, 0], b, "{:.1f}x", dm["PE_Ratio"].clip(0, 200))
    axes[1, 0].set_title("Price / Earnings", color=DARK["accent"], fontweight="bold", pad=6, fontsize=9, loc='left')

    estilo_ax(axes[1, 1])
    b = axes[1, 1].bar(years_str, dm["PS_Ratio"], color=paleta['ps'], width=0.55)
    etiquetar(axes[1, 1], b, "{:.2f}x", dm["PS_Ratio"])
    axes[1, 1].set_title("Price / Sales", color=DARK["accent"], fontweight="bold", pad=6, fontsize=9, loc='left')

    estilo_ax(axes[1, 2])
    axes[1, 2].set_ylim(0, 110)
    b = axes[1, 2].bar(years_str, dm["Gross_Margin"].clip(0, 100), color=paleta['gm'], width=0.55)
    etiquetar(axes[1, 2], b, "{:.1f}%", dm["Gross_Margin"].clip(0, 100), interior=True)
    axes[1, 2].set_title("Gross Margin (%)", color=DARK["accent"], fontweight="bold", pad=6, fontsize=9, loc='left')

    estilo_ax(axes[1, 3])
    axes[1, 3].bar(years_str, dm["Net_Margin"], color="#2b5c8f", width=0.55, label="Net Margin")
    axes[1, 3].plot(years_str, dm["Op_Margin"],  color="#ef5350",
                    marker="o", linewidth=2, label="Op Margin")
    axes[1, 3].set_title("Op vs Net Margin (%)", color=DARK["accent"], fontweight="bold", pad=6, fontsize=9, loc='left')
    axes[1, 3].legend(frameon=False, fontsize=7, loc="upper left", labelcolor=DARK["text"])

    fig.suptitle(f"ESCÁNER FUNDAMENTAL  ·  {ticker_symbol.upper()}",
                 color=DARK["accent"], fontsize=12, fontweight='bold', y=1.01)
    plt.tight_layout()
    return fig


# ══════════════════════════════════════════════════════════════════════════
# TERMINAL FINANCIERA — render principal
# ══════════════════════════════════════════════════════════════════════════

def render_terminal(ticker_symbol):
    """Renderiza la Terminal Financiera completa para el ticker dado."""

    st.markdown(f"""
    <div class="terminal-panel">
    <div class="terminal-panel-header">
        ⬡ &nbsp; TERMINAL FINANCIERA &nbsp;·&nbsp;
        <span style="color:#e2e8f0; font-size:0.85rem;">{ticker_symbol}</span>
        &nbsp;·&nbsp; <span style="font-size:0.6rem; color:#4a6fa5;">haz click en otro ticker para cambiar</span>
    </div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner(f"Cargando datos para {ticker_symbol}..."):
        df_raw = terminal_cargar_df(ticker_symbol)

    if df_raw.empty:
        st.error(f"❌ No se encontraron datos para **{ticker_symbol}**. Verifica el símbolo.")
        return

    with st.spinner("Calculando indicadores..."):
        info    = terminal_cargar_info(ticker_symbol)
        df      = terminal_calcular_indicadores(df_raw)
        niveles = terminal_calcular_niveles(df)
        scores  = terminal_calcular_scores(info)

    # Variables clave
    u            = df.iloc[-1]
    precio       = float(u['Close'])
    target_price = _safe_float(info.get('targetMeanPrice'), None) if info.get('targetMeanPrice') else None
    low_52       = _safe_float(info.get('fiftyTwoWeekLow'),  float(df['Low'].min()))
    high_52      = _safe_float(info.get('fiftyTwoWeekHigh'), float(df['High'].max()))
    vol_prom     = float(df['Volume'].tail(20).mean())
    rsi_val      = float(u['RSI'])
    sma200       = float(u['SMA200'])
    sops         = sorted([n[0] for n in niveles if n[1] == 'Soporte'     and n[0] < precio])
    ress         = sorted([n[0] for n in niveles if n[1] == 'Resistencia' and n[0] > precio])
    tendencia    = "ALCISTA" if precio > sma200 else "BAJISTA"
    nombre       = info.get('longName',  ticker_symbol)
    sector       = info.get('sector',    'N/D')

    # Header del ticker
    st.markdown(f"""
    <div style="display:flex; align-items:baseline; gap:0.8rem; margin-bottom:1rem; flex-wrap:wrap;">
        <span style="font-family:'IBM Plex Mono',monospace; font-size:1.6rem;
                     font-weight:700; color:#e2e8f0;">{ticker_symbol}</span>
        <span style="font-family:'IBM Plex Sans',sans-serif; font-size:0.9rem; color:#64748b;">{nombre}</span>
        <span style="font-family:'IBM Plex Mono',monospace; font-size:0.65rem;
                     color:#4a6fa5; border:1px solid #1e3a5f; padding:0.15rem 0.4rem;
                     border-radius:3px;">{sector}</span>
    </div>
    """, unsafe_allow_html=True)

    # Tabs
    t1, t2, t3 = st.tabs(["📊 TÉCNICO", "🏛️ FUNDAMENTAL", "📰 SENTIMIENTO"])

    # ─── TAB 1: TÉCNICO ──────────────────────────────────────────────────
    with t1:
        c1, c2, c3, c4, c5 = st.columns(5)

        pot_str = ""
        if target_price:
            pot = ((target_price - precio) / precio) * 100
            pot_str = f'<div class="term-metric-sub">Target ${target_price:.2f} · {pot:+.1f}%</div>'

        with c1:
            st.markdown(f"""<div class="term-metric-card">
                <div class="term-metric-label">Precio Actual</div>
                <div class="term-metric-value">${precio:,.2f}</div>
                {pot_str}
            </div>""", unsafe_allow_html=True)

        rsi_cls = "negative" if rsi_val > 70 else ("positive" if rsi_val < 30 else "neutral")
        rsi_lbl = 'Sobrecompra' if rsi_val > 70 else ('Sobreventa' if rsi_val < 30 else 'Zona Neutra')
        with c2:
            st.markdown(f"""<div class="term-metric-card">
                <div class="term-metric-label">RSI (14)</div>
                <div class="term-metric-value {rsi_cls}">{rsi_val:.1f}</div>
                <div class="term-metric-sub">{rsi_lbl}</div>
            </div>""", unsafe_allow_html=True)

        t_cls = "positive" if tendencia == "ALCISTA" else "negative"
        with c3:
            st.markdown(f"""<div class="term-metric-card">
                <div class="term-metric-label">Tendencia SMA200</div>
                <div class="term-metric-value {t_cls}">{tendencia}</div>
                <div class="term-metric-sub">SMA200: ${sma200:.2f}</div>
            </div>""", unsafe_allow_html=True)

        sop_str = f"${sops[-1]:.2f}" if sops else "N/D"
        res_str = f"${ress[0]:.2f}" if ress else "N/D"
        with c4:
            st.markdown(f"""<div class="term-metric-card">
                <div class="term-metric-label">Soporte / Resist.</div>
                <div class="term-metric-value positive" style="font-size:1rem;">{sop_str}</div>
                <div class="term-metric-sub" style="color:#ff5252;">{res_str} Resist.</div>
            </div>""", unsafe_allow_html=True)

        vol_cls = "positive" if float(u['Volume']) > vol_prom else "neutral"
        with c5:
            st.markdown(f"""<div class="term-metric-card">
                <div class="term-metric-label">Volumen Hoy</div>
                <div class="term-metric-value {vol_cls}">{int(u['Volume']):,}</div>
                <div class="term-metric-sub">Prom 20d: {int(vol_prom):,}</div>
            </div>""", unsafe_allow_html=True)

        with st.spinner("Renderizando gráfico..."):
            try:
                fig_tec = plot_tecnico(df, ticker_symbol, niveles, target_price, low_52, high_52)
                st.pyplot(fig_tec, use_container_width=True)
                plt.close(fig_tec)
            except Exception as e:
                st.error(f"Error en gráfico técnico: {e}")

        if niveles:
            st.markdown('<div class="term-section-header">SOPORTES &amp; RESISTENCIAS</div>',
                        unsafe_allow_html=True)
            col_s, col_r = st.columns(2)
            sops_all = [(n, t) for n, t in niveles if t == 'Soporte']
            ress_all = [(n, t) for n, t in niveles if t == 'Resistencia']
            with col_s:
                if sops_all:
                    html = '<table class="levels-table"><thead><tr><th>Soporte</th><th>Dist.</th></tr></thead><tbody>'
                    for n, _ in sorted(sops_all, reverse=True)[:6]:
                        dist = ((precio - n) / precio) * 100
                        html += f'<tr><td class="lvl-soporte">${n:.2f}</td><td style="color:#64748b;">{dist:.2f}%</td></tr>'
                    html += '</tbody></table>'
                    st.markdown(html, unsafe_allow_html=True)
            with col_r:
                if ress_all:
                    html = '<table class="levels-table"><thead><tr><th>Resistencia</th><th>Dist.</th></tr></thead><tbody>'
                    for n, _ in sorted(ress_all)[:6]:
                        dist = ((n - precio) / precio) * 100
                        html += f'<tr><td class="lvl-resistencia">${n:.2f}</td><td style="color:#64748b;">+{dist:.2f}%</td></tr>'
                    html += '</tbody></table>'
                    st.markdown(html, unsafe_allow_html=True)

        # Bollinger
        st.markdown('<div class="term-section-header">BANDAS DE BOLLINGER</div>',
                    unsafe_allow_html=True)
        bcol1, bcol2, bcol3 = st.columns(3)
        bb_upper  = float(u['Upper_Band'])
        bb_lower  = float(u['Lower_Band'])
        bb_sma    = float(u['SMA20'])
        bb_status = ("🔴 SOBRECOMPRA" if precio >= bb_upper
                     else "🟢 SOBREVENTA" if precio <= bb_lower else "⚪ NEUTRO")
        with bcol1:
            st.markdown(f"""<div class="term-metric-card">
                <div class="term-metric-label">Banda Superior</div>
                <div class="term-metric-value" style="font-size:1rem;">${bb_upper:.2f}</div>
            </div>""", unsafe_allow_html=True)
        with bcol2:
            st.markdown(f"""<div class="term-metric-card">
                <div class="term-metric-label">SMA20 / Media</div>
                <div class="term-metric-value" style="font-size:1rem;">${bb_sma:.2f}</div>
                <div class="term-metric-sub">{bb_status}</div>
            </div>""", unsafe_allow_html=True)
        with bcol3:
            st.markdown(f"""<div class="term-metric-card">
                <div class="term-metric-label">Banda Inferior</div>
                <div class="term-metric-value" style="font-size:1rem;">${bb_lower:.2f}</div>
            </div>""", unsafe_allow_html=True)

    # ─── TAB 2: FUNDAMENTAL ──────────────────────────────────────────────
    with t2:
        col_radar, col_scores = st.columns([1, 1])
        with col_radar:
            st.markdown('<div class="term-section-header">RADAR FUNDAMENTAL</div>',
                        unsafe_allow_html=True)
            try:
                fig_rad = plot_radar(ticker_symbol, scores)
                st.pyplot(fig_rad, use_container_width=True)
                plt.close(fig_rad)
            except Exception as e:
                st.error(f"Error en radar: {e}")

        with col_scores:
            st.markdown('<div class="term-section-header">SCORES (/ 10)</div>',
                        unsafe_allow_html=True)
            for cat, val in scores.items():
                pct = int(val * 10)
                st.markdown(f"""<div class="score-row">
                    <div class="score-name">{cat}</div>
                    <div class="score-num">{val:.1f}</div>
                    <div class="score-bar-wrap">
                        <div class="score-bar-bg">
                            <div class="score-bar-fill" style="width:{pct}%"></div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

            st.markdown('<div class="term-section-header" style="margin-top:1rem;">DATOS EMPRESA</div>',
                        unsafe_allow_html=True)

            def fmt_val(v, fmt):
                try:
                    return fmt.format(v) if v else "N/D"
                except Exception:
                    return "N/D"

            datos = [
                ("Sector",     sector),
                ("Industria",  info.get('industry', 'N/D')),
                ("P/E Fwd.",   fmt_val(info.get('forwardPE'),    "{:.1f}x")),
                ("P/B",        fmt_val(info.get('priceToBook'),  "{:.2f}x")),
                ("Div. Yield", fmt_val(info.get('dividendYield') and info['dividendYield']*100, "{:.2f}%")),
                ("Mkt Cap",    fmt_val(info.get('marketCap')     and info['marketCap']/1e9,     "${:.1f}B")),
                ("52W Low",    f"${low_52:.2f}"),
                ("52W High",   f"${high_52:.2f}"),
            ]
            for label, val in datos:
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:0.3rem 0;
                            border-bottom:1px solid #1a2a3a; font-family:'IBM Plex Mono',monospace;">
                    <span style="font-size:0.65rem; color:#4a6fa5;">{label}</span>
                    <span style="font-size:0.68rem; color:#c8d6e5;">{val}</span>
                </div>""", unsafe_allow_html=True)

        st.markdown('<div class="term-section-header">MATRIZ DE VALORACIÓN HISTÓRICA</div>',
                    unsafe_allow_html=True)
        with st.spinner("Cargando datos históricos..."):
            dm, fund_error = terminal_cargar_fundamentales(ticker_symbol)
        if dm is not None and not dm.empty:
            try:
                fig_mat = plot_matriz(dm, ticker_symbol)
                st.pyplot(fig_mat, use_container_width=True)
                plt.close(fig_mat)
            except Exception as e:
                st.error(f"Error en matriz: {e}")
        else:
            st.markdown(f'<div class="warn-box">⚠ Datos fundamentales no disponibles — {fund_error}</div>',
                        unsafe_allow_html=True)

    # ─── TAB 3: SENTIMIENTO ──────────────────────────────────────────────
    with t3:
        st.markdown('<div class="term-section-header">ANÁLISIS DE SENTIMIENTO DE NOTICIAS</div>',
                    unsafe_allow_html=True)
        with st.spinner("Analizando noticias..."):
            score_sent, count_news, titulos, sent_error = terminal_sentimiento(ticker_symbol)

        if count_news == 0:
            st.markdown(f'<div class="warn-box">⚠ {sent_error or "Sin noticias recientes"}</div>',
                        unsafe_allow_html=True)
        else:
            sent_label = ("POSITIVO" if score_sent > 0.05 else
                          "NEGATIVO" if score_sent < -0.05 else "NEUTRAL")
            emoji = "😊" if score_sent > 0.05 else "😡" if score_sent < -0.05 else "😐"
            cls_s = ("sent-positive" if score_sent > 0.05 else
                     "sent-negative" if score_sent < -0.05 else "sent-neutral")

            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                st.markdown(f"""<div class="term-metric-card">
                    <div class="term-metric-label">Sentimiento Global</div>
                    <div class="term-metric-value" style="font-size:1rem;">{emoji} {sent_label}</div>
                    <div class="term-metric-sub">Score: {score_sent:.3f}</div>
                </div>""", unsafe_allow_html=True)
            with mc2:
                st.markdown(f"""<div class="term-metric-card">
                    <div class="term-metric-label">Artículos analizados</div>
                    <div class="term-metric-value neutral">{count_news}</div>
                </div>""", unsafe_allow_html=True)
            with mc3:
                positivas = sum(1 for t in titulos if t['score'] > 0.05)
                negativas = sum(1 for t in titulos if t['score'] < -0.05)
                st.markdown(f"""<div class="term-metric-card">
                    <div class="term-metric-label">Distribución</div>
                    <div class="term-metric-value positive" style="font-size:1rem; display:inline;">{positivas}+</div>
                    &nbsp;
                    <div class="term-metric-value negative" style="font-size:1rem; display:inline;">{negativas}-</div>
                    <div class="term-metric-sub">{count_news - positivas - negativas} neutras</div>
                </div>""", unsafe_allow_html=True)

            gauge_pct   = int((score_sent + 1) / 2 * 100)
            gauge_color = ("#00e676" if score_sent > 0.05 else
                           "#ff5252" if score_sent < -0.05 else "#ffd740")
            st.markdown(f"""
            <div style="margin:1rem 0; padding:0.8rem; background:#0d1421;
                        border:1px solid #1e3a5f; border-radius:6px;">
                <div style="font-family:'IBM Plex Mono',monospace; font-size:0.6rem;
                            color:#4a6fa5; letter-spacing:2px; margin-bottom:0.5rem;">
                    MEDIDOR DE SENTIMIENTO
                </div>
                <div style="background:#1e3a5f; border-radius:10px; height:10px; position:relative;">
                    <div style="width:{gauge_pct}%; height:100%; background:{gauge_color};
                                border-radius:10px;"></div>
                    <div style="position:absolute; left:50%; top:-3px; width:2px; height:16px;
                                background:#4a6fa5; transform:translateX(-50%);"></div>
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:0.25rem;
                            font-family:'IBM Plex Mono',monospace; font-size:0.58rem; color:#4a6fa5;">
                    <span>MUY NEGATIVO</span><span>NEUTRAL</span><span>MUY POSITIVO</span>
                </div>
            </div>""", unsafe_allow_html=True)

            st.markdown('<div class="term-section-header">NOTICIAS RECIENTES</div>',
                        unsafe_allow_html=True)
            for t in titulos:
                s    = t['score']
                cls_ = "sent-positive" if s > 0.05 else "sent-negative" if s < -0.05 else "sent-neutral"
                icon = "▲" if s > 0.05 else "▼" if s < -0.05 else "—"
                url_link = (f'<a href="{t["url"]}" target="_blank" style="color:#00b4d8;">↗</a>'
                            if t.get('url') else '')
                st.markdown(f"""
                <div style="display:flex; align-items:flex-start; gap:0.6rem; padding:0.6rem 0;
                            border-bottom:1px solid #1a2a3a;">
                    <span class="sentiment-badge {cls_}" style="flex-shrink:0;">{icon} {s:+.2f}</span>
                    <div>
                        <div style="font-family:'IBM Plex Sans',sans-serif; font-size:0.8rem;
                                    color:#c8d6e5; line-height:1.4;">{t['title']} {url_link}</div>
                        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.62rem;
                                    color:#4a6fa5; margin-top:0.2rem;">{t.get('source','')}</div>
                    </div>
                </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="font-family:'Syne',sans-serif; font-weight:800; font-size:1.3rem;
                color:#4fc3f7; margin-bottom:0.2rem; letter-spacing:-0.01em;">
        📈 SWING SCREENER
    </div>
    <div style="font-size:0.65rem; color:#4a6080; letter-spacing:0.12em;
                text-transform:uppercase; margin-bottom:1.2rem;">
        RSI · MACD · SMA · VOLUMEN
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**SECTOR**")
    sector_seleccionado = st.radio(
        label="",
        options=list(SECTORES.keys()),
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("**PARÁMETROS**")
    periodo_rsi = st.slider("Periodo RSI", 7, 21, 14)
    historia    = st.selectbox("Historia", ["1y", "2y", "3y"], index=1)
    rsi_sc      = st.slider("RSI Sobrecomprado", 50, 80, 70)
    rsi_sv      = st.slider("RSI Sobrevendido",  20, 50, 30)
    lote        = st.slider("Tamaño de lote",    20, 100, 50)

    st.markdown("---")
    n_tickers = len(SECTORES[sector_seleccionado])
    st.markdown(f"""
    <div class="info-box">
        Sector: <b>{sector_seleccionado}</b><br>
        Tickers: <b>{n_tickers}</b><br>
        Lotes: <b>{-(-n_tickers // lote)}</b>
    </div>
    """, unsafe_allow_html=True)

    correr = st.button("▶  CORRER ANÁLISIS")

    # Botón para cerrar terminal si hay uno abierto
    if st.session_state.get("ticker_terminal"):
        st.markdown("---")
        st.markdown(f"""
        <div style="font-size:0.7rem; color:#4a6080; margin-bottom:0.3rem;">
            Terminal activa:
        </div>
        <div style="font-family:'Syne',sans-serif; font-size:1rem; font-weight:700;
                    color:#00e676; margin-bottom:0.5rem;">
            {st.session_state['ticker_terminal']}
        </div>
        """, unsafe_allow_html=True)
        if st.button("✕  Cerrar Terminal"):
            st.session_state["ticker_terminal"] = None
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════

st.markdown('<div class="main-header">SWING SCREENER</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="sub-header">sector · {sector_seleccionado.upper()} &nbsp;|&nbsp; '
    f'{len(SECTORES[sector_seleccionado])} tickers &nbsp;|&nbsp; '
    f'<span style="color:#4fc3f7;">click en ticker para abrir terminal</span></div>',
    unsafe_allow_html=True
)

# Leer ticker seleccionado via query params (puente JS→Streamlit)
params = st.query_params
if "ticker" in params and params["ticker"]:
    t_param = params["ticker"].strip().upper()
    if t_param != st.session_state.get("ticker_terminal"):
        st.session_state["ticker_terminal"] = t_param
        # Limpiar el query param para evitar que persista en reloads
        st.query_params.clear()
        st.rerun()

# Inicializar session state
if "ticker_terminal" not in st.session_state:
    st.session_state["ticker_terminal"] = None
if "df_result" not in st.session_state:
    st.session_state["df_result"] = pd.DataFrame()
if "sector_result" not in st.session_state:
    st.session_state["sector_result"] = None

# ── Correr análisis ──────────────────────────────────────────────
if correr:
    config = {
        "periodo_rsi":        periodo_rsi,
        "historia":           historia,
        "lote":               lote,
        "vol_periodo":        20,
        "rsi_sobre_comprado": rsi_sc,
        "rsi_sobre_vendido":  rsi_sv,
    }
    progress_bar = st.progress(0)
    status_text  = st.empty()
    tickers      = SECTORES[sector_seleccionado]
    df_result    = correr_analisis(tickers, config, progress_bar, status_text)
    progress_bar.empty()
    status_text.empty()

    if df_result.empty:
        st.error("❌ No se generaron resultados. Verifica la conexión o los tickers.")
    else:
        st.session_state["df_result"]     = df_result
        st.session_state["sector_result"] = sector_seleccionado
        st.session_state["ticker_terminal"] = None  # reset terminal al correr nuevo análisis

# ── Mostrar resultados ───────────────────────────────────────────
if not st.session_state["df_result"].empty:
    df_result = st.session_state["df_result"]

    # Métricas superiores
    n_compra     = int(df_result["Compra"].sum())
    n_venta      = int(df_result["Venta"].sum())
    n_neutral    = len(df_result) - n_compra - n_venta
    n_cruce_up   = int((df_result["MACD Estado"] == "CRUCE ARRIBA").sum())
    n_cruce_down = int((df_result["MACD Estado"] == "CRUCE ABAJO").sum())
    n_sobre      = int((df_result["MACD Estado"] == "SOBRE").sum())
    n_bajo       = int((df_result["MACD Estado"] == "BAJO").sum())

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#00e676;">{n_compra}</div>
            <div class="metric-label">🟢 Compra</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#ff5252;">{n_venta}</div>
            <div class="metric-label">🔴 Posible Venta</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#ffd740;">{n_neutral}</div>
            <div class="metric-label">🟡 Neutral</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#4fc3f7;">{len(df_result)}</div>
            <div class="metric-label">📊 Procesados</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#00e676;">{n_cruce_up}</div>
            <div class="metric-label">MACD CRUCE ↑</div></div>""", unsafe_allow_html=True)
    with mc2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#ff5252;">{n_cruce_down}</div>
            <div class="metric-label">MACD CRUCE ↓</div></div>""", unsafe_allow_html=True)
    with mc3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#69f0ae;">{n_sobre}</div>
            <div class="metric-label">MACD ▲ SOBRE señal</div></div>""", unsafe_allow_html=True)
    with mc4:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#ff8a80;">{n_bajo}</div>
            <div class="metric-label">MACD ▼ BAJO señal</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Filtros
    filtros     = render_filtros(df_result)
    df_filtrado = aplicar_filtros(df_result, filtros)

    st.markdown(
        f'<div class="result-count">Mostrando <b style="color:#4fc3f7">{len(df_filtrado)}</b> '
        f'de <b>{len(df_result)}</b> resultados &nbsp;·&nbsp; '
        f'<span style="color:#4a6080;">click en un ticker para abrir su terminal</span></div>',
        unsafe_allow_html=True
    )

    if df_filtrado.empty:
        st.warning("⚠️ Ningún ticker cumple los filtros actuales.")
    else:
        # ── Tabla con tickers clicables via componente HTML ──────────────
        ticker_activo = st.session_state.get("ticker_terminal")

        # Construir HTML completo con JS bridge
        import streamlit.components.v1 as components

        tabla_html = render_tabla_html(df_filtrado, ticker_activo)
        n_rows     = len(df_filtrado)
        height_px  = min(900, max(220, 56 + n_rows * 38))

        # El JS envía el ticker al padre (Streamlit) via postMessage,
        # que Streamlit captura si usamos st.components.v1.html con key.
        # Como alternativa robusta: actualizamos ?ticker=X en la URL
        # y Streamlit lo lee en query_params al rerun automático.
        html_tabla = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            body {{ margin:0; padding:0; background:transparent; overflow-x:auto; }}
            {_tabla_css()}
        </style>
        </head>
        <body>
        {tabla_html}
        <script>
        function selectTicker(ticker) {{
            // Actualiza la URL del frame padre con ?ticker=SYMBOL
            // Streamlit detecta el cambio de query_params y hace rerun
            try {{
                var url = new URL(window.parent.location.href);
                url.searchParams.set('ticker', ticker);
                window.parent.history.pushState({{}}, '', url.toString());
                // Dispara un rerun de Streamlit cambiando la URL
                window.parent.location.href = url.toString();
            }} catch(e) {{
                // Fallback: postMessage
                window.parent.postMessage({{
                    isStreamlitMessage: true,
                    type: 'streamlit:setComponentValue',
                    value: ticker
                }}, '*');
            }}
        }}
        </script>
        </body>
        </html>
        """

        components.html(html_tabla, height=height_px, scrolling=True)

    # CSV download
    csv = df_filtrado.drop(columns=["Compra", "Venta"], errors="ignore").to_csv(index=False)
    st.download_button(
        label="⬇️  Descargar CSV (filtrado)",
        data=csv,
        file_name=f"screener_{sector_seleccionado.replace(' ', '_')}.csv",
        mime="text/csv"
    )

    # ── TERMINAL FINANCIERA ──────────────────────────────────────────────
    ticker_terminal = st.session_state.get("ticker_terminal")
    if ticker_terminal:
        st.markdown("---")
        render_terminal(ticker_terminal)

else:
    st.markdown("""
    <div style="margin-top:3rem; text-align:center; color:#2a4060;">
        <div style="font-size:3rem; margin-bottom:1rem;">📊</div>
        <div style="font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:600; color:#3a5070;">
            Selecciona un sector en el panel izquierdo<br>
            y presiona <span style="color:#4fc3f7;">▶ CORRER ANÁLISIS</span>
        </div>
        <div style="font-size:0.72rem; color:#4a6080; margin-top:0.8rem; font-family:'JetBrains Mono',monospace;">
            Luego haz click en cualquier ticker para abrir su Terminal Financiera
        </div>
    </div>
    """, unsafe_allow_html=True)
