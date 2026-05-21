import streamlit as st
import yfinance as yf
import pandas as pd
import logging
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── Suprimir warnings ─────────────────────────────────────────────────────
warnings.filterwarnings("ignore")
logging.getLogger("yfinance").setLevel(logging.CRITICAL)
logging.getLogger("peewee").setLevel(logging.CRITICAL)

# ── Page config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Swing Screener",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS personalizado ─────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'JetBrains Mono', monospace;
    }

    .stApp {
        background-color: #0a0e1a;
        color: #e0e6f0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0d1220;
        border-right: 1px solid #1e2d4a;
    }

    [data-testid="stSidebar"] * {
        color: #c8d4e8 !important;
    }

    /* Header principal */
    .main-header {
        font-family: 'Syne', sans-serif;
        font-weight: 800;
        font-size: 2.2rem;
        color: #4fc3f7;
        letter-spacing: -0.02em;
        margin-bottom: 0;
        line-height: 1.1;
    }

    .sub-header {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        color: #4a6080;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 1.5rem;
    }

    /* Métricas */
    .metric-card {
        background: linear-gradient(135deg, #0f1828 0%, #121e30 100%);
        border: 1px solid #1a2d45;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        text-align: center;
    }

    .metric-value {
        font-family: 'Syne', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        line-height: 1;
    }

    .metric-label {
        font-size: 0.7rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #4a6080;
        margin-top: 0.3rem;
    }

    /* Tabla */
    .screener-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.78rem;
        font-family: 'JetBrains Mono', monospace;
    }

    .screener-table th {
        background-color: #0d1828;
        color: #4a7aaa;
        font-size: 0.68rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 0.6rem 0.8rem;
        border-bottom: 1px solid #1a2d45;
        text-align: right;
        white-space: nowrap;
    }

    .screener-table th:first-child,
    .screener-table th:nth-child(2) {
        text-align: left;
    }

    .screener-table td {
        padding: 0.5rem 0.8rem;
        border-bottom: 1px solid #111c2d;
        text-align: right;
        color: #c0ccd8;
        white-space: nowrap;
    }

    .screener-table td:first-child,
    .screener-table td:nth-child(2) {
        text-align: left;
    }

    .screener-table tr:hover td {
        background-color: #0f1e30;
    }

    /* Señales */
    .signal-buy {
        color: #00e676;
        font-weight: 700;
        font-size: 0.75rem;
    }

    .signal-sell {
        color: #ff5252;
        font-weight: 700;
        font-size: 0.75rem;
    }

    .signal-neutral {
        color: #ffd740;
        font-weight: 600;
        font-size: 0.75rem;
    }

    /* RSI colores */
    .rsi-oversold { color: #00e676; font-weight: 600; }
    .rsi-overbought { color: #ff5252; font-weight: 600; }
    .rsi-neutral { color: #ffd740; }

    /* % colores */
    .pct-pos { color: #00e676; }
    .pct-neg { color: #ff5252; }

    /* Vol colores */
    .vol-high { color: #00e676; }
    .vol-low { color: #ff5252; }

    /* Ticker badge */
    .ticker-badge {
        background-color: #1a2d45;
        color: #4fc3f7;
        padding: 0.15rem 0.45rem;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
    }

    /* Sidebar sector radio */
    .stRadio > div {
        gap: 0.3rem;
    }

    /* Botón correr */
    .stButton > button {
        background: linear-gradient(135deg, #1565c0, #1976d2);
        color: white;
        border: none;
        border-radius: 6px;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        font-size: 0.8rem;
        letter-spacing: 0.08em;
        padding: 0.6rem 1.2rem;
        width: 100%;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #1976d2, #2196f3);
        transform: translateY(-1px);
    }

    /* Divider */
    hr {
        border-color: #1a2d45;
        margin: 1rem 0;
    }

    /* Selectbox */
    .stSelectbox > div > div {
        background-color: #0d1828;
        border-color: #1a2d45;
        color: #c8d4e8;
    }

    /* Slider */
    .stSlider > div > div > div {
        background-color: #1976d2;
    }

    /* Info box */
    .info-box {
        background-color: #0d1e30;
        border-left: 3px solid #4fc3f7;
        padding: 0.6rem 1rem;
        border-radius: 0 6px 6px 0;
        font-size: 0.75rem;
        color: #7090b0;
        margin-bottom: 1rem;
    }

    /* Progress bar override */
    .stProgress > div > div > div {
        background-color: #1976d2;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# TICKERS POR SECTOR
# ══════════════════════════════════════════════════════════════════════════

SECTORES = {

    "Communication Services": [
        "ACCS", "AD", "ADV", "AENT", "AGAE", "AMC", "AMCX", "AMX", "ANGH", "ANGI", 
        "ANGX", "APP", "AREN", "ATEX", "ATHM", "ATNI", "BAOS", "BATRA", "BATRK", "BBGI", 
        "BCE", "BIDU", "BILI", "BMBL", "BODI", "BZ", "BZFD", "CABO", "CARS", "CAST", 
        "CCG", "CCO", "CCOI", "CDLX", "CHAI", "CHR", "CHT", "CHTR", "CMCM", "CMCSA", 
        "CNET", "CNK", "CNVS", "CPOP", "CRTO", "CTW", "CURI", "CXDO", "DDI", "DIBS", 
        "DIS", "DJT", "DKI", "DLPN", "DOYU", "DRCT", "DV", "EA", "EDHL", "EDUC", 
        "EEX", "ELWT", "EVC", "EVER", "FENG", "FLNT", "FNGR", "FOX", "FOXA", "FTRK", 
        "FUBO", "FVRR", "FWONA", "FWONK", "GAIA", "GAME", "GCL", "GDC", "GDEV", "GENI", 
        "GETY", "GIBO", "GIFT", "GIGM", "GITS", "GLIBA", "GLIBK", "GMHS", "GOGO", "GOOG", 
        "GOOGL", "GRPN", "GRVY", "GSAT", "GTN", "GXAI", "HAO", "HUYA", "IAC", "IDT", 
        "IHRT", "IMAX", "IOTR", "IQ", "IQST", "IRDM", "IZEA", "JOYY", "KORE", "KRKR", 
        "KT", "KUST", "KVHI", "KWM", "KYIV", "LBRDA", "LBRDK", "LBTYA", "LBTYK", "LCFY", 
        "LEE", "LFS", "LILA", "LILAK", "LLYVA", "LLYVK", "LUMN", "LVO", "LYV", "MANU", 
        "MAX", "MCHX", "MCS", "MDIA", "META", "MGNI", "MNY", "MOMO", "MPU", "MRDN", 
        "MSGE", "MSGM", "MSGS", "MTCH", "MYPS", "NAMI", "NCMI", "NEXN", "NFLX", "NIPG", 
        "NMAX", "NRDS", "NTES", "NWS", "NWSA", "NXDR", "NXST", "NYT", "OMC", "ONFO", 
        "OPRA", "OPTU", "PCLA", "PERI", "PHI", "PINS", "PLAY", "PLTK", "PODC", "PSKY", 
        "PSO", "QNST", "RBLX", "RCI", "RDCM", "RDDT", "RDI", "ROKU", "RSVR", "RUM", 
        "SATS", "SBGI", "SCHL", "SEAT", "SGA", "SHEN", "SIFY", "SIRI", "SJ", "SKLZ", 
        "SKM", "SLE", "SLMT", "SNAL", "SNAP", "SOGP", "SOHU", "SOPA", "SPHR", "SPOT", 
        "SSP", "SSTK", "STFS", "STGW", "STRZ", "STUB", "SURG", "SWAG", "T", "TBH", 
        "TBLA", "TC", "TDAY", "TDIC", "TDS", "TEAD", "TEO", "TIGO", "TIMB", "TJGC", 
        "TKC", "TKO", "TLK", "TME", "TMUS", "TNMG", "TOON", "TRVG", "TSQ", "TTD", 
        "TTWO", "TU", "TULP", "TV", "TZOO", "UCL", "UONE", "UPWK", "UPXI", "VEON", 
        "VIV", "VOD", "VSME", "VSNT", "VZ", "WB", "WBD", "WBTN", "WIMI", "WLY", 
        "WMG", "WPP", "WSHP", "XHLD", "YDKG", "YELP", "Z", "ZD", "ZDGE", "ZG", 
        "ZH", "ZIP", "ZNB",
    ],

    "Technology": [
        "AAOI", "AAPL", "ACFN", "ACIW", "ACLS", "ACMR", "ACN", "ADBE", "ADEA", "ADI", 
        "ADP", "ADSK", "ADTN", "AEHR", "AEVA", "AEYE", "AGMH", "AGPU", "AGYS", "AI", 
        "AIB", "AIFC", "AIFF", "AIMD", "AIOS", "AIOT", "AIP", "AIRG", "AISP", "AIXC", 
        "AIXI", "AKAM", "ALAB", "ALAR", "ALGM", "ALIT", "ALKT", "ALLT", "ALMU", "ALNT", 
        "ALOT", "ALRM", "AMAT", "AMBA", "AMBQ", "AMBR", "AMCI", "AMD", "AMKR", "AMOD", 
        "AMPG", "AMPL", "AMST", "AMZE", "ANET", "AOSL", "APH", "API", "APLD", "APPF", 
        "APPN", "APPS", "ARAI", "ARBB", "ARBE", "ARM", "ARQQ", "ARRY", "ARW", "ASAN", 
        "ASML", "ASTC", "ASTI", "ASTS", "ASUR", "ASX", "ASYS", "ATEN", "ATGL", "ATHR", 
        "ATOM", "AUDC", "AUID", "AUUD", "AVGO", "AVNW", "AVPT", "AVT", "AWRE", "AXIL", 
        "AXTI", "AZ", "BAND", "BB", "BBAI", "BDC", "BEEM", "BELFA", "BELFB", "BGIN", 
        "BHE", "BILL", "BIYA", "BKKT", "BKTI", "BL", "BLIN", "BLIV", "BLKB", "BLND", 
        "BLSH", "BLZE", "BMI", "BMR", "BNAI", "BNZI", "BOSC", "BOX", "BOXL", "BR", 
        "BRAI", "BRUN", "BRZE", "BSY", "BTCT", "BTDR", "BTQ", "BTTC", "BULL", "BVC", 
        "BZAI", "CACI", "CALX", "CAMT", "CAN", "CCC", "CCSI", "CDNS", "CDW", 
        "CETX", "CEVA", "CGNT", "CGNX", "CHKP", "CHOW", "CHRN", "CHYM", "CIEN", "CIFR", 
        "CINT", "CISO", "CLBT", "CLFD", "CLMB", "CLPS", "CLRO", "CLS", "CLVT", "CMRC", 
        "CMTL", "CNDT", "CNXC", "CNXN", "COHR", "COHU", "CORZ", "CPAY", "CPSH", "CRCT", 
        "CRDO", "CREX", "CRM", "CRNC", "CRNT", "CRSR", "CRUS", "CRWD", "CRWV", "CSAI", 
        "CSCO", "CSGS", "CSIQ", "CSPI", "CTLP", "CTM", "CTS", "CTSH", "CURR", "CVLT", 
        "CWAN", "CXAI", "CXM", "CYAB", "CYCU", "CYN", "DAIC", "DAIO", "DAKT", "DAVA", 
        "DAVE", "DBD", "DBX", "DCBO", "DDD", "DDOG", "DELL", "DFIN", "DGII", "DHX", 
        "DIOD", "DJCO", "DLO", "DMRC", "DOCN", "DOCU", "DOMO", "DOX", "DPRO", "DQ", 
        "DSGX", "DSP", "DSWL", "DT", "DTSS", "DTST", "DUOL", "DUOT", "DVLT", "DXC", 
        "EBON", "EEFT", "EFOR", "EGAN", "EGHT", "ELSE", "ELTK", "ENPH", "ENTG", "EPAM", 
        "ERIC", "ESE", "ESTC", "EVCM", "EVTC", "EXFY", "EXLS", "EXOD", "EXTR", 
        "FATN", "FCUV", "FEBO", "FEIM", "FFIV", "FICO", "FIEE", "FIG", "FIS", "FISV", 
        "FIVN", "FKWL", "FLEX", "FLYW", "FN", "FORM", "FORTY", "FOUR", "FOXX", "FRGT", 
        "FRMM", "FROG", "FRSH", "FSLR", "FSLY", "FTCI", "FTFT", "FTNT", "FTV", "FUSE", 
        "G", "GAUZ", "GCT", "GCTS", "GDDY", "GDS", "GDYN", "GEN", "GFS", "GGRP", 
        "GIB", "GILT", "GLE", "GLOB", "GLOO", "GLW", "GMEX", "GMM", "GNSS", "GOAI", 
        "GPN", "GPRO", "GRAB", "GRMN", "GRND", "GRRR", "GSIT", "GTLB", "GTM", "GWRE", 
        "HCKT", "HIMX", "HIT", "HKD", "HKIT", "HLIT", "HOLO", "HPAI", "HPE", "HPQ", 
        "HQ", "HTCR", "HUBC", "HUBS", "IBEX", "IBM", "IBTA", "ICG", "ICHR", "IDAI", 
        "IDCC", "IDN", "IFBD", "III", "IIIV", "ILLR", "IMMR", "IMOS", "IMTE", "IMXI", 
        "INDI", "INFQ", "INFY", "INGM", "INLX", "INOD", "INSG", "INTA", "INTC", "INTT", 
        "INTU", "INTZ", "INUV", "IONQ", "IOT", "IPGP", "IPM", "IPWR", "IT", "ITRI", 
        "ITRN", "IZM", "JBL", "JFU", "JG", "JKHY", "JKS", "JTAI", "JZ", "KARO", 
        "KC", "KD", "KDK", "KEEL", "KEYS", "KLAC", "KLAR", "KLIC", "KLTR", "KN", 
        "KNRX", "KOPN", "KOSS", "KPLT", "KSPI", "KTCC", "KULR", "KVYO", "LAES", "LASR", 
        "LAW", "LDOS", "LEDS", "LFUS", "LGCL", "LGL", "LHSW", "LIDR", "LIF", 
        "LINK", "LITE", "LOGI", "LPL", "LPSN", "LPTH", "LRCX", "LSAK", "LSCC", "LSPD", 
        "LTRX", "LYFT", "LYTS", "LZMH", "MANH", "MASK", "MCHP", "MCRP", "MDB", "MEI", 
        "MFI", "MGRT", "MIND", "MITK", "MITQ", "MKSI", "MLAB", "MLGO", "MNDO", "MNDY", 
        "MNTN", "MOBX", "MOVE", "MPTI", "MPWR", "MQ", "MRAM", "MRT", "MRVL", "MSAI", 
        "MSFT", "MSI", "MSN", "MSTR", "MTC", "MTEK", "MTLS", "MTSI", "MU", "MVIS", 
        "MX", "MXL", "MYSE", "MYSZ", "NA", "NABL", "NATL", "NAVN", "NBIS", "NCNO", 
        "NEON", "NET", "NICE", "NIQ", "NN", "NNDM", "NOK", "NOVT", "NOW", "NRDY", 
        "NSIT", "NTAP", "NTCL", "NTCT", "NTGR", "NTNX", "NTSK", "NTWK", "NUAI", "NVDA", 
        "NVEC", "NVMI", "NVNI", "NVTS", "NXPI", "NXPL", "NXT", "NXTT", "NYAX", "OBAI", 
        "OCC", "ODYS", "OKTA", "OLB", "OLED", "ON", "ONDS", "ONTO", "OOMA", 
        "OPTX", "ORCL", "ORIO", "ORKT", "OSIS", "OSPN", "OSS", "OTEX", "OUST", "OWLS", 
        "P", "PAGS", "PANW", "PAR", "PATH", "PAY", "PAYC", "PAYO", "PAYP", "PAYS", 
        "PAYX", "PCOR", "PCTY", "PD", "PDC", "PDFS", "PDYN", "PEGA", "PENG", "PERF", 
        "PGY", "PHUN", "PI", "PICS", "PLAB", "PLTR", "PLUS", "PLXS", "PN", "POET", 
        "PONY", "POWI", "PRGS", "PRSO", "PRTH", "PSFE", "PSN", "PSQH", "PTC", "PTRN", 
        "PUBM", "PXLW", "Q", "QBTS", "QCLS", "QCOM", "QLYS", "QMCO", "QNC", "QRVO", 
        "QTWO", "QUBT", "QUIK", "QXL", "RAL", "RAMP", "RBBN", "RBRK", "RCT", "RDVT", 
        "RDWR", "RDZN", "REFR", "REKR", "RELL", "RELY", "RGTI", "RIME", "RMBS", "RMNI", 
        "RMSG", "RNG", "ROC", "ROG", "ROP", "RPAY", "RPD", "RPGL", "RSKD", "RSSS", 
        "RTB", "RUN", "RXT", "RYDE", "RZLV", "S", "SABR", "SAGT", "SAIC", "SAIH", 
        "SAIL", "SANG", "SANM", "SAP", "SCKT", "SCOR", "SCSC", "SEDG", "SELX", "SHAZ", 
        "SHLS", "SHOP", "SILC", "SIMO", "SITM", "SKYT", "SLAB", "SLAI", "SMCI", "SMRT", 
        "SMSI", "SMTC", "SMTK", "SMWB", "SMXT", "SNDK", "SNOW", "SNPS", "SNX", "SOBR", 
        "SONM", "SONO", "SONY", "SOTK", "SOUN", "SPRU", "SPSC", "SPT", "SPWR", "SQNS", 
        "SRAD", "SSNC", "SSTI", "SSYS", "ST", "STM", "STNE", "STRC", "STX", "SUNE", 
        "SUPX", "SVCO", "SVRE", "SWKS", "SWMR", "SYNA", "SYNX", "TACT", "TAOP", "TAOX", 
        "TASK", "TBCH", "TCX", "TDC", "TDTH", "TDY", "TEAM", "TEL", "TENB", "TER", 
        "TGHL", "TGL", "THRY", "TLS", "TONX", "TOST", "TOYO", "TRAK", "TRMB", "TRT", 
        "TSAT", "TSEM", "TSM", "TSSI", "TTAN", "TTEC", "TTGT", "TTMI", "TURB", "TUYA", 
        "TWLO", "TXN", "TYGO", "TYL", "U", "UAVS", "UBER", "UBXG", "UCTT", "UEIC", 
        "UI", "UIS", "UMAC", "UMC", "UPBD", "UPLD", "USBC", "USIO", "UTSI", "VECO", 
        "VEEA", "VELO", "VERI", "VERX", "VHC", "VIA", "VIAV", "VICR", "VISN", 
        "VIVO", "VLN", "VNET", "VNT", "VPG", "VRNS", "VRRM", "VRSN", "VS", "VSAT", 
        "VSH", "VTEX", "VTIX", "VTSI", "VUZI", "VYX", "WATT", "WBX", "WCT", "WDAY", 
        "WDC", "WETH", "WETO", "WEX", "WIT", "WIX", "WK", "WKEY", "WLDS", "WLTH", 
        "WOLF", "WRAP", "WRD", "WTO", "WYFI", "WYY", "XBP", "XNDU", "XNET", 
        "XPER", "XYZ", "YAAS", "YALA", "YB", "YEXT", "YIBO", "YMM", "YMT", "YOU", 
        "YXT", "YYAI", "ZBRA", "ZENA", "ZEO", "ZEPP", "ZETA", "ZM", "ZS", "ZSQR",
    ],

    "Consumer Cyclical": [
        "AAP", "ABG", "ABLV", "ABNB", "ACEL", "ACVA", "ADNT", "AEO", "AHMA", "AIIO", 
        "AIN", "AKA", "ALH", "ALSN", "ALV", "AMBP", "AMCR", "AMWD", "AMZN", "AN", 
        "ANDG", "ANF", "AOUT", "APTV", "ARCO", "ARHS", "ARKO", "ARKR", "AS", "ASO", 
        "ATAT", "ATER", "ATMU", "AUR", "AVY", "AZI", "AZO", "BABA", "BALL", "BALY", 
        "BARK", "BBBY", "BBW", "BBWI", "BBY", "BC", "BDL", "BFAM", "BGI", "BGSI", 
        "BH", "BIRD", "BIRK", "BJRI", "BKE", "BKNG", "BLMN", "BNED", "BOBS", "BOOT", 
        "BQ", "BRAG", "BRCB", "BRIA", "BRLT", "BROS", "BRSL", "BSET", "BTBD", "BURL", 
        "BWA", "BWMX", "BYD", "BZH", "BZUN", "CAAS", "CAKE", "CAL", "CALY", "CARG", 
        "CART", "CASY", "CATO", "CAVA", "CBRL", "CCHH", "CCK", "CCL", "CDRO", "CENN", 
        "CGTL", "CHA", "CHDN", "CHH", "CHPT", "CHSN", "CHWY", "CLAR", "CLIK", "CMG", 
        "CNNE", "CNTY", "COLM", "COOK", "CPHC", "CPNG", "CPRI", "CPS", "CRI", "CRMT", 
        "CROX", "CRWS", "CSV", "CTRN", "CUK", "CULP", "CURV", "CVCO", "CVEO", "CVGI", 
        "CVNA", "CWH", "CYD", "CZR", "DAN", "DASH", "DBGI", "DBI", "DCH", "DCX", 
        "DDS", "DECK", "DFH", "DHI", "DIN", "DKNG", "DKS", "DLTH", "DOGZ", "DOO", 
        "DORM", "DPZ", "DRI", "DRVN", "DSS", "DXLG", "EAT", "EBAY", "ECX", "EFOI", 
        "EJH", "ELA", "EMPD", "ESCA", "ETD", "ETSY", "EVGO", "EVTV", "EXPE", "EYE", 
        "EZGO", "F", "FABC", "FFAI", "FGI", "FIGS", "FIVE", "FLL", "FLUT", "FLWS", 
        "FLXS", "FLYE", "FMFC", "FND", "FNKO", "FOSL", "FOXF", "FRSX", "FTDR", "FUN", 
        "FWDI", "FWRG", "GAMB", "GAP", "GBTG", "GCO", "GDHG", "GEF", "GENK", "GGR", 
        "GHG", "GIII", "GIL", "GLBE", "GM", "GME", "GNTX", "GOLF", "GOOS", "GPC", 
        "GPI", "GPK", "GRBK", "GRWG", "GT", "GTEC", "GTIM", "GTX", "H", "HAS", 
        "HBB", "HCHL", "HD", "HDL", "HEPS", "HERE", "HGV", "HLLY", "HLT", "HMC", 
        "HNI", "HOFT", "HOG", "HOUR", "HOV", "HRB", "HSAI", "HTHT", "HTLM", "HVT", 
        "HWH", "HYLN", "HZO", "IBP", "IHG", "INEO", "INSE", "INTG", "INVZ", "IP", 
        "IPW", "JACK", "JAKK", "JBDI", "JD", "JEM", "JILL", "JL", "JMIA", "JOUT", 
        "JRSH", "JWEL", "JXG", "JZXN", "KBH", "KEQU", "KMRK", "KMX", "KNDI", "KRT", 
        "KRUS", "KSS", "KTB", "KWY", "KXIN", "LAD", "LAKE", "LANV", "LCID", "LCII", 
        "LCUT", "LE", "LEA", "LEG", "LEGH", "LEN", "LESL", "LEVI", "LGIH", "LI", 
        "LIND", "LITB", "LIVE", "LKQ", "LOBO", "LOCO", "LOT", "LOVE", "LOW", "LQDT", 
        "LTH", "LUCK", "LULU", "LUXE", "LVLU", "LVS", "LVWR", "LZB", "M", "MAMO", 
        "MAR", "MAT", "MB", "MBC", "MBLY", "MBUU", "MCD", "MCFT", "MCRI", "MCW", 
        "MED", "MELI", "MGA", "MGIH", "MGM", "MHK", "MHO", "MI", "MKDW", "MLCO", 
        "MLKN", "MLR", "MMA", "MMYT", "MNRO", "MNSO", "MOD", "MOGU", "MOV", "MPAA", 
        "MPX", "MRM", "MSC", "MTH", "MTN", "MUSA", "MVST", "MWYN", "MYE", 
        "NAAS", "NATH", "NCI", "NCL", "NCLH", "NDLS", "NEGG", "NEXR", "NHTC", "NIO", 
        "NIU", "NKE", "NOMA", "NPT", "NTRP", "NTZ", "NVR", "NVVE", "NWTG", "OCG", 
        "OI", "OLPX", "ONEW", "ONON", "OPLN", "ORBS", "ORLY", "OSW", "OTH", "OXM", 
        "PACK", "PAG", "PASW", "PATK", "PDD", "PENN", "PETZ", "PHIN", "PHM", "PII", 
        "PKG", "PLBL", "PLBY", "PLCE", "PLNT", "PLOW", "PMNT", "PRKS", "PRPL", "PRSU", 
        "PRTS", "PSNY", "PTLE", "PTLO", "PTON", "PUSA", "PVH", "PZZA", "QS", "QSR", 
        "RACE", "RAVE", "RCKY", "RCL", "RDNW", "REAL", "REBN", "RECT", "REE", "RENT", 
        "RERE", "REYN", "RGS", "RH", "RICK", "RIVN", "RL", "ROL", "ROLR", "ROST", 
        "RRGB", "RRR", "RSI", "RUSHA", "RVLV", "SAH", "SBUX", "SCI", "SCVL", 
        "SDA", "SE", "SEGG", "SES", "SEV", "SFIX", "SG", "SGC", "SGHC", "SGI", 
        "SHAK", "SHOO", "SIG", "SKY", "SLDP", "SLGN", "SMJF", "SMP", "SN", "SNBR", 
        "SON", "SORA", "SPHL", "SPWH", "SRI", "SSM", "STKS", "STLA", "STRT", "SVV", 
        "SW", "SYPR", "TCOM", "TDUP", "THCH", "THO", "THRM", "TILE", "TJX", "TKLF", 
        "TLF", "TLYS", "TM", "TMHC", "TNL", "TOL", "TOUR", "TPH", "TPR", "TRIP", 
        "TRNR", "TRON", "TRS", "TRUG", "TSCO", "TSLA", "TXRH", "UA", "UAA", "UCAR", 
        "UFI", "ULTA", "URBN", "UXIN", "UZX", "VAC", "VC", "VEEE", "VENU", "VFC", 
        "VFS", "VGNT", "VIK", "VIOT", "VIPS", "VIRC", "VMAR", "VNCE", "VRA", "VSCO", 
        "VSTD", "VVV", "W", "WBUY", "WEN", "WEYS", "WGO", "WH", "WHR", "WINA", 
        "WING", "WKHS", "WKSP", "WNW", "WOOF", "WPRT", "WSM", "WWW", "WYNN", "XELB", 
        "XMAX", "XPEL", "XPEV", "XPOF", "YETI", "YHGJ", "YJ", "YTRA", "YUM", "YUMC", 
        "YYGH", "ZGN", "ZKH", "ZOOZ", "ZUMZ",
    ],

    "Consumer Defensive": [
        "AACG", "ABEV", "ABVE", "ACI", "ACU", "ADM", "AFRI", "AFYA", "AGCC", "AGRO", 
        "AGRZ", "AIIR", "AKO-A", "AKO-B", "ALCO", "AMBO", "ANDE", "APEI", "AQB", 
        "ATPC", "AVO", "BF-A", "BF-B", "BG", "BGS", "BHST", "BJ", "BOF", "BRBR", 
        "BRCC", "BRFH", "BRID", "BRLS", "BTI", "BUD", "BUDA", "BYAH", "BYND", "CAG", 
        "CALM", "CCEP", "CCU", "CELH", "CENT", "CENTA", "CHD", "CHEF", "CHGG", "CL", 
        "CLX", "COCO", "COE", "COKE", "COOT", "COST", "COTY", "COUR", "CPB", "CVGW", 
        "CVSA", "DAO", "DAR", "DDC", "DDL", "DEO", "DG", "DIT", "DLTR", "DNUT", 
        "DOLE", "DSY", "EDBL", "EDTK", "EDU", "EEIQ", "EL", "ELF", "EPC", 
        "EPSM", "EWCZ", "FAMI", "FC", "FCHL", "FDP", "FEDU", "FIZZ", "FLO", "FMX", 
        "FRPT", "FTLF", "GHC", "GIS", "GNLN", "GNS", "GO", "GOTU", "GROV", "GSUN", 
        "GV", "HAIN", "HCWC", "HELE", "HFFG", "HLF", "HNST", "HRL", "HSY", "IBG", 
        "IH", "IMKTA", "INGR", "IPAR", "ISPR", "JBS", "JBSS", "JDZG", "JJSF", "JVA", 
        "KDP", "KHC", "KIDZ", "KLC", "KMB", "KO", "KOF", "KR", "KVUE", "LAUR", 
        "LFVN", "LGCY", "LINC", "LMNR", "LND", "LOCL", "LOPE", "LRN", "LSF", "LW", 
        "LWAY", "LXEH", "MAGN", "MAMA", "MDLZ", "MEHA", "MGPI", "MH", "MICC", "MKC", 
        "MNST", "MO", "MSS", "MTEX", "MYND", "MZTI", "NAII", "NATR", "NCRA", "NGVC", 
        "NOMD", "NUS", "ODD", "OFRM", "OLLI", "ORIS", "OTLY", "PAVS", "PEP", 
        "PFAI", "PFGC", "PG", "PM", "POST", "PPC", "PRDO", "PRMB", "PSMT", "PXED", 
        "RAY", "REED", "RKDA", "RLX", "RMCF", "RYET", "RYM", "SAM", "SBEV", "SDOT", 
        "SENEA", "SFD", "SFM", "SJM", "SKIL", "SKIN", "SLSN", "SMPL", "SNDL", "SOWG", 
        "SPB", "SRXH", "STG", "STKH", "STRA", "STZ", "SYY", "TAL", "TANH", 
        "TAP", "TBBB", "TGT", "TPB", "TR", "TSN", "TWG", "UDMY", "UG", "UL", 
        "UNFI", "USFD", "USNA", "UTI", "UTZ", "UVV", "VFF", "VHUB", "VITL", "VLGEA", 
        "VSA", "WAFU", "WALD", "WEST", "WILC", "WMK", "WMT", "WVVI", "WYHG", "XXII", 
        "YHC", "YOUL", "YQ", "YSG", "YSWY", "ZVIA",
    ],

    "Energy": [
        "ACDC", "AEC", "AESI", "AM", "AMPY", "ANNA", "APA", "AR", "ARLP", "AROC",
        "BANL", "BATL", "BKR", "BKV", "BORR", "BP", "BRN", "BSM", "BTE", "BTU",
        "BWLP", "CAPL", "CCJ", "CHRD", "CKX", "CLB", "CLNE", "CMBT", "CNQ", "CNR",
        "CNX", "COP", "CQP", "CRC", "CRGY", "CRK", "CRT", "CSAN", "CTRA", "CVE",
        "CVI", "CVX", "DEC", "DHT", "DINO", "DK", "DKL", "DLNG", "DLXY", "DMLP",
        "DNN", "DTI", "DTM", "DVN", "DWSN", "E", "EC", "EE", "EFXT", "EGY",
        "ENB", "EOG", "EONR", "EP", "EPD", "EPM", "EPSN", "EQNR", "EQT",
        "ET", "EU", "EXE", "FANG", "FET", "FLNG", "FLOC", "FRO", "FTI", "FTK",
        "FTW", "GEL", "GEOS", "GFR", "GLND", "GLNG", "GLP", "GPOR", "GPRK", "GRNT",
        "GTE", "HAL", "HESM", "HLX", "HMH", "HNRG", "HP", "HPK", "IEP", "IMO",
        "IMPP", "INDO", "INR", "INSW", "INVX", "ISOU", "JAGU", "KGEI", "KGS", "KLXE",
        "KMI", "KNOP", "KNTK", "KOS", "KRP", "LB", "LBRT", "LEU", "LNG", "LPG",
        "LSE", "MARPS", "MGY", "MMLP", "MNR", "MPC", "MPLX", "MTDR", "MTR",
        "MUR", "MVO", "MXC", "NAT", "NBR", "NC", "NCSM", "NE", "NESR", "NEXT",
        "NFE", "NFG", "NGL", "NGS", "NINE", "NOA", "NOG", "NOV", "NPKI", "NRP",
        "NRT", "NUCL", "NVGS", "NXE", "OBE", "OII", "OIS", "OKE", "OMSE", "OVV",
        "OXY", "PAA", "PAGP", "PARR", "PBA", "PBF", "PBR", "PBR-A", "PBT", "PDS",
        "PED", "PNRG", "PR", "PROP", "PRT", "PSX", "PTEN", "PUMP", "PVL", "PXS",
        "RBNE", "RCON", "REI", "REPX", "RES", "RIG", "RNGR", "RRC", "SBR", "SD",
        "SDRL", "SEI", "SGU", "SHEL", "SJT", "SKYQ", "SLB", "SLNG", "SM", "SMC",
        "SND", "SOBO", "SOC", "STAK", "STNG", "SU", "SUN", "SUNC", "TALO", "TBN",
        "TDW", "TEN", "TGS", "TK", "TMDE", "TNK", "TOPS", "TORO", "TPET", "TPL",
        "TRGP", "TRMD", "TRP", "TS", "TTE", "TXO", "UEC", "UGP", "URG", "UROY",
        "USAC", "USEG", "UUUU", "VAL", "VET", "VG", "VIST", "VIVK", "VLO", "VNOM",
        "VOC", "VTOL", "VTS", "WBI", "WDS", "WES", "WFRD", "WHD", "WKC", "WMB",
        "WTI", "WTTR", "XOM", "XPRO", "YPF",
    ],

    "Financial": [
        "AIG", "ALL", "AMP", "AON", "AXP", "BAC", "BEN", "BK", "BLK", "BRK.B",
        "C", "CB", "CFG", "CME", "COF", "DFS", "FITB", "GS", "HBAN", "ICE",
        "IVZ", "JPM", "KEY", "L", "MCO", "MET", "MMC", "MS", "MSCI", "MTB",
        "NTRS", "NYCB", "PFG", "PGR", "PNC", "PRU", "RF", "SCHW", "SIVB", "SPGI",
        "STT", "SYF", "TFC", "TRV", "USB", "V", "WFC", "WRB", "ZION",
    ],

    "Healthcare": [
        "ABT", "ABBV", "ALGN", "AMGN", "BAX", "BDX", "BIIB", "BMY", "BSX", "CAH",
        "CI", "CNC", "COO", "CRL", "CVS", "DHR", "DGX", "ELV", "GILD", "HCA",
        "HOLX", "HUM", "IDXX", "ILMN", "INCY", "IQV", "ISRG", "JNJ", "LH", "LLY",
        "MCK", "MDT", "MRK", "MTD", "MRNA", "PKI", "PFE", "PODD", "REGN", "RMD",
        "ROL", "STE", "SYK", "TMO", "UNH", "VRTX", "WAT", "ZBH", "ZBRA", "ZTS",
    ],

    "Industrials": [
        "ALLE", "AME", "AOS", "CAT", "CHRW", "CMI", "CTAS", "DAL", "DE", "DOV",
        "ETN", "EFX", "EMR", "EXPD", "FAST", "FDX", "FTV", "GE", "GWW", "HON",
        "HWM", "IEX", "ITW", "JCI", "JBHT", "LDOS", "LHX", "LMT", "MAS", "MMM",
        "NOC", "ODFL", "PCAR", "PH", "PWR", "RHI", "ROK", "RTX", "SNA", "SWK",
        "TDG", "TT", "TXT", "UAL", "UNP", "UPS", "URI", "WAB", "WM", "XPO",
    ],

    "Real Estate": [
        "AIV", "AMT", "ARE", "AVB", "BXP", "CBRE", "CCI", "CPT", "DLR", "EQR",
        "ESS", "EXR", "FRT", "HST", "INVH", "IRM", "KIM", "MAA", "NNN", "O",
        "PLD", "PSA", "REG", "SBAC", "SLG", "SPG", "UDR", "VNO", "VTR", "WELL",
        "WY",
    ],

    "Utilities": [
        "AEE", "AEP", "AES", "AGIG", "AQN", "ARTNA", "ATO", "AVA", "AWK", "AWR",
        "AXIA", "BEP", "BEPC", "BESS", "BIP", "BIPC", "BKH", "BNRG", "CDZI", "CEG",
        "CEPU", "CIG", "CMS", "CNP", "CPK", "CREG", "CTRI", "CWCO", "CWEN", "CWT",
        "D", "DGXX", "DTE", "DUK", "ED", "EDN", "EIX", "ELLO", "ELPC", "EMA",
        "ENIC", "ENLT", "ES", "ETR", "EVRG", "EXC", "FE", "FLNC", "FTS",
        "GNE", "GWRS", "HE", "HTO", "HTOO", "IDA", "IMSR", "KEN", "KEP", "LNT",
        "MDU", "MGEE", "MSEX", "MWH", "NEE", "NGG", "NI", "NJR", "NKLR", "NRG",
        "NRGV", "NWE", "NWN", "NXXT", "OGE", "OGS", "OKLO", "OPAL", "ORA", "PCG",
        "PCYO", "PEG", "PNW", "POR", "PPL", "RGCO", "RNW", "SAFX", "SBS", "SO",
        "SPH", "SR", "SRE", "STEM", "SUUN", "SWX", "TAC", "TLN", "TXNM", "UGI",
        "UTL", "VGAS", "VST", "WAVE", "WEC", "WTRG", "XEL", "XIFR", "YORW",
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
        "FIBRAMQ12.MX", "FUNO11.MX",
        "FIBRAHD15.MX", "FIBRAUP18.MX", "FPLUS16.MX",
        "FVIA16.MX", "DANHOS13.MX",
    ],
    
    "ZAIK": [
        "QQQ", "VOO", "IAU", "IBIT", "TSLA", "AMZN", "META", "ORCL", "NFLX", "FIBRAPL14.MX",
        "FMTY14.MX", "DANHOS13.MX", "NVDA", "WMT", "NEM", "LAES", "RGTI", "1211N.MX", "BBAI", "DPZ",
        "XOM", "PDD", "LCID", "CVX", "SPOT", "NU", "BABA", "KO", "MSFT", "AAPL",
        "MU", "TSM", "PLTR", "GOOGL", "AEM", "CRWV", "BRK-B", "ASML", "GS", "BLK", "REGN", "JNJ", "MELI",
        "INTC", "APLD", "ZJK", "WATT", "AVGO", "XYZ", "AMD", "FTV", "SHOP", "UBER", "MSTR", "SMCI", "WDC",
        "CRM", "INUV", "HOOD", "V", "BAC", "AXP", "PM", "DIS", "BVS", "FUNO11.MX",
    ],
}

# ══════════════════════════════════════════════════════════════════════════
# FUNCIONES ANALÍTICAS
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

def formatear_market_cap(valor):
    if valor is None or pd.isna(valor):
        return "N/A"
    if valor >= 1e12:
        return f"{valor/1e12:.2f}T"
    elif valor >= 1e9:
        return f"{valor/1e9:.2f}B"
    elif valor >= 1e6:
        return f"{valor/1e6:.2f}M"
    return f"{valor:.0f}"

def descargar_lotes(tickers, historia, lote, progress_bar, status_text):
    frames_close, frames_vol = [], []
    total_lotes = -(-len(tickers) // lote)

    for i in range(0, len(tickers), lote):
        grupo = tickers[i:i + lote]
        lote_num = i // lote + 1
        status_text.text(f"⬇️  Descargando lote {lote_num}/{total_lotes}: {grupo[0]} … {grupo[-1]}")
        progress_bar.progress(int((lote_num / total_lotes) * 50))

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

def consultar_single_mcap(ticker):
    try:
        return ticker, yf.Ticker(ticker).info.get("marketCap", None)
    except Exception:
        return ticker, None

def obtener_market_caps_paralelo(tickers, max_workers, progress_bar, status_text):
    status_text.text(f"📊 Obteniendo Market Cap ({max_workers} hilos)…")
    market_caps = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futuros = {executor.submit(consultar_single_mcap, t): t for t in tickers}
        done = 0
        for futuro in as_completed(futuros):
            ticker, mcap = futuro.result()
            market_caps[ticker] = mcap
            done += 1
            progress_bar.progress(50 + int((done / len(tickers)) * 50))
    return market_caps

def correr_analisis(tickers, config, progress_bar, status_text):
    precios_df, volumen_df = descargar_lotes(
        tickers, config["historia"], config["lote"], progress_bar, status_text
    )

    if precios_df.empty:
        return pd.DataFrame()

    tickers_validos = precios_df.columns.tolist()
    dict_mcap = obtener_market_caps_paralelo(
        tickers_validos, config["max_workers"], progress_bar, status_text
    )

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
            "Ticker":    ticker,
            "Precio":    round(precio, 2),
            "RSI":       round(rsi_hoy, 2),
            "RSI Ayer":  round(rsi_ayer, 2),
            "% SMA20":   round(pct_sma20, 2),
            "% SMA50":   round(pct_sma50, 2),
            "% SMA200":  round(pct_sma200, 2),
            "MACD":      round(macd_hoy, 4),
            "Signal":    round(signal_hoy, 4),
            "Vol Hoy":   int(vol_hoy)    if vol_hoy    is not None else None,
            "Vol Avg20": int(vol_prom20) if vol_prom20 is not None else None,
            "Market Cap": formatear_market_cap(dict_mcap.get(ticker)),
            "Compra":    comprar,
            "Venta":     posible_venta,
            "Señal":     señal,
        })

    df = pd.DataFrame(resultados)
    if df.empty:
        return df

    df["_orden"] = df["Compra"].astype(int) * 2 + df["Venta"].astype(int)
    df = df.sort_values(["_orden", "RSI"], ascending=[False, True]).reset_index(drop=True)
    df.drop(columns=["_orden"], inplace=True)
    return df

# ══════════════════════════════════════════════════════════════════════════
# RENDERIZADO HTML DE TABLA
# ══════════════════════════════════════════════════════════════════════════

def render_tabla(df):
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

    def señal_html(s):
        if s == "COMPRAR":
            return '<span class="signal-buy">🟢 COMPRAR</span>'
        elif s == "POSIBLE VENTA":
            return '<span class="signal-sell">🔴 POSIBLE VENTA</span>'
        return '<span class="signal-neutral">🟡 NEUTRAL</span>'

    rows = ""
    for i, row in df.iterrows():
        rows += f"""
        <tr>
            <td>{i+1}</td>
            <td><span class="ticker-badge">{row['Ticker']}</span></td>
            <td>${row['Precio']:.2f}</td>
            <td>{rsi_html(row['RSI'])}</td>
            <td>{row['RSI Ayer']:.2f}</td>
            <td>{pct_html(row['% SMA20'])}</td>
            <td>{pct_html(row['% SMA50'])}</td>
            <td>{pct_html(row['% SMA200'])}</td>
            <td>{vol_html(row['Vol Hoy'], row['Vol Avg20'])}</td>
            <td>{formatear_volumen(row['Vol Avg20'])}</td>
            <td>{row['MACD']:.4f}</td>
            <td>{row['Signal']:.4f}</td>
            <td>{row['Market Cap']}</td>
            <td>{señal_html(row['Señal'])}</td>
        </tr>"""

    return f"""
    <div style="overflow-x:auto; margin-top:1rem;">
    <table class="screener-table">
        <thead>
            <tr>
                <th>#</th><th>Ticker</th><th>Precio</th><th>RSI</th><th>RSI Ayer</th>
                <th>% SMA20</th><th>% SMA50</th><th>% SMA200</th>
                <th>Vol Hoy</th><th>Vol Avg20</th>
                <th>MACD</th><th>Signal</th><th>MCap</th><th>Señal</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    </div>"""

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
    max_workers = st.slider("Hilos paralelos",   5,  30,  20)

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

# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════

st.markdown(f'<div class="main-header">SWING SCREENER</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="sub-header">sector · {sector_seleccionado.upper()} &nbsp;|&nbsp; '
    f'{len(SECTORES[sector_seleccionado])} tickers</div>',
    unsafe_allow_html=True
)

if correr:
    config = {
        "periodo_rsi":      periodo_rsi,
        "historia":         historia,
        "lote":             lote,
        "max_workers":      max_workers,
        "vol_periodo":      20,
        "rsi_sobre_comprado": rsi_sc,
        "rsi_sobre_vendido":  rsi_sv,
    }

    progress_bar = st.progress(0)
    status_text  = st.empty()

    tickers = SECTORES[sector_seleccionado]
    df_result = correr_analisis(tickers, config, progress_bar, status_text)

    progress_bar.empty()
    status_text.empty()

    if df_result.empty:
        st.error("❌ No se generaron resultados. Verifica la conexión o los tickers.")
    else:
        n_compra  = int(df_result["Compra"].sum())
        n_venta   = int(df_result["Venta"].sum())
        n_neutral = len(df_result) - n_compra - n_venta

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
        st.markdown(render_tabla(df_result), unsafe_allow_html=True)

        # CSV download
        csv = df_result.drop(columns=["Compra", "Venta"]).to_csv(index=False)
        st.download_button(
            label="⬇️  Descargar CSV",
            data=csv,
            file_name=f"screener_{sector_seleccionado.replace(' ','_')}.csv",
            mime="text/csv"
        )

else:
    st.markdown("""
    <div style="margin-top:3rem; text-align:center; color:#2a4060;">
        <div style="font-size:3rem; margin-bottom:1rem;">📊</div>
        <div style="font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:600; color:#3a5070;">
            Selecciona un sector en el panel izquierdo<br>y presiona <span style="color:#4fc3f7;">▶ CORRER ANÁLISIS</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
