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
        "AAL", "ALLT", "AMX", "ANGI", "ANET", "APCX", "APP", "ASEA", "ASST", "ATAI",
        "ATNI", "ATO", "RO", "AXS", "BAND", "BCE", "BCOR", "BDL", "BFRG", "BIDU",
        "BILI", "BLZE", "BMBL", "BNED", "BNGO", "BPTH", "BTE", "BTM", "BTT", "BUR",
        "BWMX", "BZ", "BZUN", "CABA", "CABO", "CAMT", "CAN", "CANG", "CARG", "CARR",
        "CARS", "CAT", "CBAT", "CCO", "CCOI", "CD", "CDLX", "CDW", "CELH", "CENT",
        "CETX", "CHCI", "CHDN", "CHGG", "CHKP", "CHTR", "CHWY", "CIG", "CINT", "CIX",
        "CLIR", "CLNE", "CLPS", "CLRO", "CLSK", "CLVT", "CMCSA", "CMG", "CMRE", "CMS",
        "CMTL", "CNEY", "CNK", "CNMD", "CNO", "CNSP", "CNXC", "COCO", "COCP", "COGT",
        "COHN", "COHR", "COIN", "COMS", "COMT", "CONY", "CORZ", "COSM", "COST", "CPB",
        "CQP", "CRDO", "CREG", "CREX", "CRIS", "CRKN", "CRMT", "CRNC", "CRNT", "CRNX",
        "CRSP", "CRSR", "CRTD", "CRTO", "CRWD", "CSCO", "CSGP", "CSIQ", "CSX", "CTAS",
        "CTBI", "CTLP", "CTO", "CTRM", "CTRN", "CTS", "CTSH", "CTSO", "CTVA", "CUK",
        "CURV", "CVCO", "CVGI", "CVGW", "CVI", "CVLG", "CVLT", "CVNA", "CVR", "CVS",
        "CVX", "CW", "CWAN", "CWBC", "CWCO", "CWEN", "CWH", "CWK", "CWST", "CWT",
        "CX", "CXAI", "CXDO", "CXM", "CXT", "CYAN", "CYCN", "CYD", "CYN", "CYRX",
        "CZNC", "CZR", "CZWI", "D", "DAIO", "DAKT", "DAL", "DAN", "DAR", "DARE",
        "DASH", "DAVA", "DAVE", "DB", "DBD", "DBGI", "DBI", "DBVT", "DBX", "DC",
        "DCBO", "DCI", "DCO", "DCOM", "DCTH", "DD", "DDD", "DDI", "DDOG", "DDS",
        "DE", "DEA", "DECK", "DEI", "DELL", "DEO", "DERM", "DFH", "DFLI", "DGX",
        "DH", "DHC", "DHI", "DHIL", "DHR", "DHT", "DHX", "DIBS", "DIOD", "DIS",
        "DIT", "DJCO", "DJT", "DK", "DKNG", "DKS", "DLB", "DLHC", "DLNG", "DLO",
        "DLPN", "DLR", "DLTH", "DLTR", "DLX", "DMA", "DMAN", "DMAC", "DMAX", "DMB",
        "DMLP", "DMO", "DMRC", "DNA", "DNLI", "DNN", "DNOW", "DNUT", "DOC", "DOCN",
        "DOCS", "DOCU", "DOGZ", "DOL", "DOMO", "DON", "DOO", "DORM", "DOV", "DOW",
        "DOX", "DOYU", "DPRO", "DRCT", "DRD", "DRH", "DRI", "DRMA", "DRS", "DRTS",
        "DRUG", "DRV", "DRVN", "DSGN", "DSGR", "DSGX", "DSI", "DSL", "DSM", "DSP",
        "DSS", "DSU", "DSWL", "DSX", "DT", "DTE", "DTEC", "DTF", "DTG", "DTIL",
        "DTM", "DTN", "DTSS", "DTST", "EDN", "EGHT", "ELS", "EMR", "ERIE", "ETSY",
        "EVTC", "FB", "FDX", "FENG", "FINV", "FISV", "FLWS", "FOX", "FOXA", "FTNT",
        "FUBO", "GCO", "GDDY", "GDEN", "GEO", "GHM", "GNE", "GNLN", "GOOG", "GOOGL",
        "GPRO", "GRPN", "GSAT", "GSL", "GSM", "GTN", "HAYW", "HDSN", "HFBL", "HPQ",
        "HRB", "HRI", "HSY", "HUBS", "HUYA", "IAC", "IAG", "IBEX", "IBM", "ICE",
        "IDCC", "IDT", "IHRT", "ILMN", "IMAX", "INCY", "INDP", "INFY", "INOD", "INSE",
        "INTC", "INUV", "IQ", "IRDM", "IRET", "IRIX", "IRTC", "ISCB", "ITRI", "ITW",
        "IX", "JAKK", "JAN", "JAZZ", "JBL", "JBLU", "JBSS", "JELD", "JILL", "JJSF",
        "JKHY", "JKS", "JMIA", "JMM", "JOE", "JOUT", "JPM", "JRSH", "JSML", "JTAI",
        "JYNT", "KAI", "KALA", "KALV", "KBH", "KBNT", "KBR", "KC", "KD", "KDP",
        "KE", "KELYA", "KEN", "KEP", "KEX", "KEY", "KEYS", "KF", "KFFB", "KFRC",
        "KFS", "KFY", "KGC", "KHC", "KIM", "KINS", "KIO", "KKR", "KLAC", "KLDO",
        "KLIC", "KLTR", "KLXE", "KMB", "KMDA", "KMI", "KMPR", "KMT", "KMX", "KN",
        "KNDI", "KNOP", "KNSA", "KNSL", "KNTK", "KNX", "KO", "KOD", "KODK", "KOP",
        "KOPN", "KOS", "KOSS", "KPTI", "KR", "KRC", "KRE", "KRMD", "KRNY", "KRO",
        "KRP", "KRUS", "KRYS", "KSPI", "KSS", "KT", "KTB", "KTCC", "KTF", "KTH",
        "KTN", "KTOS", "KURA", "KVHI", "KVLE", "KW", "KWR", "KXIN", "KYMR", "KYN",
        "LBRDA", "LBRDK", "LILA", "LILAK", "LIN", "LION", "LIQT", "LIVE", "LMFA",
        "LMNR", "LMNX", "LMND", "LMT", "LNC", "LND", "LNG", "LNGR", "LNN", "LNTH",
        "LNT", "LNW", "LOAN", "LOB", "LOCO", "LODE", "LOGC", "LOGI", "LOMA", "LOOP",
        "LOPE", "LOT", "LOVE", "LOW", "LPG", "LPL", "LPLA", "LPSN", "LPX", "LQDA",
        "LQDT", "LRCX", "LRGE", "LRMR", "LRN", "LSAK", "LSAT", "LSBK", "LSPD", "LST",
        "LTC", "LTH", "LU", "LUCK", "LULU", "LUMN", "LUNR", "LUV", "LVLU", "LVO",
        "LVS", "LW", "LWAY", "LX", "LXEH", "LXP", "LXRX", "LYB", "LYFT", "LYG",
        "LYRA", "LYV", "LZ", "LZB", "M", "MA", "MAC", "MADE", "MAGS", "MAIN",
        "MAN", "MANH", "MANU", "MAPS", "MAR", "MARA", "MARK", "MARPS", "MAS",
        "MASI", "MAT", "MATV", "MATX", "MAX", "MAXN", "MBI", "MBIN", "MBIO", "MBOT",
        "MBRX", "MBS", "MBUU", "MBWM", "MC", "MCB", "MCBS", "MCD", "MCFT", "MCH",
        "MCHI", "MCHX", "MCI", "MCK", "MCN", "MCO", "MCR", "MCRB", "MCS", "MCW",
        "MCY", "MDB", "MDGL", "MDIA", "MDLZ", "MDRX", "MDT", "MDU", "MDV", "MDXG",
        "MEC", "MED", "MEDP", "MEG", "MEGI", "MEI", "MEIP", "MELI", "MEOH", "MERC",
        "MESO", "MET", "METC", "MFA", "MFC", "MFG", "MFI", "MFM", "MG", "MGA",
        "MGC", "MGEE", "MGF", "MGM", "MGMT", "MGPI", "MGR", "MGRC", "MGTX", "MGY",
        "MHD", "MHF", "MHK", "MHLA", "MHNC", "MHO", "MHTX", "MHY", "MI", "MIDD",
        "MIG", "MILN", "MIND", "MINN", "MIR", "MIRA", "MIST", "MITK", "MITT", "MJ",
        "MJNE", "MKC", "MKL", "MKSI", "MKTX", "MLAC", "MLCO", "MLI", "MLM", "MLN",
        "MLP", "MLPA", "MLPB", "MLPD", "MLPH", "MLPR", "MLPX", "MLR", "MMA", "MMD",
        "MMI", "MMIT", "MMK", "MMLP", "MMM", "MMS", "MMSI", "MMT", "MMTM", "MMU",
        "MNA", "MNDO", "MNDY", "MNKD", "MNPR", "MNR", "MNRO", "MNSB", "MNSO", "MNST",
        "MNTR", "MO", "MOB", "MOD", "MOH", "MOLN", "MOMO", "MOO", "MORN", "MOS",
        "MOTS", "MOV", "MP", "MPA", "MPAA", "MPB", "MPC", "MPG", "MPO", "MPV",
        "MPWR", "MPX", "MQ", "MRAM", "MRBK", "MRCC", "MRCY", "MREO", "MRK", "MRKR",
        "MRLN", "MRM", "MRMD", "MRNJ", "MRTN", "MRVI", "MRVL", "MS", "MSA", "MSB",
        "MSBI", "MSC", "MSCI", "MSD", "MSDL", "MSFT", "MSGE", "MSGM", "MSGS", "MSI",
        "MSM", "MSN", "MSPR", "MSSS", "MST", "MSTR", "MSW", "MT", "MTA", "MTAL",
        "MTB", "MTCH", "MTD", "MTDR", "MTEX", "MTG", "MTH", "MTLS", "MTN", "MTNB",
        "MTR", "MTRN", "MTRX", "MTS", "MTSI", "MTUM", "MTW", "MTX", "MTZ", "MU",
        "MUA", "MUB", "MUC", "MUD", "MUFG", "MUJ", "MUNI", "MUR", "MUSA", "MUX",
        "MVBF", "MVIS", "MVLA", "MVO", "MVV", "MX", "MXC", "MXCT", "MXE", "MXF",
        "MXL", "MYE", "MYI", "MYN", "MYND", "MYO", "MYPS", "MYRG", "MYY", "NAVI",
        "NCLH", "NFLX", "NIO", "NWSA", "NWS", "NXST", "O", "OEF", "OMC", "ON",
        "ORCL", "OTIS", "PANW", "PBA", "PBI", "PBR", "PBT", "PCF", "PCG", "PDD",
        "PEB", "PEO", "PEP", "PFE", "PG", "PH", "PHM", "PIM", "PLD", "PLTR",
        "PM", "PNC", "PNR", "PNW", "PPL", "PR", "PRU", "PSA", "PSN", "PSX",
        "PTC", "PUI", "PYPL", "QCOM", "R", "RBA", "RCI", "RDN", "RHI", "RJF",
        "RL", "RMD", "RNG", "ROG", "RSI", "RSG", "RTX", "RY", "SAN", "SAP",
        "SBC", "SBUX", "SCHW", "SCI", "SEE", "SFL", "SHW", "SLB", "SLGN", "SMG",
        "SMP", "SNA", "SNAP", "SNOW", "SONY", "SPG", "SPGI", "SPY", "SRI", "SRL",
        "SSD", "STM", "STX", "STZ", "SUN", "SUZ", "SYK", "SYY", "T", "TAP",
        "TBB", "TD", "TDG", "TEAM", "TEL", "TEN", "TEX", "TFC", "TFX", "TG",
        "TGT", "THC", "THG", "THO", "THR", "TIMB", "TJX", "TKR", "TLK", "TM",
        "TMO", "TMUS", "TNC", "TNET", "TOL", "TPC", "TPH", "TRGP", "TRMB", "TROW",
        "TRP", "TRU", "TRV", "TS", "TSLA", "TSM", "TSN", "TTC", "TTE", "TTWO",
        "TW", "TXN", "TY", "TYL", "UA", "UAA", "UBER", "UBS", "UDR", "UGI",
        "UHAL", "UHS", "UI", "UL", "UMC", "UNF", "UNH", "UNP", "UPS", "URBN",
        "URI", "USA", "USB", "USFD", "V", "VFC", "VLO", "VNDA", "VNET", "VNM",
        "VNQ", "VONG", "VOO", "VRP", "VRSK", "VRSN", "VRTX", "VTR", "VTV", "VUG",
        "VVV", "VWO", "VXUS", "VYM", "WAB", "WAT", "WBD", "WBS", "WCC", "WDC",
        "WEC", "WELL", "WFC", "WGO", "WH", "WHD", "WM", "WMB", "WMT", "WNC",
        "WST", "WTW", "WU", "WWD", "WY", "WYNN", "XLY", "XOM", "XPO", "XRAY",
        "XYL", "YUM", "ZBH", "ZBRA", "ZION", "ZTS",
    ],

    "Technology": [
        "AAPL", "ACN", "ADBE", "ADI", "ADSK", "AKAM", "AMAT", "AMD", "ANET", "APP",
        "ASML", "AVGO", "AZTA", "BAND", "BILI", "BITS", "BL", "BLZE", "BMBL", "BSY",
        "CAC", "CACI", "CANG", "CARR", "CARS", "CCC", "CDNS", "CDW", "CEVA", "CHKP",
        "CIEN", "CINT", "CLST", "CLVT", "CMBM", "CMS", "COMS", "COMT", "CORZ", "COSM",
        "CPNG", "CRDO", "CREG", "CREX", "CRNC", "CRNT", "CRNX", "CRSR", "CRWD", "CSCO",
        "CSIQ", "CTAS", "CTSH", "CTVA", "CXAI", "CXM", "CYAN", "CYCN", "DAIO", "DAKT",
        "DASH", "DAVA", "DAVE", "DBX", "DCBO", "DDOG", "DELL", "DFLI", "DGX", "DH",
        "DIBS", "DIOD", "DKNG", "DLB", "DLO", "DMRC", "DNLI", "DOCN", "DOCU", "DOGZ",
        "DOMO", "DOX", "DOYU", "DPRO", "DRCT", "DRS", "DRTS", "DSGN", "DSGX", "DT",
        "DTEC", "DTIL", "DTSS", "DTST", "DXC", "EBAY", "EDGE", "EDIT", "EGHT", "ENPH",
        "EPAM", "ERIC", "ERIE", "ETSY", "EVTC", "EXTR", "FICO", "FIS", "FISV", "FLWS",
        "FLYW", "FORM", "FORR", "FORTY", "FOUR", "FRSH", "FSLY", "FTNT", "FUTU", "G",
        "GDDY", "GHM", "GLOB", "GLW", "GNSS", "GOOG", "GOOGL", "GPRO", "GRPN", "GSAT",
        "GSL", "GSM", "GWRE", "HAYW", "HDSN", "HIMX", "HPQ", "HRI", "HUBS", "HURC",
        "IBM", "IDCC", "INFY", "INOD", "INSE", "INTC", "INTU", "INUV", "IONQ", "IQ",
        "IRDM", "IRTC", "IT", "ITRI", "IVV", "IX", "JAN", "JAZZ", "JBL", "JKHY",
        "JKS", "KAI", "KALV", "KBR", "KC", "KD", "KEYS", "KLAC", "KLIC", "KLTR",
        "KNDI", "KNX", "KOPN", "KPTI", "KRNT", "KRYS", "KT", "KTCC", "KTOS", "KURA",
        "KVHI", "KYMR", "LBRDK", "LCID", "LEN", "LEON", "LI", "LION", "LIQT", "LIVE",
        "LMNR", "LMNX", "LMND", "LMT", "LNW", "LOGC", "LOGI", "LOOP", "LOPE", "LPL",
        "LPLA", "LPSN", "LQDT", "LRCX", "LRN", "LSAT", "LSPD", "LST", "LULU", "LUMN",
        "LUNR", "LUV", "LVLU", "LVS", "LWAY", "LX", "LXEH", "LXP", "LXRX", "LYFT",
        "LZ", "MA", "MANH", "MAPS", "MARA", "MARK", "MASI", "MAT", "MATX", "MAXN",
        "MBOT", "MBUU", "MCHX", "MCK", "MCN", "MCO", "MCRB", "MDB", "MDIA", "MDRX",
        "MDT", "MDXG", "MEDP", "MEG", "MEI", "MELI", "MEOH", "MESO", "METC", "MGA",
        "MGC", "MGMT", "MGRC", "MGTX", "MGY", "MHK", "MIDD", "MIG", "MIND", "MINN",
        "MIRA", "MIST", "MITK", "MITT", "MKSI", "MKTX", "MLCO", "MLI", "MMI", "MMS",
        "MMSI", "MMTM", "MNDO", "MNDY", "MNKD", "MNPR", "MNRO", "MNST", "MNTR", "MOB",
        "MOD", "MOH", "MOLN", "MOMO", "MORN", "MOTS", "MOV", "MP", "MPWR", "MQ",
        "MRAM", "MRCY", "MREO", "MRK", "MRKR", "MRMD", "MRNA", "MRTN", "MRVI", "MRVL",
        "MSFT", "MSGE", "MSGM", "MSI", "MSM", "MSN", "MSTR", "MTCH", "MTD", "MTEX",
        "MTG", "MTH", "MTLS", "MTNB", "MTRN", "MTRX", "MTS", "MTSI", "MTUM", "MTW",
        "MTX", "MU", "MUFG", "MUR", "MUSA", "MUX", "MVIS", "MVLA", "MXCT", "MXL",
        "MYE", "MYND", "MYRG", "NAVI", "NCA", "NCI", "NFLX", "NICE", "NIO", "NNDM",
        "NOW", "NSIT", "NTAP", "NTCT", "NTES", "NTNX", "NTRS", "NU", "NUV", "NVDA",
        "NVMI", "NVR", "NWSA", "NXPI", "NXST", "O", "OKTA", "OMC", "OMCL", "ON",
        "ONTF", "OPAD", "OPEN", "OPK", "OPRA", "OPRX", "ORCL", "OSIS", "OTIS", "OTLK",
        "OUST", "OVV", "OWLT", "OXM", "PAGS", "PANW", "PATK", "PATH", "PAYC", "PAYX",
        "PAYS", "PBI", "PBR", "PCG", "PCTY", "PD", "PDD", "PDFS", "PEGA", "PEP",
        "PFE", "PG", "PH", "PHM", "PINS", "PLD", "PLTK", "PLTR", "PLUG", "PLUS",
        "PNC", "PNR", "POWI", "PPL", "PRGS", "PRU", "PSA", "PSN", "PSX", "PTC",
        "PTEN", "PUBM", "PUI", "PYPL", "QCOM", "QLYS", "QRVO", "QS", "QTRX", "R",
        "RBA", "RBLX", "RCI", "RDN", "RHI", "RIOT", "RITM", "RJF", "RL", "RMD",
        "RMBS", "RNG", "ROK", "ROKU", "ROP", "RSI", "RSG", "RTX", "RUN", "RUSHA",
        "RVMD", "RXT", "RY", "RYAAY", "SAN", "SAP", "SATS", "SBC", "SBUX", "SCHW",
        "SCI", "SE", "SEE", "SFL", "SHC", "SHW", "SI", "SIG", "SITM", "SITE",
        "SKLZ", "SLB", "SLGN", "SMCI", "SMG", "SMP", "SNA", "SNAP", "SNDR", "SNOW",
        "SNPS", "SONY", "SOUN", "SPG", "SPGI", "SPOT", "SPRO", "SPWR", "SPY", "SRI",
        "SRL", "SSNC", "STG", "STM", "STNE", "STRT", "STX", "STZ", "SUZ", "SWKS",
        "SXC", "SYK", "SYNA", "SYY", "T", "TAL", "TAP", "TBB", "TD", "TDG",
        "TEAM", "TEL", "TEN", "TER", "TEX", "TFC", "TFX", "TG", "TGT", "THC",
        "THG", "THO", "THR", "TIGO", "TIMB", "TIPT", "TJX", "TKR", "TLK", "TLN",
        "TLRY", "TM", "TMDX", "TMO", "TMUS", "TNC", "TNET", "TOST", "TPC", "TPH",
        "TREE", "TRGP", "TRMB", "TROW", "TRP", "TRUP", "TSLA", "TSM", "TSN", "TTC",
        "TTE", "TTWO", "TW", "TWLO", "TXN", "TY", "TYL", "UA", "UAA", "UBER",
        "UBS", "UDR", "UGI", "UHAL", "UHS", "UI", "UIS", "UL", "ULTA", "UMC",
        "UNF", "UNH", "UNP", "UNIT", "UPST", "UPS", "URBN", "URI", "USA", "USB",
        "USFD", "V", "VFC", "VIAV", "VLO", "VMC", "VMD", "VNDA", "VNET", "VNM",
        "VNQ", "VOD", "VONG", "VOO", "VRP", "VRSK", "VRSN", "VRT", "VRTX", "VSH",
        "VTI", "VTR", "VTV", "VUG", "VVV", "VWO", "VXUS", "VYM", "WAB", "WAT",
        "WBD", "WBS", "WCC", "WDC", "WEC", "WELL", "WFC", "WGO", "WH", "WHD",
        "WIT", "WIX", "WK", "WLDN", "WM", "WMB", "WMT", "WNC", "WOLF", "WPM",
        "WST", "WTW", "WU", "WWD", "WY", "WYNN", "XBI", "XEL", "XLE", "XLF",
        "XLI", "XLK", "XLP", "XLU", "XLV", "XLY", "XOM", "XPO", "XRAY", "XYL",
        "YANG", "YELP", "YETI", "YINN", "YOU", "YPF", "YUM", "YUMC", "Z", "ZBH",
        "ZBRA", "ZD", "ZGN", "ZION", "ZM", "ZS", "ZTO", "ZTS",
    ],

    # ── PLACEHOLDER — reemplaza con tus listas de Finviz ─────────────────
    "Basic Materials": [
        "AA", "ALB", "APD", "ARNC", "ASH", "AVY", "AXTA", "BCC", "CF", "CLF",
        "CMC", "CRS", "DOW", "EMN", "FCX", "FMC", "GRA", "HUN", "IFF", "IP",
        "KGC", "LIN", "LYB", "MOS", "MP", "NEM", "NUE", "OLN", "PKG", "PPG",
        "RS", "RIO", "RPM", "SLVM", "SMG", "SQM", "STLD", "SWK", "TREX", "VMC",
        "WRK", "X", "XOM",
    ],

    "Consumer Cyclical": [
        "ABNB", "AMZN", "AN", "AZO", "BBWI", "BBY", "BKNG", "BWA", "CCL", "CMG",
        "COF", "CROX", "DG", "DLTR", "DPZ", "DRI", "EBAY", "ETSY", "EXPE", "F",
        "GM", "GRMN", "HD", "HLT", "HOG", "HRB", "HYMC", "KMX", "LEN", "LOW",
        "LVS", "MAR", "MCD", "MGM", "NKE", "NCLH", "NVR", "ORLY", "PHM", "PTON",
        "PVH", "RL", "RCL", "RIVN", "SBUX", "SHW", "SNAP", "TGT", "TJX", "TOL",
        "TSLA", "UAA", "UBER", "ULTA", "VFC", "WYNN", "YUM",
    ],

    "Consumer Defensive": [
        "ADM", "BF.B", "CAG", "CHD", "CL", "CLX", "COST", "CPB", "CVS", "EL",
        "GIS", "HRL", "HSY", "K", "KHC", "KMB", "KO", "KR", "MDLZ", "MKC",
        "MO", "MNST", "PEP", "PG", "PM", "SJM", "STZ", "SYY", "TAP", "TGT",
        "TSN", "WBA", "WMT",
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
        "AEE", "AEP", "AES", "AGR", "ATO", "AWK", "CMS", "CNP", "D", "DTE",
        "DUK", "ED", "EIX", "ES", "ETR", "EVRG", "EXC", "FE", "LNT", "NEE",
        "NI", "NRG", "OGE", "PCG", "PEG", "PNM", "PNW", "PPL", "SO", "SRE",
        "WEC", "XEL",
    ],

    "BMV": [
        "AC.MX", "AERO.MX", "ACTINVRB.MX", "AGUA.MX", "AGUILASCPO.MX",
        "ALPEKA.MX", "ALSEA.MX", "AMXB.MX", "ARA.MX", "ASURB.MX",
        "AUTLANB.MX", "AXTELCPO.MX", "BBAJIOO.MX", "BIMBOA.MX", "BOLSAA.MX",
        "CEMEXCPO.MX", "CHDRAUIB.MX", "CIDMEGA.MX", "CIEB.MX", "CMOCTEZ.MX", "CADUA.MX",
        "CMRB.MX", "CUERVO.MX", "CULTIBAB.MX", "CYDSASAA.MX", "DANHOS13.MX",
        "DINEB.MX", "FEMSAUB.MX", "FINAMEXO.MX", "FRAGUAB.MX", "GAPB.MX",
        "GCARSOA1.MX", "GCC.MX", "GENTERA.MX", "GFINBURO.MX", "GFNORTEO.MX",
        "GIGANTE.MX", "GISSAA.MX", "GMEXICOB.MX", "GNP.MX", "GPH1.MX",
        "GRUMAB.MX", "HERDEZ.MX", "HOTEL.MX", "ICHB.MX",
        "INVEXA.MX", "KIMBERA.MX", "KOFUBL.MX", "KUOB.MX", "LABB.MX",
        "LACOMERUBC.MX", "LAMOSA.MX", "LASITE.MX", "LIVEPOLC-1.MX", "MEDICAB.MX",
        "MEGACPO.MX", "MFRISCOA-1.MX", "NEMAKA.MX", "OMAB.MX", "ORBIA.MX",
        "PE&OLES.MX", "PINFRA.MX", "POSADASA.MX", "Q.MX", "RA.MX",
        "RLHA.MX", "ROBOTIKFF.MX", "SIMECB.MX", "SORIANAB.MX", "TLEVISACPO.MX", "TRAXIONA.MX",
        "VESTA.MX", "VINTE.MX", "VISTAA.MX", "VITROA.MX", "VOLARA.MX", "WALMEX.MX",
        "FIBRAPL14.MX", "FIHO12.MX", "FINN13.MX", "FMTY14.MX",
        "FIBRAMQ12.MX", "FZUAD17.MX", "FUNO11.MX", "TERRA13.MX",
        "FIBRAHD15.MX", "FIBRAUP18.MX", "FPLUS16.MX", "FEBE19.MX",
        "FVIA16.MX", "EDM17.MX", "DANHOS13.MX",
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
        "CRM", "INUV", "HOOD", "V", "BAC", "AXP", "PM", "DIS",
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
