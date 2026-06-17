import streamlit as st
import yfinance as yf
import pandas as pd
import logging
import warnings

warnings.filterwarnings("ignore")
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
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@400;600;800&display=swap');
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
    /* MACD Estado */
    .macd-cross-up   { color: #00e676; font-weight: 700; }
    .macd-cross-down { color: #ff5252; font-weight: 700; }
    .macd-above      { color: #69f0ae; }
    .macd-below      { color: #ff8a80; }
    .ticker-badge { background-color: #1a2d45; color: #4fc3f7; padding: 0.15rem 0.45rem;
                    border-radius: 4px; font-weight: 600; font-size: 0.75rem; letter-spacing: 0.05em; }
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
    .stProgress > div > div > div { background-color: #1976d2; }
    .filter-bar { background: linear-gradient(135deg, #0d1828 0%, #101e30 100%);
                  border: 1px solid #1a2d45; border-radius: 8px;
                  padding: 0.9rem 1.2rem 0.6rem 1.2rem; margin: 1rem 0 0.5rem 0; }
    .filter-title { font-size:0.68rem; letter-spacing:0.14em; text-transform:uppercase;
                    color:#4a7aaa; margin-bottom:0.6rem; }
    .result-count { font-size:0.72rem; color:#4a7aaa; letter-spacing:0.08em; margin-bottom:0.5rem; }
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
        "AAMI", "AB", "AFCG", "ALP", "ALTI", "AMG", "AMP", "AMTD", "APAM", "APO", 
        "ARCC", "ARES", "ASST", "AVX", "BAM", "BBDC", "BCG", "BCIC", "BCSF", "BEN", 
        "BENF", "BLK", "BN", "BNBX", "BNKK", "BPRE", "BTX", "BUR", "BX", "BXSL", 
        "CCAP", "CEF", "CFND", "CG", "CGBD", "CION", "CNS", "CRBG", "CSWC", "CWD", 
        "DBRG", "DFDV", "DXYZ", "EARN", "EQH", "EQS", "FDUS", "FGNX", "FHI", "FINS", 
        "FSK", "GAIN", "GBDC", "GCMG", "GECC", "GEG", "GLAD", "GROW", "GSBD", "GUG", 
        "HASI", "HERZ", "HLNE", "HNNA", "HRZN", "HSDT", "HTGC", "ICMB", "INV", "IVZ", 
        "JHG", "KBDC", "KKR", "LIEN", "MAAS", "MAIN", "MFIC", "MGLD", "MLCI", "MSDL", 
        "MSIF", "NCDL", "NDMO", "NMAI", "NMFC", "NOAH", "NTRS", "OBDC", "OCSL", "OFS", 
        "OIO", "OTF", "OWL", "OXSQ", "PAX", "PDCC", "PDX", "PFG", "PFLT", "PFX", 
        "PHYS", "PNNT", "PS", "PSBD", "PSEC", "PSLV", "RAND", "RFM", "RFMZ", "RJF", 
        "RMCO", "RMMZ", "RPC", "RSF", "RVI", "RWAY", "SABA", "SAMG", "SAR", "SATA", 
        "SCM", "SDEV", "SDHY", "SEIC", "SII", "SLRC", "SPMC", "SPPP", "SSSS", "STEP", 
        "STT", "TCPC", "TGE", "TPG", "TPVG", "TRIN", "TROW", "TSLX", "TWAV", "VCTR", 
        "VINP", "VRTS", "WDI", "WHF", "WHG", "WT", "ZSTK", "BAC", "BBVA", "BCS", 
        "BMO", "BNS", "BNY", "C", "CM", "HSBC", "ING", "JPM", "MUFG", "NTB", 
        "RY", "SAN", "SMFG", "TD", "UBS", "WFC", "ABCB", "ACNB", "AFBI", "AGBK", 
        "ALRS", "AMAL", "AMTB", "AROW", "ASB", "ASRV", "ATLO", "AUB", "AUBN", "AVAL", 
        "AVBC", "AVBH", "AX", "BAFN", "BANC", "BANF", "BANR", "BAP", "BBAR", "BBD", 
        "BBT", "BCAL", "BCBP", "BCH", "BCML", "BFC", "BFST", "BHB", "BHRB", "BKU", 
        "BLX", "BMA", "BMRC", "BOH", "BOKF", "BOTJ", "BPOP", "BPRN", "BRBS", "BSAC", 
        "BSBK", "BSBR", "BSRR", "BSVN", "BUSE", "BVFL", "BWB", "BWFG", "BY", 
        "BYFC", "CAC", "CARE", "CASH", "CATY", "CBAN", "CBC", "CBFV", "CBK", "CBNA", 
        "CBNK", "CBSH", "CBU", "CCB", "CCBG", "CCNE", "CFBK", "CFFI", "CFFN", "CFG", 
        "CFR", "CHCO", "CHMG", "CIB", "CIVB", "CLBK", "CLST", "CMTV", "CNOB", "COFS", 
        "COLB", "COSO", "CPBI", "CPF", "CTBI", "CUBI", "CVBF", "CWBC", "CZFS", "CZNC", 
        "CZWI", "DB", "DCOM", "EBC", "EBMT", "ECBK", "EFSC", "EFSI", "EGBN", "EQBK", 
        "ESQ", "EWBC", "FBIZ", "FBK", "FBLA", "FBNC", "FBP", "FCAP", "FCBC", "FCCO", 
        "FCF", "FCNCA", "FDBC", "FDSB", "FFBC", "FFIC", "FFIN", "FGBI", "FHB", "FHN", 
        "FIBK", "FINW", "FISI", "FITB", "FLG", "FMAO", "FMBH", "FMNB", "FNB", "FNLC", 
        "FNRN", "FNWB", "FNWD", "FRAF", "FRBA", "FRME", "FRST", "FSBC", "FSBW", "FSEA", 
        "FSUN", "FULT", "FUNC", "FUSB", "FVCB", "FXNC", "GABC", "GBCI", "GBFH", "GCBC", 
        "GGAL", "GSBC", "HAFC", "HBAN", "HBCP", "HBNC", "HBT", "HDB", "HFBL", "HFWA", 
        "HIFS", "HNVR", "HOMB", "HOPE", "HTB", "HWBK", "HWC", "HYNE", "IBCP", "IBN", 
        "IBOC", "IFS", "INBK", "INDB", "INTR", "ISBA", "ISTR", "ITUB", "JMSB", "KB", 
        "KEY", "KFFB", "KRNY", "LARK", "LC", "LCNB", "LKFN", "LOB", "LSBK", "LYG", 
        "MBBC", "MBIN", "MBWM", "MCB", "MCBS", "MCHB", "MFG", "MGYR", "MNSB", "MPB", 
        "MRBK", "MSBI", "MTB", "MVBF", "MYFW", "NBBK", "NBHC", "NBN", "NBTB", "NECB", 
        "NEWT", "NFBK", "NIC", "NKSH", "NPB", "NRIM", "NSTS", "NU", "NWBI", "NWFL", 
        "NWG", "OBK", "OBT", "OCFC", "OFG", "ONB", "OPBK", "OPHC", "ORRF", "OSBC", 
        "OVBC", "OVLY", "OZK", "PB", "PBFS", "PBHC", "PCB", "PDLB", "PEBK", "PEBO", 
        "PFBC", "PFIS", "PFS", "PGC", "PKBK", "PLBC", "PNBK", "PNC", "PNFP", "PRK", 
        "PROV", "QCRH", "RBB", "RBCAA", "RBKB", "RF", "RMBI", "RNST", "RRBI", "RVSB", 
        "SBCF", "SBFG", "SBSI", "SFBC", "SFBS", "SFNC", "SFST", "SHBI", "SHFS", "SHG", 
        "SMBC", "SMBK", "SPFI", "SRBK", "SRCE", "SSB", "SSBI", "STBA", "STEL", "SUPV", 
        "SYBT", "TBBK", "TCBI", "TCBK", "TCBS", "TCBX", "TFC", "TFIN", "TFSL", "THFF", 
        "TMP", "TOWN", "TRMK", "TRST", "TSBK", "UBCP", "UBSI", "UCB", "UMBF", "UNB", 
        "UNTY", "USB", "USCB", "UVSP", "VABK", "VBNK", "VLY", "WABC", "WAFD", "WAL", 
        "WASH", "WBS", "WF", "WNEB", "WSBC", "WSBF", "WSBK", "WSFS", "WTBA", "WTFC", 
        "ZION", "ABTC", "ABTS", "ANY", "ARBK", "ATCH", "AUC", "AURE", "AXG", "BGC", 
        "BGDE", "BMHL", "BMNR", "BRBI", "BRR", "BTBT", "BTCS", "BTGO", "BTM", "CANG", 
        "CD", "CLSK", "CNCK", "COHN", "CRCL", "CSHR", "DEFT", "DOMH", "ETOR", 
        "EVR", "FIGR", "FLD", "FUFU", "FUTU", "GEMI", "GLXY", "GOLD", "GRAN", "GREE", 
        "GS", "GSIW", "HGBL", "HIVE", "HLI", "HOOD", "HUT", "IBKR", "IPST", "IREN", 
        "JEF", "LAZ", "LGHL", "LMFA", "LPLA", "MARA", "MATH", "MC", "MDBH", 
        "MEGL", "MIAX", "MKTX", "MRX", "MS", "NAKA", "NCPL", "NCTY", "NMR", "OPY", 
        "PIPR", "PJT", "PLUT", "PMAX", "PURR", "PWP", "RIOT", "SBET", "SCHW", "SF", 
        "SIEB", "SLNH", "SNEX", "SOS", "SRL", "STEX", "STKE", "TIGR", "TOP", "TW", 
        "VIRT", "WAI", "WTF", "WULF", "XP", "AFRM", "AGM", "ALLY", "ANTA", "ATLC", 
        "AXP", "BFH", "CACC", "COF", "CPSS", "DXF", "ECPG", "ENVA", "EZPW", "FCFS", 
        "FINV", "FOA", "GDOT", "HTT", "JCAP", "JF", "JFIN", "LPRO", "LU", "LX", 
        "MA", "MFIN", "NAVI", "NNI", "OMF", "OPFI", "OPRT", "PMTS", "PRAA", "PYPL", 
        "QFIN", "RM", "SEZL", "SLM", "SNTG", "SOFI", "SUIG", "SYF", "TROO", "UPST", 
        "V", "VRM", "WRLD", "WU", "XYF", "YRD", "FRHC", "HTH", "IX", "RILY", 
        "TREE", "VOYA", "BTOG", "CBOE", "CME", "COIN", "DTCX", "FDS", "ICE", "MCO", 
        "MKTW", "MORN", "MSCI", "NDAQ", "SPGI", "TRU", "VALU", "ACGL", "AEG", "AIG", 
        "BNT", "BRK-A", "BRK-B", "HIG", "IGIC", "PLGO", "SLF", "WDH", "XZO", "AAME", 
        "ABX", "AFL", "BHF", "CIA", "CNO", "FG", "GL", "GNW", "JXN", "LNC", 
        "MET", "MFC", "PRI", "PRU", "PUK", "SNFCA", "UNM", "ACIC", "AFG", "AII", 
        "AIZ", "ALL", "ASIC", "BOW", "CB", "CINF", "CNA", "DGICA", "GBLI", "HCI", 
        "HGTY", "HIPO", "HMN", "HRTG", "KINS", "KMPR", "KNSL", "L", "LMND", "MCY", 
        "MKL", "NODK", "ORI", "PGR", "PLMR", "PRA", "PRCH", "PRHI", "RLI", "ROOT", 
        "SAFT", "SIGI", "SKWD", "SLDE", "STC", "THG", "TRUP", "TRV", "UFCS", "UVE", 
        "WRB", "WTM", "EG", "GLRE", "HG", "KG", "OXBR", "RGA", "RNR", "SPNT", 
        "ACT", "AGO", "AMSF", "AXS", "EIG", "ESNT", "FAF", "FNF", "ITIC", "JRVR", 
        "MBI", "MTG", "NMIH", "OSG", "RDN", "RYAN", "TIPT", "AIFU", "AJG", "AON", 
        "ARX", "BRO", "BWIN", "CRD-A", "CRD-B", "CRVL", "EHTH", "ERIE", "EZRA", "GOCO", 
        "GSHD", "HUIZ", "LIFE", "MRSH", "NP", "SLQT", "TWFG", "WTW", "XHG", "ZBAO", 
        "BETR", "BLNE", "CNF", "GHI", "IOR", "LDI", "ONIT", "PAPL", "PFSI", "RKT", 
        "UWMC", "VEL", "WD",
    ],
    "ETFs": [
        "SPY", "VOO", "IVV", "QQQ", "QQQM", "IWM", "TLT", "GLD",
        "AAAU", "AAXJ", "ACES", "ACWI", "ACWX", "AFK", "AGG", "AIA", "AIQ", "AMLP",
        "AMZA", "ANGL", "ARGT", "ARKG", "ARKQ", "ARKK", "ASHR", "ATMP", "AWAY", "AWP",
        "BAR", "BATT", "BBH", "BBP", "BFOR", "BIB", "BIL", "BIS", "BJK", "BLCN",
        "BLOK", "BND", "BNDX", "BNO", "BOTZ", "BUG", "CHIQ", "CLOU", "CNYA", "COPX",
        "CORP", "COWZ", "CPER", "CQQQ", "CRBN", "CUT", "CXSE", "DBA", "DBB", "DBC",
        "DBEF", "DEM", "DFEN", "DGRO", "DGS", "DIA", "DRIV", "DSI", "DVY", "DXJ",
        "EAGG", "ECH", "EDEN", "EDIV", "EDV", "EEM", "EEMA", "EFA", "EFAV", "EFG",
        "EFV", "ELD", "EMB", "EMGF", "EMLP", "ENFR", "EPP", "EPU", "EZA", "FAD",
        "FALN", "FAN", "FBT", "FCOM", "FDN", "FEMS", "FENY", "FILL", "FINX",
        "FITE", "FLOT", "FLRN", "FNDA", "FNDB", "FNDC", "FNDE", "FNDF", "FNDX", "FPE",
        "FREL", "FRI", "FTSD", "FTSM", "FVD", "FXI", "FXO", "GAMR", "GDX", "GDXJ",
        "GEM", "GIGB", "GLDM", "GOVT", "GRID", "GXC", "GXG", "HACK", "HAIL", "HAUS",
        "HDV", "HEAL", "HEFA", "HEWJ", "HERO", "HFXI", "HOMZ", "HYG", "HYLB", "HYS",
        "HYXF", "IAI", "IAT", "IAU", "IBB", "IBUY", "ICF", "ICLN", "ICSH", "IDNA",
        "IDRV", "IDX", "IEF", "IEI", "IEO", "IEUR", "IEZ", "IFGL", "IGLB", "IGSB",
        "IGV", "IHE", "IHI", "IHAK", "IJK", "IJJ", "IJR", "IJS", "ILF", "INDA",
        "INDS", "IPAC", "IPAY", "IRBO", "ITA", "ITB", "IVW", "IWB", "IWC", "IWD",
        "IWF", "IWN", "IWO", "IWP", "IWR", "IWS", "IWV", "IXC", "IYF", "IYG",
        "IYH", "IYJ", "IYK", "IYM", "IYR", "IYT", "IYW", "JETS", "JKF", "JKG",
        "JKH", "JKI", "JKK", "JPST", "KARS", "KBA", "KBWB", "KBWP", "KBWR", "KBWY",
        "KIE", "KLD", "KOMP", "KRE", "KSA", "KWEB", "LABD", "LABU", "LEGR", "LEMB",
        "LIT", "LKOR", "LOUP", "LOWC", "LQD", "MBB", "MCHI", "MDY", "MDYG", "MDYV",
        "MINT", "MISL", "MLPA", "MLPX", "MOO", "MORT", "MTUM", "MUB", "NEAR",
        "NETL", "NOBL", "NUKZ", "NUMG", "OEF", "OIH", "ONLN", "OUNZ", "PALL", "PBD",
        "PBW", "PCY", "PDBC", "PEJ", "PEX", "PFF", "PFFD", "PFFR", "PHO", "PICK",
        "PPLT", "PPA", "PPTY", "PRNT", "PSJ", "PSK", "PULS", "PXE", "PXI", "QAT",
        "QCLN", "QLTA", "REET", "REM", "REMX", "REZ", "RGI", "RHS", "RNRG", "ROBO",
        "RYE", "RYF", "RYH", "RYT", "RYU", "SBIO", "SCHA", "SCHB", "SCHC", "SCHD",
        "SCHE", "SCHF", "SCHG", "SCHH", "SCHI", "SCHJ", "SCHM", "SCHO", "SCHP", "SCHQ",
        "SCHR", "SCHV", "SCHX", "SCHZ", "SCZ", "SDY", "SGOL", "SGOV", "SHE",
        "SHV", "SHY", "SHYG", "SIL", "SIVR", "SKYY", "SLQD", "SLV", "SLYG", "SLYV",
        "SMH", "SMOG", "SNPE", "SOCL", "SOXX", "SPIB", "SPLB", "SPLG", "SPSB",
        "SPYD", "SPYG", "SPYM", "SPYV", "SPYX", "SRET", "SRVR", "SUSA", "SUSC",
        "SUSL", "TAN", "TFLO", "THD", "TIP", "TLH", "TPAY", "TPYP", "TUR", "UAE",
        "UNG", "URA", "USFR", "USHY", "USIG", "USMV", "USO", "USRT", "USSG", "VAW",
        "VB", "VBR", "VBK", "VCAR", "VCIT", "VCLT", "VCR", "VCSH", "VDC", "VDE",
        "VEA", "VEGI", "VFH", "VGIT", "VGK", "VGLT", "VGSH", "VGT", "VHT", "VIG",
        "VIOO", "VIOG", "VIOV", "VIS", "VNM", "VNQ", "VONE", "VONG", "VONV", "VOX",
        "VPU", "VRIG", "VRP", "VTEB", "VTHR", "VTI", "VTIP", "VTWO", "VUG", "VUSE",
        "VXUS", "VWOB", "WCBR", "WCLD", "WOMN", "WOOD", "XAR", "XBI", "XLB", "XLC",
        "XLE", "XLF", "XLK", "XLI", "XLP", "XLRE", "XLU", "XLV", "XLY", "XOP",
        "XPH", "XSD", "XSW", "XTL", "XTN", "ZROZ",
    ],
    "SHELL COMPANIES": [
        "AACB", "AACI", "AACO", "ACAA", "ACGCU", "ADAC", "AEAQ", "AEXA", "AFJK", "AIIA",
        "ALCY", "ALDF", "ALF", "ALIS", "ALOV", "ALUB", "ANSC", "APAC", "APAD", "APXT",
        "ARCI", "ARCLU", "ARTC", "ASPC", "ATII", "AXIN", "BACC", "BAYA", "BBCQ", "BCAR",
        "BCSS", "BDCI", "BEAG", "BEBE", "BHAV", "BIII", "BIXI", "BKHA", "BLRK", "BLUW",
        "BLZR", "BPAC", "BSAA", "CAEP", "CAIIU", "CAPN", "CAQ", "CCII", "CCIX", "CCXI",
        "CEPF", "CEPO", "CEPS", "CEPT", "CEPV", "CGCT", "CHAR", "CHEC", "CHPG", "CLBR",
        "CMII", "COLA", "COPL", "CRAC", "CRAN", "CRAQ", "CTAA", "CUB", "CXIIU", "DAAQ",
        "DBCA", "DMAA", "DMII", "DNMX", "DRDB", "DSAC", "DTSQ", "DYNC", "DYOR", "EGHA",
        "EMIS", "EURK", "EVAC", "EVOX", "FACT", "FCRS", "FERA", "FGII", "FGMC", "FIGX",
        "FMACU", "FSHP", "FTHAU", "FVAV", "FVN", "GCGRU", "GIG", "GIW", "GIX", "GLED",
        "GPAC", "GPAT", "GRAF", "GSHR", "GSRF", "GTEN", "GTERA", "HACQ", "HAVA", "HCAC",
        "HCIC", "HCMA", "HLXC", "HSPT", "HVII", "HVMC", "IACO", "IACQU", "IBAC", "IEAG",
        "IGAC", "ILLU", "INAC", "IPCX", "IPEX", "IPFXU", "IPOD", "IRAB", "IRHO", "ITHA",
        "JACS", "JATT", "JENA", "KBON", "KCHV", "KFII", "KOYN", "KRAQ", "KRSP", "KTWO",
        "KVAC", "LAFA", "LATA", "LCCC", "LEGO", "LEGT", "LFAC", "LION", "LKSP", "LOKV",
        "LPAA", "LPBB", "LPCV", "LWAC", "MACI", "MBAV", "MBVI", "MCAHU", "MCGA", "MESH",
        "MEVO", "MKLY", "MLAA", "MLAC", "MMTX", "MTAL", "MUZE", "MZYX", "NBRG", "NHIC",
        "NHIVU", "NMP", "NOEM", "NPAC", "NTWO", "NWAX", "OACC", "OBA", "OIM", "ONCH",
        "ORIQ", "OTGA", "OYSE", "PAAC", "PACH", "PAII", "PALO", "PCAP", "PCSC", "PGAC",
        "PLMK", "PMTR", "POLE", "PTOR", "QADRU", "QETA", "QSEA", "QUMS", "RAAQ", "RAC",
        "RANG", "RDAC", "RDAG", "RFAI", "RFAM", "RIBB", "RNGT", "RREVU", "RTAC", "SAAQ",
        "SAC", "SBXD", "SBXE", "SCII", "SCPQ", "SDHI", "SIMA", "SOCA", "SORN", "SOUL",
        "SPEG", "SPKL", "SSAC", "SSEA", "SUMA", "SVAC", "SVAQ", "SVCC", "SVIV", "SZZL",
        "TACH", "TACO", "TAVI", "TDAC", "TDWD", "TLNC", "TMTS", "TRAD", "TRGS", "TVA",
        "TVAI", "TWLV", "UAC", "UYSC", "VACH", "VACI", "VNME", "WENN", "WLAC", "WLII",
        "WPAC", "WSTN", "WTG", "XCBE", "XFLH", "XRPN", "XSLL", "XXI", "YCY", "YHNA",
        "ZKP",
    ],
    "Healthcare": [
        "A", "AAPG", "AARD", "ABBV", "ABCL", "ABEO", "ABOS", "ABSI", "ABT", "ABUS", 
        "ABVC", "ABVX", "ACAD", "ACB", "ACET", "ACH", "ACHC", "ACHV", "ACIU", "ACOG", 
        "ACON", "ACRS", "ACRV", "ACTU", "ACXP", "ADAG", "ADCT", "ADGM", "ADIL", "ADMA", 
        "ADPT", "ADTX", "ADUS", "ADVB", "ADXN", "AEMD", "AEON", "AGEN", "AGIO", "AGL", 
        "AGMB", "AHCO", "AHG", "AIDX", "AIM", "AIRS", "AKAN", "AKBA", "AKTS", "AKTX", 
        "ALC", "ALDX", "ALEC", "ALGN", "ALGS", "ALHC", "ALKS", "ALLO", "ALLR", "ALMR", 
        "ALMS", "ALNY", "ALPS", "ALT", "ALVO", "ALXO", "ALZN", "AMGN", "AMIX", "AMLX", 
        "AMN", "AMPH", "AMRN", "AMRX", "AMS", "AMWL", "ANAB", "ANGO", "ANIK", "ANIP", 
        "ANIX", "ANL", "ANNX", "ANRO", "ANTX", "ANVS", "AORT", "APGE", "APLM", "APLS", 
        "APM", "APRE", "APUS", "APVO", "APYX", "AQST", "ARAY", "ARCT", "ARDT", "ARDX", 
        "ARGX", "ARMP", "ARQT", "ARTL", "ARTV", "ARVN", "ARWR", "ASBP", "ASMB", "ASND", 
        "ASRT", "ASTH", "ATAI", "ATEC", "ATHE", "ATNM", "ATOS", "ATR", "ATRA", "ATRC", 
        "ATYR", "AUNA", "AUPH", "AURA", "AUTL", "AVAH", "AVBP", "AVIR", "AVLN", "AVNS", 
        "AVR", "AVTR", "AVTX", "AVXL", "AXGN", "AXSM", "AYTU", "AZN", "AZTA", "AZTR", 
        "BAX", "BBIO", "BBLG", "BBNX", "BBOT", "BCAB", "BCAX", "BCDA", "BCRX", "BCTX", 
        "BCYC", "BDMD", "BDRX", "BDSX", "BDTX", "BDX", "BEAM", "BEAT", "BFLY", "BFRG", 
        "BFRI", "BGM", "BGMS", "BHC", "BHVN", "BIAF", "BIIB", "BIO", "BIOA", "BIVI", 
        "BJDX", "BKD", "BLCO", "BLFS", "BLLN", "BLRX", "BLTE", "BMEA", "BMGL", "BMRA", 
        "BMRN", "BMY", "BNGO", "BNR", "BNTC", "BNTX", "BOLD", "BOLT", "BRKR", "BRNS", 
        "BRTX", "BSX", "BTAI", "BTMD", "BTSG", "BVS", "BWAY", "BYSI", "CABA", "CABR", 
        "CADL", "CAH", "CAI", "CALC", "CAMP", "CANF", "CAPR", "CARL", "CATX", "CBIO", 
        "CBLL", "CBUS", "CCCC", "CCEL", "CCLD", "CCM", "CCRN", "CDIO", "CDNA", "CDT", 
        "CDXS", "CELC", "CELU", "CELZ", "CERS", "CERT", "CGC", "CGEM", "CGEN", "CGON", 
        "CGTX", "CHE", "CHRS", "CI", "CING", "CLDI", "CLDX", "CLGN", "CLLS", "CLNN", 
        "CLOV", "CLPT", "CLRB", "CLYM", "CMMB", "CMND", "CMPS", "CMPX", "CNC", "CNMD", 
        "CNSP", "CNTA", "CNTB", "CNTN", "CNTX", "COAG", "COCH", "COCP", "CODX", "COGT", 
        "COLL", "CON", "COO", "COR", "CORT", "COSM", "COYA", "CPHI", "CPIX", "CPRX", 
        "CRBP", "CRBU", "CRDF", "CRDL", "CRIS", "CRL", "CRMD", "CRNX", "CRON", "CRSP", 
        "CRVO", "CRVS", "CSBR", "CSTL", "CTEV", "CTKB", "CTMX", "CTNM", "CTOR", "CTSO", 
        "CTXR", "CUE", "CUPR", "CURX", "CV", "CVKD", "CVM", "CVRX", "CVS", "CYCN", 
        "CYH", "CYPH", "CYTK", "DARE", "DBVT", "DCGO", "DCOY", "DCTH", "DERM", "DFTX", 
        "DGX", "DH", "DHR", "DMAC", "DMRA", "DNA", "DNLI", "DNTH", "DOCS", "DRIO", 
        "DRMA", "DRTS", "DRUG", "DSGN", "DTIL", "DVA", "DWTX", "DXCM", "DXR", "DYAI", 
        "DYN", "EBS", "ECOR", "EDAP", "EDIT", "EDSA", "EHAB", "EHC", "EIKN", "ELAB", 
        "ELAN", "ELDN", "ELMD", "ELTX", "ELUT", "ELV", "ELVN", "EMBC", "ENGN", "ENLV", 
        "ENOV", "ENSC", "ENSG", "ENTA", "ENTX", "ENVB", "EOLS", "EPRX", "EQ", "ERAS", 
        "ERNA", "ESLA", "ESPR", "ESTA", "ETON", "EVAX", "EVGN", "EVH", "EVMN", "EVO", 
        "EW", "EWTX", "EXEL", "EXOZ", "EYPT", "FATE", "FBIO", "FBLG", "FBRX", "FDMT", 
        "FEED", "FEMY", "FENC", "FHTX", "FLGT", "FLNA", "FMS", "FONR", "FORA", "FTRE", 
        "FULC", "GALT", "GANX", "GCTK", "GDRX", "GDTC", "GEHC", "GELS", "GENB", "GERN", 
        "GH", "GHRS", "GILD", "GKOS", "GLMD", "GLSI", "GLUE", "GMAB", "GMED", "GNLX", 
        "GNPX", "GNTA", "GOSS", "GOVX", "GPCR", "GRAL", "GRCE", "GRDN", "GRDX", "GRFS", 
        "GRI", "GSK", "GTBP", "GUTS", "GYRE", "HAE", "HALO", "HBIO", "HCA", "HCAT", 
        "HCM", "HCSG", "HCTI", "HCWB", "HELP", "HIMS", "HIND", "HITI", "HKPD", "HLN", 
        "HNGE", "HOTH", "HOWL", "HQY", "HRMY", "HROW", "HRTX", "HSCS", "HSIC", "HSTM", 
        "HTFL", "HUM", "HUMA", "HURA", "HYFT", "HYPD", "HYPR", "IART", "IBIO", "IBO", 
        "IBRX", "ICCC", "ICCM", "ICLR", "ICU", "ICUI", "IDXX", "IDYA", "IFRX", "IGC", 
        "IKT", "ILMN", "IMA", "IMCC", "IMCR", "IMDX", "IMMP", "IMMX", "IMNM", "IMNN", 
        "IMRN", "IMRX", "IMTX", "IMUX", "IMVT", "INAB", "INBS", "INBX", "INCR", "INCY", 
        "INDP", "INDV", "INFU", "INGN", "INKT", "INM", "INMB", "INMD", "INNV", "INO", 
        "INSM", "INSP", "INTS", "INVA", "IONS", "IOVA", "IPHA", "IPSC", "IQV", "IRD", 
        "IRIX", "IRMD", "IRON", "IRTC", "IRWD", "ISPC", "ISRG", "ITGR", "ITOC", "IVA", 
        "IVF", "IVVD", "IXHL", "JAGX", "JAN", "JANX", "JAZZ", "JBIO", "JNJ", "JSPR", 
        "JUNS", "JYNT", "KALA", "KALV", "KAPA", "KIDS", "KLRA", "KLRS", "KMDA", "KMTS", 
        "KNSA", "KOD", "KPRX", "KPTI", "KRMD", "KROS", "KRRO", "KRYS", "KTTA", "KURA", 
        "KYMR", "KYNB", "KYTX", "KZIA", "KZR", "LAB", "LABT", "LBRX", "LCTX", "LEGN", 
        "LENZ", "LEXX", "LFCR", "LFMD", "LFST", "LFWD", "LGND", "LGVN", "LH", "LIMN", 
        "LITS", "LIVN", "LIXT", "LKFT", "LLY", "LMAT", "LMRI", "LNAI", "LNSR", "LNTH", 
        "LONA", "LPCN", "LQDA", "LRMR", "LSTA", "LTRN", "LUCD", "LUCY", "LUNG", "LXEO", 
        "LXRX", "LYEL", "MAIA", "MANE", "MASI", "MASS", "MAZE", "MBAI", "MBIO", "MBOT", 
        "MBRX", "MBX", "MCK", "MCRB", "MD", "MDAI", "MDCX", "MDGL", "MDLN", "MDT", 
        "MDWD", "MDXG", "MDXH", "MEDP", "MENS", "MESO", "MGNX", "MGRX", "MGTX", "MGX", 
        "MIRA", "MIRM", "MIST", "MLEC", "MLSS", "MLTX", "MLYS", "MMED", "MMSI", "MNDR", 
        "MNKD", "MNOV", "MNPR", "MODD", "MOH", "MOLN", "MPLT", "MREO", "MRK", "MRKR", 
        "MRNA", "MRVI", "MSLE", "MTD", "MTNB", "MTVA", "MXCT", "MYGN", "MYO", "NAGE", 
        "NAMS", "NAUT", "NBIX", "NBP", "NBTX", "NCEL", "NCNA", "NDRA", "NEO", "NEOG", 
        "NEPH", "NERV", "NEUP", "NGEN", "NGNE", "NHC", "NIVF", "NKTR", "NKTX", "NMRA", 
        "NMTC", "NNNN", "NNOX", "NNVC", "NOTV", "NPCE", "NRC", "NRIX", "NRSN", "NRXP", 
        "NRXS", "NSPR", "NSRX", "NSYS", "NTHI", "NTLA", "NTRA", "NTRB", "NUTX", "NUVB", 
        "NUVL", "NUWE", "NVAX", "NVCR", "NVCT", "NVNO", "NVO", "NVS", "NVST", "NXGL", 
        "NXL", "NXTC", "NYXH", "OABI", "OBIO", "OCGN", "OCS", "OCUL", "OFIX", "OGEN", 
        "OGI", "OGN", "OKUR", "OKYO", "OLMA", "OM", "OMCL", "OMDA", "OMER", "ONC", 
        "ONCO", "ONCY", "ONMD", "OPCH", "OPK", "OPRX", "ORGO", "ORIC", "ORKA", "ORMP", 
        "OSCR", "OSRH", "OSTX", "OSUR", "OTLK", "OVID", "OWLT", "PACB", "PACS", "PAHC", 
        "PALI", "PARK", "PASG", "PAVM", "PBH", "PBM", "PBYI", "PCRX", "PCSA", "PCVX", 
        "PDEX", "PDSB", "PEN", "PEPG", "PETS", "PFE", "PFSA", "PGEN", "PGNY", "PHAR", 
        "PHAT", "PHG", "PHGE", "PHIO", "PHR", "PHVS", "PIII", "PLRX", "PLRZ", "PLSE", 
        "PLSM", "PLUR", "PLX", "PLYX", "PMCB", "PMI", "PMN", "PMVP", "PNTG", "POAS", 
        "POCI", "PODD", "POM", "PPBT", "PPCB", "PRAX", "PRCT", "PRE", "PRFX", "PRGO", 
        "PRLD", "PRME", "PROF", "PROK", "PRPO", "PRQR", "PRTA", "PRTC", "PRVA", "PSNL", 
        "PSTV", "PTCT", "PTGX", "PTHS", "PTN", "PULM", "PVLA", "PYPD", "PYXS", "QDEL", 
        "QGEN", "QNCX", "QNRX", "QNTM", "QSI", "QTEX", "QTI", "QTRX", "QTTB", "QUCY", 
        "QURE", "RADX", "RANI", "RAPP", "RARE", "RCEL", "RCKT", "RCUS", "RDGT", "RDHL", 
        "RDNT", "RDY", "REGN", "REPL", "REVB", "RGC", "RGEN", "RGNT", "RGNX", "RIGL", 
        "RLAY", "RLMD", "RLYB", "RMD", "RMTI", "RNA", "RNAC", "RNAZ", "RNTX", "RNXT", 
        "ROIV", "RPID", "RPRX", "RVMD", "RVP", "RVTY", "RXRX", "RXST", "RYTM", "RZLT", 
        "SABS", "SANA", "SBFM", "SCLX", "SCNI", "SCNX", "SCYX", "SDGR", "SEER", "SEM", 
        "SENS", "SEPN", "SER", "SERA", "SGHT", "SGMT", "SGP", "SGRY", "SHC", "SHPH", 
        "SI", "SIBN", "SIGA", "SILO", "SINT", "SION", "SKYE", "SLDB", "SLGL", "SLN", 
        "SLNO", "SLP", "SLS", "SLXN", "SMMT", "SMTI", "SNDA", "SNDX", "SNGX", "SNN", 
        "SNOA", "SNSE", "SNTI", "SNWV", "SNY", "SNYR", "SOLV", "SOPH", "SPOK", "SPRB", 
        "SPRC", "SPRO", "SPRY", "SPTX", "SRPT", "SRRK", "SRTA", "SRTS", "SRZN", "SSII", 
        "STAA", "STE", "STIM", "STOK", "STRO", "STSS", "STTK", "STVN", "STXS", "SUPN", 
        "SVRA", "SXTC", "SXTP", "SY", "SYK", "SYRE", "TAK", "TALK", "TARA", "TARS", 
        "TBPH", "TBRG", "TCMD", "TCRT", "TCRX", "TDOC", "TECH", "TECX", "TELA", "TELO", 
        "TEM", "TENX", "TEVA", "TFX", "TGTX", "THC", "TIL", "TKNO", "TLPH", "TLRY", 
        "TLSA", "TLSI", "TLX", "TMCI", "TMDX", "TMO", "TNDM", "TNGX", "TNON", "TNXP", 
        "TNYA", "TOI", "TOVX", "TPST", "TRAW", "TRAX", "TRDA", "TRIB", "TRVI", "TSHA", 
        "TTRX", "TVGN", "TVRD", "TVTX", "TWST", "TXG", "TXMD", "TYRA", "UFPT", "UHS", 
        "UNCY", "UNH", "UPB", "UPC", "URGN", "USPH", "UTHR", "UTMD", "VALN", "VANI", 
        "VBIO", "VCEL", "VCYT", "VEEV", "VERA", "VERU", "VIR", "VIVS", "VKTX", "VMD", 
        "VNDA", "VNRX", "VOR", "VRAX", "VRCA", "VRDN", "VREX", "VRTX", "VSEE", "VSTM", 
        "VTAK", "VTGN", "VTRS", "VTVT", "VVOS", "VYGR", "VYNE", "WAT", "WAY", "WEAV", 
        "WGRX", "WGS", "WHWK", "WOK", "WRBY", "WST", "WVE", "WW", "XAIR", "XBIO", 
        "XBIT", "XCUR", "XENE", "XERS", "XFOR", "XGN", "XLO", "XNCR", "XOMA", "XRAY", 
        "XRTX", "XTLB", "XTNT", "XWEL", "YCBD", "YDES", "YI", "ZBH", "ZBIO", "ZCMD", 
        "ZJYL", "ZLAB", "ZNTL", "ZTEK", "ZTS", "ZURA", "ZVRA", "ZYBT", "ZYME"
    ],
    "Industrials": [
        "AAL", "AAON", "ABAT", "ABM", "ACA", "ACCL", "ACCO", "ACHR", "ACM", "ACTG",
        "ADSE", "ADT", "ADUR", "AEBI", "AEHL", "AEIS", "AER", "AERO", "AERT", "AGCO",
        "AGX", "AIHS", "AIR", "AIRI", "AIRJ", "AIRO", "AIRT", "AIT", "ALG",
        "ALGT", "ALK", "ALLE", "ALTG", "AME", "AMPX", "AMRC", "AMSC", "AMTM", "ANPA",
        "AOS", "AP", "APG", "APOG", "APT", "APWC", "AQMS", "ARCB", "ARLO", "ARMK",
        "ARQ", "ARTW", "ARXS", "ASC", "ASLE", "ASPN", "ASR", "ASTE", "ATI", "ATKR",
        "ATLN", "ATRO", "ATS", "ATXG", "AVAV", "AVEX", "AWI", "AWX", "AXON", "AYI",
        "AZZ", "BA", "BAER", "BAH", "BBCP", "BBSI", "BBUC", "BCHT", "BCO", "BEEP",
        "BETA", "BGSF", "BKSY", "BLBD", "BLD", "BLDP", "BLDR", "BLNK", "BNC", "BOC",
        "BOOM", "BRC", "BTOC", "BURU", "BUUU", "BV", "BW", "BWEN", "BWMN", "BWXT",
        "BXC", "BYRN", "CAAP", "CAE", "CAR", "CARR", "CASS", "CAT", "CBAT", "CBZ",
        "CCEC", "CCTG", "CDLR", "CDNL", "CDRE", "CDTG", "CECO", "CETY", "CHRW", "CIIT",
        "CISS", "CIX", "CJMB", "CLH", "CLIR", "CLWT", "CMC", "CMCO", "CMDB", "CMI",
        "CMPR", "CMRE", "CNH", "CNI", "CNM", "CODA", "CODI", "CP", "CPA", "CPRT",
        "CR", "CRAI", "CRE", "CRESY", "CRGO", "CRS", "CSL", "CSTE", "CSW", "CSX",
        "CTAS", "CTNT", "CTOS", "CTRM", "CVLG", "CVR", "CVU", "CVV", "CW", "CWST",
        "CXT", "CXW", "CYRX", "DAC", "DAL", "DCI", "DCO", "DE", "DETX", "DEVS",
        "DFLI", "DFNS", "DFSC", "DGNX", "DLB", "DLHC", "DLX", "DNOW", "DOV", "DRS",
        "DSGR", "DSX", "DUKR", "DXPE", "DXST", "DY", "EAF", "EBF", "ECG", "ECO",
        "EDRY", "EFX", "EGG", "EH", "EHGO", "EHLD", "ELMT", "ELOG", "ELPW", "ELVA",
        "EMBJ", "EME", "EML", "EMR", "ENGS", "ENR", "ENS", "ENVX", "EOSE", "EPAC",
        "EPOW", "EQPT", "ERII", "ESAB", "ESEA", "ESLT", "ESOA", "ESP", "ETN", "ETS",
        "EVEX", "EVI", "EVLV", "EVTL", "EXPD", "EXPO", "FA", "FAST", "FBGL", "FBIN",
        "FBYD", "FCEL", "FCN", "FDX", "FELE", "FER", "FERG", "FGL", "FIP", "FIX",
        "FJET", "FLR", "FLS", "FLUX", "FLX", "FLY", "FLYX", "FOFO", "FORR", "FPS",
        "FSS", "FSTR", "FTAI", "FTEK", "FWRD", "GASS", "GATX", "GBX", "GCDT", "GD",
        "GE", "GENC", "GEO", "GEV", "GFAI", "GFF", "GFL", "GGG", "GHM", "GIC",
        "GLBS", "GLXG", "GNK", "GNRC", "GP", "GPGI", "GPUS", "GRC", "GRNQ", "GSL",
        "GTES", "GTLS", "GVA", "GVH", "GWAV", "GWH", "GWW", "GXO", "HAFN",
        "HAYW", "HCAI", "HEI", "HEI-A", "HHS", "HIHO", "HII", "HLIO", "HLMN", "HMR",
        "HON", "HOVR", "HQI", "HRI", "HSHP", "HTCO", "HTLD", "HTZ", "HUBB", "HUBG",
        "HUHU", "HURC", "HURN", "HWM", "HXHX", "HXL", "HY", "HYFM", "ICFI", "ICON",
        "IESC", "IEX", "IIIN", "ILAG", "INLF", "INTJ", "INVE", "IPDN", "IR", "ISSC",
        "ITT", "ITW", "IVDA", "J", "JBHT", "JBI", "JBLU", "JBTM", "JCI", "JCSE",
        "JELD", "JLHL", "JOB", "JOBY", "JYD", "KAI", "KBR", "KE", "KELYA", "KEX",
        "KFRC", "KFY", "KITT", "KMT", "KNX", "KODK", "KRMN", "KRNT", "KSCP", "KTOS",
        "LASE", "LBGJ", "LECO", "LGN", "LGPS", "LHX", "LICN", "LII", "LIQT", "LMB",
        "LMT", "LNKS", "LNN", "LNZA", "LOAR", "LPX", "LSH", "LSTR", "LTBR", "LTM",
        "LUNR", "LUV", "LXFR", "LZ", "MAIR", "MAN", "MAS", "MATW", "MATX", "MDA",
        "MEC", "MG", "MGN", "MGRC", "MHH", "MIDD", "MIMI", "MIR", "MLI", "MMM",
        "MMS", "MNTS", "MOB", "MOG-A", "MRCY", "MRLN", "MRTN", "MSA", "MSGY", "MSM",
        "MSW", "MTEN", "MTRX", "MTW", "MTZ", "MWA", "MWG", "MYRG", "NCEW", "NCT",
        "NDSN", "NEOV", "NIXX", "NL", "NMM", "NNBR", "NNE", "NOC", "NPK", "NPO",
        "NPWR", "NSC", "NSP", "NSSC", "NTIP", "NVRI", "NVT", "NVX", "NX", "OC",
        "ODFL", "OESX", "OFAL", "OFLX", "OLOX", "OMAB", "ONEG", "ONT", "OPTT", "OPXS",
        "ORN", "OSK", "OTIS", "OTTR", "PAC", "PAL", "PAM", "PAMT", "PANL", "PBI",
        "PCAR", "PCT", "PESI", "PEW", "PH", "PHOE", "PKE", "PKOH", "PL", "PLAG",
        "PLPC", "PLUG", "PMEC", "PNR", "POLA", "POOL", "POWL", "POWW", "PPHC", "PPIH",
        "PPSI", "PRG", "PRIM", "PRLB", "PRZO", "PSHG", "PSIG", "PSIX", "PWR", "QRHC",
        "QUAD", "QXO", "R", "RAIL", "RAIN", "RAYA", "RBA", "RBC", "RCAT", "RCMT",
        "RDW", "RELX", "REZI", "RFIL", "RGP", "RGR", "RHI", "RHLD", "RITR", "RJET",
        "RKLB", "RLGT", "ROAD", "ROCK", "ROK", "ROMA", "RR", "RRX", "RSG", "RTO",
        "RTX", "RUBI", "RVSN", "RXO", "RYAAY", "RYOJ", "RYZ", "SAIA", "SARO", "SATL",
        "SB", "SBC", "SBLK", "SCAG", "SCWO", "SDST", "SEB", "SERV", "SFHG", "SFL",
        "SFWL", "SGLY", "SGRP", "SHIM", "SHIP", "SHMD", "SIDU", "SIF", "SITE", "SKBL",
        "SKK", "SKYW", "SKYX", "SLGB", "SLND", "SMHI", "SMR", "SMX", "SNA", "SNCY",
        "SNDR", "SNT", "SOAR", "SPAI", "SPCB", "SPCE", "SPIR", "SPPL", "SPXC",
        "SRFM", "SST", "STI", "STN", "STRL", "STRR", "SUGP", "SUNB", "SVRN", "SWBI",
        "SWIM", "SWK", "SWVL", "SXI", "SYM", "TATT", "TAYD", "TBI", "TDG", "TE",
        "TEX", "TFII", "TG", "TGEN", "TH", "THH", "THR", "TIC", "TISI", "TITN",
        "TKR", "TLIH", "TNC", "TNET", "TOMZ", "TOPP", "TPC", "TPCS", "TRC", "TREX",
        "TRI", "TRN", "TRNS", "TRSG", "TT", "TTC", "TTEK", "TTI", "TUSK", "TWI",
        "TWIN", "TXT", "UAL", "UFG", "UGRO", "UHAL", "UHAL-B", "ULBI", "ULCC", "ULH",
        "ULS", "UNF", "UNP", "UP", "UPS", "URI", "USEA", "UUU", "VATE", "VCIG",
        "VLRS", "VLTO", "VMI", "VNTG", "VOYG", "VRME", "VRSK", "VRT", "VSEC", "VSTS",
        "VVX", "VWAV", "WAB", "WCC", "WCN", "WERN", "WFCF", "WFF", "WLDN", "WLFC",
        "WM", "WMS", "WNC", "WOR", "WSC", "WSO", "WTS", "WWD", "WXM", "XCH",
        "XE", "XMTR", "XOS", "XPO", "XPON", "XRX", "XTIA", "XYL", "YDDL", "YOOV",
        "YSS", "YSXT", "ZDAI", "ZIM", "ZJK", "ZONE", "ZTG", "ZTO", "ZWS",
    ],
    "Real Estate": [
        "AAT", "ABR", "ACR", "ACRE", "ADAM", "ADC", "AEI", "AGNC", "AGNT", "AHR",
        "AHRT", "AHT", "AIRE", "AIV", "AKR", "ALBT", "ALX", "AMH", "AMT", "AOMR",
        "APLE", "ARE", "ARI", "ARL", "ARR", "ASPS", "AVB", "AXR", "BDN", "BEKE",
        "BFS", "BHM", "BHR", "BNL", "BRSP", "BRT", "BRX", "BXMT", "BXP",
        "CBL", "CBRE", "CCI", "CCS", "CDP", "CHCI", "CHCT", "CHMI", "CIGI", "CIM",
        "CLDT", "CLPR", "CMCT", "CMTG", "COLD", "COMP", "CPT", "CSGP", "CSR", "CTO",
        "CTRE", "CUBE", "CURB", "CUZ", "CWK", "DEA", "DEI", "DHC", "DLR", "DOC",
        "DOUG", "DRH", "DUO", "DX", "EFC", "EGP", "ELME", "ELS", "EPR", "EPRT",
        "EQIX", "EQR", "ESBA", "ESRT", "ESS", "EUDA", "EXR", "FBRT", "FCPT", "FOR",
        "FPH", "FPI", "FR", "FRMI", "FRPH", "FRT", "FSP", "FSV", "FTHM", "FVR",
        "GBR", "GIPR", "GLPI", "GNL", "GOOD", "GPMT", "GTY", "GYRO", "HBNB", "HHH",
        "HIW", "HPP", "HR", "HST", "IHS", "IHT", "IIPR", "ILPT", "INN", "INVH",
        "IRM", "IRS", "IRT", "IVR", "IVT", "JBGS", "JFB", "JLL", "JOE", "KIM",
        "KRC", "KREF", "KRG", "KW", "LADR", "LAMR", "LAND", "LFT", "LHAI", "LINE",
        "LOAN", "LPA", "LRE", "LRHC", "LTC", "LXP", "MAA", "MAC", "MAYS", "MDRR",
        "MDV", "MFA", "MITT", "MKZR", "MLP", "MMI", "MPT", "MRNO", "MRP", "NEN",
        "NHI", "NHP", "NLOP", "NLY", "NMRK", "NNN", "NREF", "NSA", "NTST", "NXDT",
        "NXRT", "NYC", "O", "OHI", "OLP", "OMH", "ONL", "OPAD", "OPEN", "ORC",
        "OUT", "OZ", "PDM", "PEB", "PECO", "PINE", "PK", "PLD", "PMT", "PSA",
        "PSTL", "PW", "RC", "REAX", "REFI", "REG", "RENX", "REXR", "RFL", "RHP",
        "RITM", "RLJ", "RMAX", "RMR", "RPT", "RWT", "RYN", "SACH", "SAFE", "SBAC",
        "SBRA", "SDHC", "SEG", "SELF", "SEVN", "SHO", "SILA", "SITC", "SKT", "SKYH",
        "SLG", "SMA", "SPG", "SQFT", "SRG", "STAG", "STHO", "STRS", "STRW", "STWD",
        "SUI", "SUNS", "SVC", "TCI", "TRNO", "TRTX", "TWO", "UDR", "UE", "UHT",
        "UK", "UMH", "UNIT", "VICI", "VNO", "VRE", "VTMX", "VTR", "WELL", "WHLR",
        "WPC", "WSR", "WY", "XHR", "XRN",
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
        "QQQ.MX", "VOO.MX", "IAU.MX", "IBIT", "TSLA.MX", "AMZN.MX", "META.MX", "ORCL.MX", "NFLX.MX", "FIBRAPL14.MX",
        "FMTY14.MX", "DANHOS13.MX", "NVDA.MX", "WMT.MX", "NEM.MX", "LAES", "RGTI", "1211N.MX", "BBAI", "DPZ.MX",
        "XOM.MX", "PDDN.MX", "LCID", "CVX.MX", "SPOTN.MX", "NUN.MX", "BABAN.MX", "KO.MX", "MSFT.MX", "AAPL.MX",
        "MU.MX", "TSMN.MX", "PLTR.MX", "GOOGL.MX", "AEM.MX", "CRWV.MX", "BRKB.MX", "ASMLN.MX", "GS.MX", "BLK.MX", "REGN.MX",
        "JNJ.MX", "MELIN.MX", "INTC.MX", "APLD", "ZJK", "WATT", "AVGO.MX", "XYZ.MX", "AMD.MX", "FTV", "SHOPN.MX", "UBER.MX",
        "MSTR.MX", "SMCI.MX", "WDC.MX", "CRM.MX", "INUV", "HOOD.MX", "V.MX", "BAC.MX", "AXP.MX", "PM.MX", "DIS.MX",
        "BVS", "FUNO11.MX", "QTEX", "FULT", "CYPH", "LLY.MX", "JPM.MX", "CSCO.MX", "COST.MX", "MA.MX",
    ],
}

# TODOS: union de todos los sectores sin duplicados
_todos, _seen = [], set()
for _tickers in SECTORES.values():
    for _t in _tickers:
        if _t not in _seen:
            _seen.add(_t)
            _todos.append(_t)
SECTORES["TODOS"] = _todos


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


def clasificar_macd_estado(macd_line, signal_line):
    """
    Clasifica la posición del MACD respecto a su línea de señal.

    Retorna:
        'CRUCE ARRIBA'  — cruzó arriba hoy  (ayer debajo, hoy encima)
        'CRUCE ABAJO'  — cruzó abajo hoy   (ayer encima, hoy debajo)
        'SOBRE'     — MACD sobre señal  (sin cruce hoy)
        'BAJO'      — MACD bajo señal   (sin cruce hoy)
    """
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

        # ── Estado detallado del MACD ──────────────────────────────────
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
            "MACD Estado": macd_estado,          # ← reemplaza Market Cap
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

    # Fila 1: Ticker · Señal · MACD Estado · Precio mín/máx · Reset
    c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 2, 1.5, 1.5, 1])
    with c1:
        ticker_busq = st.text_input("Ticker", placeholder="Buscar… ej. NVDA",
                                    label_visibility="collapsed", key="f_ticker")
    with c2:
        señal_opt = st.selectbox("Señal", ["Todas", "COMPRAR", "POSIBLE VENTA", "NEUTRAL"],
                                 label_visibility="collapsed", key="f_señal")
    with c3:
        macd_estado_opt = st.selectbox(
            "MACD Estado",
            ["Todos", "CRUCE ARRIBA", "CRUCE ABAJO", "SOBRE", "BAJO"],
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

    # Fila 2: rangos RSI / SMAs
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

    # Fila 3: checkboxes
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

    def macd_estado_html(estado):
        mapa = {
            "CRUCE ARRIBA": "macd-cross-up",
            "CRUCE ABAJO": "macd-cross-down",
            "SOBRE":    "macd-above",
            "BAJO":     "macd-below",
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
            <td>{row['MACD']:.4f}</td>
            <td>{row['Signal']:.4f}</td>
            <td>{macd_estado_html(row['MACD Estado'])}</td>
            <td>{vol_html(row['Vol Hoy'], row['Vol Avg20'])}</td>
            <td>{formatear_volumen(row['Vol Avg20'])}</td>
            <td>{señal_html(row['Señal'])}</td>
        </tr>"""

    return f"""
    <div style="overflow-x:auto; margin-top:1rem;">
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


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════

st.markdown('<div class="main-header">SWING SCREENER</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="sub-header">sector · {sector_seleccionado.upper()} &nbsp;|&nbsp; '
    f'{len(SECTORES[sector_seleccionado])} tickers</div>',
    unsafe_allow_html=True
)

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

    tickers   = SECTORES[sector_seleccionado]
    df_result = correr_analisis(tickers, config, progress_bar, status_text)

    progress_bar.empty()
    status_text.empty()

    if df_result.empty:
        st.error("❌ No se generaron resultados. Verifica la conexión o los tickers.")
    else:
        st.session_state["df_result"]     = df_result
        st.session_state["sector_result"] = sector_seleccionado

if "df_result" in st.session_state and not st.session_state["df_result"].empty:
    df_result = st.session_state["df_result"]

    # ── Métricas superiores ─────────────────────────────────────────────
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

    # ── Segunda fila de métricas: estado MACD ───────────────────────────
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

    # ── Filtros ─────────────────────────────────────────────────────────
    filtros     = render_filtros(df_result)
    df_filtrado = aplicar_filtros(df_result, filtros)

    st.markdown(
        f'<div class="result-count">Mostrando <b style="color:#4fc3f7">{len(df_filtrado)}</b> '
        f'de <b>{len(df_result)}</b> resultados</div>',
        unsafe_allow_html=True
    )

    if df_filtrado.empty:
        st.warning("⚠️ Ningún ticker cumple los filtros actuales.")
    else:
        st.markdown(render_tabla(df_filtrado), unsafe_allow_html=True)

    # ── Descarga CSV ────────────────────────────────────────────────────
    csv = df_filtrado.drop(columns=["Compra", "Venta"], errors="ignore").to_csv(index=False)
    st.download_button(
        label="⬇️  Descargar CSV (filtrado)",
        data=csv,
        file_name=f"screener_{sector_seleccionado.replace(' ', '_')}.csv",
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
