from datetime import date, timedelta
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Mi Portafolio", page_icon="💼", layout="wide")
st.markdown("""<style>
.stApp{background:#0a0e1a;color:#e0e6f0}[data-testid=stSidebar]{background:#0d1220}
[data-testid=stMetric]{background:#0d1421;border:1px solid #1e3a5f;border-radius:6px;padding:.6rem .9rem}
</style>""", unsafe_allow_html=True)

DATA = Path(__file__).resolve().parent.parent / "datos_portafolio"
DATA.mkdir(exist_ok=True)
F_OPS, F_CAP, F_MAP = DATA / "operaciones.csv", DATA / "capital.csv", DATA / "mapeo_tickers.csv"
COL_OPS = ["FECHA", "HORA", "SIMBOLO", "TIPO", "MERCADO", "CANTIDAD", "PRECIO", "COMISION", "CUENTA"]
COL_CAP = ["FECHA", "TIPO", "CLASIFICACION", "IMPORTE", "BANCO", "CUENTA"]
COL_MAP = ["SIMBOLO", "YAHOO", "PRECIO_MANUAL"]
BG, PANEL, BORDER, TXT = "#0a0e1a", "#0d1421", "#1e3a5f", "#c8d6e5"


# ───────────────────────── datos ─────────────────────────
def cargar(path, cols):
    df = pd.read_csv(path, dtype=str).reindex(columns=cols) if path.exists() else pd.DataFrame(columns=cols)
    for c in ("CANTIDAD", "PRECIO", "COMISION", "IMPORTE", "PRECIO_MANUAL"):
        if c in df:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    if "FECHA" in df:
        df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce").dt.date
    return df


def guardar(df, path):
    df.to_csv(path, index=False)


def num(s):
    return pd.to_numeric(s.astype(str).str.replace(r"[$,\s]", "", regex=True), errors="coerce")


def fecha(s):
    return pd.to_datetime(s, dayfirst=True, errors="coerce").dt.date


def importar(df):
    """Reconoce las hojas exportadas de Google Sheets (o los CSV de la app web)."""
    d = df.copy()
    d.columns = [c.strip().upper().replace("Ó", "O").replace("Í", "I") for c in d.columns]
    pick = lambda n: next((c for c in d.columns if c.startswith(n)), None)
    col = lambda n, alt="": d[pick(n)].astype(str).str.strip() if pick(n) else alt
    if pick("SIMBOLO") and pick("CANTID"):
        out = pd.DataFrame({
            "FECHA": fecha(d[pick("FECHA")]), "HORA": col("HORA"), "SIMBOLO": col("SIMBOLO").str.upper(),
            "TIPO": col("TIPO").str.upper(), "MERCADO": col("MERCADO", "BMV"),
            "CANTIDAD": num(d[pick("CANTID")]), "PRECIO": num(d[pick("PRECIO")]),
            "COMISION": num(d[pick("COMISION")]) if pick("COMISION") else 0.0, "CUENTA": col("CUENTA"),
        })
        return "ops", out.dropna(subset=["FECHA", "CANTIDAD", "PRECIO"])
    if pick("CLASIF"):
        out = pd.DataFrame({
            "FECHA": fecha(d[pick("FECHA")]), "TIPO": col("TIPO").str.upper(),
            "CLASIFICACION": col("CLASIF"), "IMPORTE": num(d[pick("IMPORTE")]),
            "BANCO": col("BANCO"), "CUENTA": col("CUENTA"),
        })
        return "cap", out.dropna(subset=["FECHA", "IMPORTE"])
    return None, None


# ───────────────────────── cálculo ─────────────────────────
def limpiar_ops(ops):
    o = ops.dropna(subset=["FECHA", "SIMBOLO", "CANTIDAD", "PRECIO"]).copy()
    o["COMISION"] = o["COMISION"].fillna(0)
    o["HORA"] = o["HORA"].fillna("").astype(str)
    return o.sort_values(["FECHA", "HORA"], kind="stable")


def posiciones(ops):
    """Costo promedio; las ventas realizan ganancia contra el costo promedio."""
    pos = {}
    for r in limpiar_ops(ops).itertuples():
        p = pos.setdefault(r.SIMBOLO, {"q": 0.0, "c": 0.0, "r": 0.0})
        if r.TIPO == "COMPRA":
            p["q"] += r.CANTIDAD
            p["c"] += r.CANTIDAD * r.PRECIO + r.COMISION
        else:
            a = p["c"] / p["q"] if p["q"] else 0.0
            p["r"] += r.CANTIDAD * r.PRECIO - r.COMISION - a * r.CANTIDAD
            p["c"] -= a * r.CANTIDAD
            p["q"] -= r.CANTIDAD
    return pos


def yahoo_de(simbolos, mapeo):
    m = mapeo.dropna(subset=["YAHOO"]).set_index("SIMBOLO")["YAHOO"].to_dict()
    return {s: (str(m.get(s, "")).strip() or f"{s}.MX") for s in simbolos}


@st.cache_data(ttl=900, show_spinner="Descargando precios de Yahoo Finance…")
def bajar(tickers, inicio):
    df = yf.download(list(tickers), start=inicio, auto_adjust=True, progress=False, threads=True)["Close"]
    if isinstance(df, pd.Series):
        df = df.to_frame(tickers[0])
    return df.ffill()


def rendimiento(ops, precios, ymap, en_mxn):
    """Rendimiento ponderado por tiempo: los aportes y retiros no cuentan como ganancia."""
    idx = precios.index
    o = limpiar_ops(ops)
    o["i"] = idx.searchsorted(pd.to_datetime(o["FECHA"]))
    o = o[o["i"] < len(idx)]
    sg = np.where(o["TIPO"] == "COMPRA", 1, -1)
    o["dq"], o["flujo"] = sg * o["CANTIDAD"], sg * o["CANTIDAD"] * o["PRECIO"] + o["COMISION"]
    valor, flujos, faltan = np.zeros(len(idx)), np.zeros(len(idx)), []
    for s, g in o.groupby("SIMBOLO"):
        y = ymap[s]
        if y not in precios or precios[y].dropna().empty:
            faltan.append(s)
            continue
        qty = g.groupby("i")["dq"].sum().reindex(range(len(idx)), fill_value=0).cumsum().values
        valor += qty * np.nan_to_num(precios[y].values)
        flujos += g.groupby("i")["flujo"].sum().reindex(range(len(idx)), fill_value=0).values
    ret = np.zeros(len(idx))
    for t in range(1, len(idx)):
        ret[t] = (valor[t] - flujos[t]) / valor[t - 1] - 1 if valor[t - 1] > 0 else 0.0
    sp = precios["^GSPC"] * (precios["USDMXN=X"] if en_mxn else 1)
    df = pd.DataFrame({"Portafolio": (1 + ret).cumprod(), "S&P 500": sp.values}, index=idx)
    df = df[valor > 0].dropna()
    return df, faltan


def grafica(sub):
    fig, ax = plt.subplots(figsize=(10, 4.2), facecolor=BG)
    ax.set_facecolor(PANEL)
    for c, color in (("Portafolio", "#2f7df6"), ("S&P 500", "#f0b35a")):
        ax.plot(sub.index, sub[c] * 100, color=color, lw=1.8, label=c)
        ax.annotate(f"{sub[c].iloc[-1] * 100:+.2f}%", (sub.index[-1], sub[c].iloc[-1] * 100), xytext=(6, 0),
                    textcoords="offset points", color=color, fontweight="bold", va="center", annotation_clip=False)
    ax.axhline(0, color=BORDER, ls="--", lw=0.8)
    ax.tick_params(colors=TXT, labelsize=8)
    ax.grid(color=BORDER, alpha=0.3, lw=0.5)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)
    ax.legend(facecolor=PANEL, edgecolor=BORDER, labelcolor=TXT, loc="upper left")
    fig.subplots_adjust(right=0.92)
    return fig


# ───────────────────────── página ─────────────────────────
st.title("💼 Mi Portafolio")
ops, cap, mapeo = cargar(F_OPS, COL_OPS), cargar(F_CAP, COL_CAP), cargar(F_MAP, COL_MAP)
if st.session_state.get("msg"):
    st.success(st.session_state.pop("msg"))

with st.expander("📥 Importar CSV de Google Sheets (operaciones o capital)"):
    subidos = st.file_uploader("CSV", type="csv", accept_multiple_files=True)
    if subidos and st.button("Importar (reemplaza esa sección)"):
        res = []
        for f in subidos:
            k, d = importar(pd.read_csv(f, dtype=str))
            if k == "ops":
                guardar(d, F_OPS); res.append(f"{len(d)} operaciones")
            elif k == "cap":
                guardar(d, F_CAP); res.append(f"{len(d)} movimientos de capital")
            else:
                res.append(f"{f.name}: columnas no reconocidas")
        st.session_state["msg"] = "Importado: " + ", ".join(res)
        st.rerun()

simb = sorted(limpiar_ops(ops)["SIMBOLO"].unique())
ymap = yahoo_de(simb, mapeo)
manual = mapeo.dropna(subset=["PRECIO_MANUAL"]).set_index("SIMBOLO")["PRECIO_MANUAL"].to_dict()
precios = pd.DataFrame()
if simb:
    inicio = min(ops["FECHA"].dropna()) - timedelta(days=7)
    precios = bajar(tuple(sorted(set(ymap.values()) | {"^GSPC", "USDMXN=X"})), str(inicio))


def ultimo(s):
    y = ymap[s]
    if y in precios and precios[y].dropna().size:
        return float(precios[y].dropna().iloc[-1])
    return manual.get(s)


pos = posiciones(ops)
filas = []
for s, p in sorted(pos.items()):
    if p["q"] > 1e-9:
        px = ultimo(s)
        val = p["q"] * px if px else None
        filas.append({"Símbolo": s, "Cantidad": p["q"], "Costo prom.": p["c"] / p["q"], "Precio": px,
                      "Valor": val, "G/P": val - p["c"] if val else None,
                      "G/P %": (val / p["c"] - 1) * 100 if val and p["c"] else None})
tabla = pd.DataFrame(filas)
valor_total = tabla["Valor"].sum() if len(tabla) else 0.0
costo = sum(p["c"] for p in pos.values() if p["q"] > 1e-9)
neto = cap.dropna(subset=["IMPORTE"]).assign(s=lambda d: np.where(d["TIPO"] == "INGRESO", 1, -1) * d["IMPORTE"])["s"].sum()
realizada = sum(p["r"] for p in pos.values())

m = st.columns(5)
m[0].metric("Capital aportado", f"${neto:,.2f}")
m[1].metric("Costo invertido", f"${costo:,.2f}")
m[2].metric("Valor actual", f"${valor_total:,.2f}")
m[3].metric("Ganancia no realizada", f"${valor_total - costo:,.2f}")
m[4].metric("Ganancia realizada", f"${realizada:,.2f}")

t1, t2, t3, t4, t5 = st.tabs(["Portafolio", "Rendimiento", "Operaciones", "Capital", "Precios y mapeo"])

with t1:
    if tabla.empty:
        st.info("Aún no hay posiciones. Importa tus CSV o registra una compra en Operaciones.")
    else:
        tabla["Peso %"] = tabla["Valor"] / valor_total * 100 if valor_total else None
        st.dataframe(tabla.sort_values("Valor", ascending=False), hide_index=True, use_container_width=True,
                     column_config={"Cantidad": st.column_config.NumberColumn(format="%.4g"),
                                    **{c: st.column_config.NumberColumn(format="$%.2f") for c in ("Costo prom.", "Precio", "Valor", "G/P")},
                                    **{c: st.column_config.NumberColumn(format="%.2f%%") for c in ("G/P %", "Peso %")}})
        if tabla["Precio"].isna().any():
            st.warning("Sin precio: " + ", ".join(tabla[tabla["Precio"].isna()]["Símbolo"]) + ". Corrige el mapeo en la pestaña Precios y mapeo.")

with t2:
    if not simb:
        st.info("Necesitas operaciones para calcular el rendimiento.")
    else:
        c1, c2 = st.columns([3, 2])
        rango = c1.radio("Rango", ["1m", "6m", "YTD", "1a", "5a", "TODO"], index=3, horizontal=True)
        en_mxn = c2.checkbox("S&P 500 en pesos (ajustado por USD/MXN)", value=True)
        df, faltan = rendimiento(ops, precios, ymap, en_mxn)
        if faltan:
            st.warning("No se incluyen en la gráfica por falta de precios en Yahoo: " + ", ".join(faltan))
        if len(df) < 2:
            st.info("No hay suficientes datos para graficar.")
        else:
            hoy = pd.Timestamp(df.index[-1])
            corte = {"1m": hoy - pd.DateOffset(months=1), "6m": hoy - pd.DateOffset(months=6), "1a": hoy - pd.DateOffset(years=1),
                     "5a": hoy - pd.DateOffset(years=5), "YTD": pd.Timestamp(hoy.year, 1, 1), "TODO": df.index[0]}[rango]
            sub = df[df.index >= corte]
            if len(sub) < 2:
                st.info("Ese rango tiene muy pocos datos todavía.")
            else:
                sub = sub / sub.iloc[0] - 1
                st.pyplot(grafica(sub), use_container_width=True)
                st.caption("El rendimiento del portafolio no cuenta aportes ni retiros. Asume que las operaciones se hicieron al cierre del día.")

with t3:
    ed = st.data_editor(ops, num_rows="dynamic", hide_index=True, use_container_width=True, key="ed_ops",
                        column_config={"FECHA": st.column_config.DateColumn(format="YYYY-MM-DD", required=True),
                                       "TIPO": st.column_config.SelectboxColumn(options=["COMPRA", "VENTA"], required=True),
                                       "MERCADO": st.column_config.SelectboxColumn(options=["BMV", "SIC"])})
    if st.button("💾 Guardar operaciones"):
        ed["SIMBOLO"] = ed["SIMBOLO"].astype(str).str.strip().str.upper()
        guardar(ed.dropna(subset=["FECHA", "SIMBOLO", "CANTIDAD", "PRECIO"]), F_OPS)
        st.session_state["msg"] = "Operaciones guardadas"
        st.rerun()
    st.download_button("⬇️ Descargar CSV", ops.to_csv(index=False), "operaciones.csv", "text/csv")

with t4:
    ed = st.data_editor(cap, num_rows="dynamic", hide_index=True, use_container_width=True, key="ed_cap",
                        column_config={"FECHA": st.column_config.DateColumn(format="YYYY-MM-DD", required=True),
                                       "TIPO": st.column_config.SelectboxColumn(options=["INGRESO", "EGRESO"], required=True)})
    if st.button("💾 Guardar capital"):
        guardar(ed.dropna(subset=["FECHA", "IMPORTE"]), F_CAP)
        st.session_state["msg"] = "Capital guardado"
        st.rerun()
    st.download_button("⬇️ Descargar CSV", cap.to_csv(index=False), "capital.csv", "text/csv")

with t5:
    st.caption("Por defecto el símbolo de Yahoo es SÍMBOLO + .MX (ej. FUNO11.MX). Cámbialo si no encuentra precio, "
               "o captura un precio manual de respaldo.")
    base = pd.DataFrame({"SIMBOLO": pd.Series(simb, dtype="object")}).merge(
        mapeo.astype({"SIMBOLO": "object"}), on="SIMBOLO", how="left")
    base["YAHOO"] = base["YAHOO"].fillna(pd.Series([ymap[s] for s in base["SIMBOLO"]], index=base.index))
    em = st.data_editor(base, hide_index=True, use_container_width=True, key="ed_map", disabled=["SIMBOLO"])
    if st.button("💾 Guardar mapeo"):
        guardar(em, F_MAP)
        bajar.clear()
        st.session_state["msg"] = "Mapeo guardado"
        st.rerun()
    if st.button("🔄 Actualizar precios ahora"):
        bajar.clear()
        st.rerun()
