import json
import os
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.settings import ACTIVOS
from data.processors.feature_engineering import calcular_features
from data.collectors.news_collector import obtener_noticias, analizar_sentimiento

st.set_page_config(page_title="LatixIA · Análisis técnico", page_icon="📈", layout="centered")

RUTA_REGISTRO = "data/registro_senales.csv"
RUTA_EVALUACION = "reportes/walkforward.json"
TICKER_EXPERIMENTO = "BTC-USD"
SENALES_PARA_CONCLUIR = 60
AZUL, VERDE, ROJO, GRIS = "#1A6FFF", "#00C896", "#EF476F", "#8A94A6"

ESTILO = """
<style>
.hero {
    background: linear-gradient(135deg, #0D1B2A 0%, #123A63 60%, #0A6E7A 100%);
    border-radius: 18px; padding: 1.6rem 1.8rem; color: #FFFFFF;
    margin-bottom: 1.2rem; box-shadow: 0 8px 24px rgba(13,27,42,.18);
}
.hero .marca { font-size: 2rem; font-weight: 800; letter-spacing: 3px; line-height: 1; }
.hero .sub { font-size: 11px; color: #00C896; letter-spacing: 4px; margin-top: 4px; }
.hero .lema { font-size: 14px; opacity: .85; margin-top: 12px; }
.precio { font-size: 2.4rem; font-weight: 700; line-height: 1.1; }
.pill { display: inline-block; border-radius: 999px; padding: .2rem .7rem;
        font-size: .85rem; font-weight: 600; }
.pill-up { background: rgba(0,200,150,.15); color: #00A37A; }
.pill-down { background: rgba(239,71,111,.15); color: #D6335C; }
.pill-neutral { background: rgba(138,148,166,.18); color: #6B7689; }
.estado { font-weight: 600; margin-top: .3rem; }
.explica { color: #6B7689; font-size: .9rem; margin-top: .2rem; }
.aviso { border-left: 4px solid #FFB020; background: rgba(255,176,32,.08);
         padding: .8rem 1rem; border-radius: 8px; font-size: .92rem; }
</style>
"""


# ── Datos ────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def verificar_activos():
    import yfinance as yf
    resultado = {}
    for mercado, activos in ACTIVOS.items():
        resultado[mercado] = {}
        for nombre, ticker in activos.items():
            try:
                datos = yf.download(ticker, period="1mo", interval="1d",
                                    auto_adjust=True, progress=False)
                resultado[mercado][nombre] = len(datos) >= 5
            except Exception:
                resultado[mercado][nombre] = False
    return resultado


@st.cache_data(ttl=600)
def titulares_de(ticker):
    return obtener_noticias(ticker)


@st.cache_data(ttl=600)
def analizar(ticker):
    import yfinance as yf
    datos = yf.download(ticker, period="2y", interval="1d",
                        auto_adjust=True, progress=False)
    if datos.empty or len(datos) < 260:
        return None
    datos.columns = ["open", "high", "low", "close", "volume"]
    datos.dropna(inplace=True)
    df = calcular_features(datos.copy())

    titulares = titulares_de(ticker)
    score, etiqueta = analizar_sentimiento(titulares)
    fila = df.iloc[-1]
    return {
        "ticker": ticker,
        "fecha": df.index[-1].date(),
        "precio": float(fila["close"]),
        "cambio_dia": float(fila["close"] / datos["close"].iloc[-2] - 1),
        "rsi": float(fila["rsi"]),
        "macd": float(fila["macd"]),
        "macd_signal": float(fila["macd_signal"]),
        "bb_position": float(fila["bb_position"]),
        "volumen_relativo": float(fila["volume_ratio"]),
        "volatilidad": float(fila["atr"] / fila["close"]),
        "tendencia_alcista": bool(fila["tendencia"]),
        "sentimiento_score": score,
        "sentimiento_etiqueta": etiqueta,
        "titulares": titulares[:6],
        "grafico": df[["close", "sma20", "bb_upper", "bb_lower"]].tail(120),
    }


def cargar_registro():
    if not os.path.exists(RUTA_REGISTRO):
        return pd.DataFrame()
    registro = pd.read_csv(RUTA_REGISTRO, dtype={"fecha": str, "acierto": str})
    return registro[registro["ticker"] == TICKER_EXPERIMENTO].copy()


def cargar_evaluacion():
    if not os.path.exists(RUTA_EVALUACION):
        return None
    with open(RUTA_EVALUACION, encoding="utf-8") as f:
        return json.load(f)


# ── Componentes ──────────────────────────────────────────────

def pastilla(texto, tipo):
    return f'<span class="pill pill-{tipo}">{texto}</span>'


def render_cabecera(r, nombre):
    tipo = "up" if r["cambio_dia"] > 0 else "down" if r["cambio_dia"] < 0 else "neutral"
    st.markdown(f"##### {nombre} · {r['ticker']}")
    st.markdown(
        f'<div class="precio">${r["precio"]:,.2f}</div>'
        f'{pastilla(f"{r["cambio_dia"]:+.2%} hoy", tipo)} '
        f'<span class="explica">Cierre del {r["fecha"]}</span>',
        unsafe_allow_html=True)


def render_kpis(r):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Tendencia", "Alcista" if r["tendencia_alcista"] else "Bajista",
                  help="Compara la media de 50 días con la de 200 días. "
                       "Si la de 50 está arriba, la tendencia de fondo es alcista.")
    with c2:
        st.metric("Volatilidad diaria", f"{r['volatilidad']:.1%}",
                  help="Cuánto se mueve el precio en un día típico (ATR de 14 días).")
    with c3:
        st.metric("Tono de titulares", r["sentimiento_etiqueta"].capitalize(),
                  help="Conteo simple de palabras positivas y negativas en los titulares. "
                       "No es un modelo de lenguaje ni predice precios.")


def render_grafico(r):
    g = r["grafico"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=g.index, y=g["bb_upper"], line=dict(width=0),
                             hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=g.index, y=g["bb_lower"], line=dict(width=0),
                             fill="tonexty", fillcolor="rgba(26,111,255,0.08)",
                             name="Banda de Bollinger", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=g.index, y=g["close"], name="Cierre",
                             line=dict(color=AZUL, width=2.5)))
    fig.add_trace(go.Scatter(x=g.index, y=g["sma20"], name="Media 20 días",
                             line=dict(color=VERDE, width=1.5, dash="dot")))
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10),
                      hovermode="x unified",
                      legend=dict(orientation="h", y=1.12, x=0),
                      yaxis=dict(tickprefix="$", separatethousands=True),
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, width="stretch")
    st.caption("Últimos 120 días. La banda muestra dónde suele moverse el precio: "
               "un precio que sale de la banda es un movimiento poco común.")


def tarjeta(titulo, valor, progreso, estado, explicacion):
    with st.container(border=True):
        c1, c2 = st.columns([1, 1])
        c1.markdown(f"**{titulo}**")
        c2.markdown(f"<div style='text-align:right; font-weight:700'>{valor}</div>",
                    unsafe_allow_html=True)
        st.progress(min(max(progreso, 0.0), 1.0))
        st.markdown(f"<div class='estado'>{estado}</div>"
                    f"<div class='explica'>{explicacion}</div>",
                    unsafe_allow_html=True)


def render_indicadores(r):
    rsi = r["rsi"]
    if rsi >= 70:
        estado_rsi = "Sobrecompra: el precio subió rápido y puede frenarse"
    elif rsi <= 30:
        estado_rsi = "Sobreventa: el precio cayó rápido y puede rebotar"
    else:
        estado_rsi = "Zona neutral (entre 30 y 70)"
    tarjeta("RSI · 14 días", f"{rsi:.0f} / 100", rsi / 100, estado_rsi,
            "Mide la velocidad de los cambios recientes de precio.")

    macd_alcista = r["macd"] > r["macd_signal"]
    tarjeta("MACD", f"{r['macd']:.2f}", 0.75 if macd_alcista else 0.25,
            "Impulso alcista: el MACD está sobre su señal" if macd_alcista
            else "Impulso bajista: el MACD está bajo su señal",
            f"Señal: {r['macd_signal']:.2f}. Compara dos promedios del precio "
            "de distinta duración.")

    bb = r["bb_position"]
    if bb >= 0.8:
        estado_bb = "Cerca de la banda superior"
    elif bb <= 0.2:
        estado_bb = "Cerca de la banda inferior"
    else:
        estado_bb = "En el centro de las bandas"
    tarjeta("Posición en Bollinger", f"{bb:.2f}", bb, estado_bb,
            "0 = banda inferior · 1 = banda superior.")

    vol = r["volumen_relativo"]
    estado_vol = ("Volumen alto frente al promedio de 20 días" if vol >= 1.5
                  else "Volumen bajo frente al promedio" if vol <= 0.8
                  else "Volumen normal")
    tarjeta("Volumen relativo", f"{vol:.2f}×", vol / 2, estado_vol,
            "Compara el volumen de hoy con el promedio de los últimos 20 días. "
            "La barra llega al máximo en 2×.")

    v = r["volatilidad"]
    estado_v = ("Volatilidad baja" if v < 0.02
                else "Volatilidad moderada" if v < 0.04 else "Volatilidad alta")
    tarjeta("Volatilidad diaria", f"{v:.1%}", v / 0.10, estado_v,
            "Movimiento típico de un día. La barra llega al máximo en 10%.")


def render_titulares(r):
    if not r["titulares"]:
        st.info("No hay titulares recientes para este activo.")
        return
    for titular in r["titulares"]:
        st.markdown(f"- {titular}")
    st.caption("Fuente: RSS público de Yahoo Finance.")


def render_prueba_en_vivo():
    st.markdown("#### Prueba en vivo de BTC-USD")
    st.caption("Cada día el modelo registra su probabilidad de subida para mañana "
               "antes de conocer el resultado. Es la única medición de rendimiento real "
               "del proyecto.")
    registro = cargar_registro()
    total_registradas = len(registro)
    progreso = min(total_registradas / SENALES_PARA_CONCLUIR, 1.0)
    st.progress(progreso, text=f"{total_registradas} de {SENALES_PARA_CONCLUIR} "
                               "señales necesarias para una conclusión")
    if registro.empty:
        st.info("La prueba empieza con la primera ejecución diaria.")
        return

    calificadas = registro[registro["acierto"].isin(["True", "False"])]
    aciertos = int((calificadas["acierto"] == "True").sum())
    c1, c2, c3 = st.columns(3)
    c1.metric("Señales registradas", total_registradas)
    c2.metric("Calificadas", len(calificadas))
    c3.metric("Aciertos", f"{aciertos / len(calificadas):.0%}" if len(calificadas) else "—")
    if len(calificadas) < SENALES_PARA_CONCLUIR:
        st.caption("Con menos de 60 señales calificadas, el porcentaje de aciertos "
                   "no permite concluir nada.")

    tabla = registro.sort_values("fecha", ascending=False).head(15).copy()
    tabla["señal"] = tabla["senal"].map(
        {"ALCISTA": "▲ Alcista", "BAJISTA": "▼ Bajista", "NEUTRAL": "◆ Neutral"})
    tabla["acierto"] = tabla["acierto"].map(
        {"True": "✅", "False": "❌"}).fillna("—")
    tabla["prob_alcista"] = tabla["prob_alcista"] * 100
    st.dataframe(
        tabla[["fecha", "señal", "prob_alcista", "precio", "resultado", "acierto"]],
        hide_index=True, width="stretch",
        column_config={
            "fecha": "Fecha",
            "señal": "Señal",
            "prob_alcista": st.column_config.ProgressColumn(
                "Prob. de subida", format="%.0f%%", min_value=0, max_value=100),
            "precio": st.column_config.NumberColumn("Precio", format="$%.0f"),
            "resultado": "Resultado",
            "acierto": "Acertó",
        })


def render_metodologia():
    st.markdown("#### Qué es LatixIA")
    st.write("Una herramienta educativa que calcula indicadores técnicos sobre precios "
             "diarios y los explica en lenguaje simple. Además, mantiene una prueba en vivo "
             "de un modelo de probabilidad para BTC-USD.")

    st.markdown("#### Qué no es")
    st.write("No es una recomendación de compra ni de venta, ni asesoría financiera. "
             "El modelo no ha demostrado una ventaja frente al azar.")

    st.markdown("#### Evaluación del modelo")
    rep = cargar_evaluacion()
    if rep is None:
        st.info("Aún no hay evaluación disponible.")
    else:
        r = rep["resumen"]
        c1, c2 = st.columns(2)
        c1.metric("Acierto del modelo", f"{r['accuracy_modelo_media']:.1%}",
                  help="Porcentaje de días en que el modelo acertó la dirección del "
                       "día siguiente, en datos que no usó para entrenar.")
        c2.metric("Acierto de «siempre sube»", f"{r['baseline_siempre_sube_media']:.1%}",
                  help="Acertar siempre que el precio sube. Es el punto de comparación más simple.")
        st.markdown(
            '<div class="aviso"><b>En revisión.</b> El resultado del backtest no se muestra '
            'porque su magnitud no es creíble como pronóstico. Hasta resolverlo, no se '
            'debe usar para decidir nada.</div>', unsafe_allow_html=True)

    st.markdown("#### Límites")
    st.markdown(
        "- El modelo se entrena solo con BTC-USD, pero los indicadores funcionan para todos los activos.\n"
        "- Un buen resultado en un periodo no garantiza nada en otro.\n"
        "- El tono de titulares cuenta palabras; no es análisis de noticias.\n"
        "- Los datos vienen de Yahoo Finance y pueden tener retrasos o errores.")


# ── Página ───────────────────────────────────────────────────

st.markdown(ESTILO, unsafe_allow_html=True)
st.markdown("""
<div class="hero">
  <div class="marca">LATIX</div>
  <div class="sub">ANÁLISIS TÉCNICO</div>
  <div class="lema">Entiende los indicadores antes de decidir. Esta herramienta no da recomendaciones.</div>
</div>
""", unsafe_allow_html=True)

with st.spinner("Preparando activos..."):
    disponibles = verificar_activos()

mercados = [m for m in ACTIVOS if any(disponibles[m].values())]
col1, col2 = st.columns(2)
with col1:
    mercado = st.selectbox("Mercado", mercados)
with col2:
    nombres = [n for n, ok in disponibles[mercado].items() if ok]
    if not nombres:
        st.warning("Ningún activo de este mercado tiene datos disponibles ahora.")
        st.stop()
    activo = st.selectbox("Activo", nombres)

ocultos = sum(1 for ok in disponibles[mercado].values() if not ok)
if ocultos:
    st.caption(f"{ocultos} activo(s) de este mercado no tienen datos suficientes y están ocultos.")

ticker = ACTIVOS[mercado][activo]
if st.button("Ver indicadores", type="primary", width="stretch"):
    with st.spinner("Analizando..."):
        st.session_state["analisis"] = {"ticker": ticker, "nombre": activo,
                                        "resultado": analizar(ticker)}

analisis = st.session_state.get("analisis")
if analisis and analisis["ticker"] == ticker:
    r = analisis["resultado"]
    if r is None:
        st.warning(f"No hay datos suficientes para {activo} en este momento.")
    else:
        st.divider()
        render_cabecera(r, analisis["nombre"])
        render_kpis(r)
        tab_grafico, tab_indicadores, tab_titulares, tab_vivo, tab_metodo = st.tabs(
            ["Gráfico", "Indicadores", "Titulares", "Prueba en vivo", "Metodología"])
        with tab_grafico:
            render_grafico(r)
        with tab_indicadores:
            render_indicadores(r)
        with tab_titulares:
            render_titulares(r)
        with tab_vivo:
            if ticker == TICKER_EXPERIMENTO:
                render_prueba_en_vivo()
            else:
                st.info("La prueba en vivo solo existe para BTC-USD.")
                st.caption("Abre el activo Bitcoin para ver el registro.")
        with tab_metodo:
            render_metodologia()
else:
    st.info("Elige un activo y presiona **Ver indicadores**.")
    st.markdown("#### Qué vas a ver")
    st.markdown("- **Gráfico** del precio con su banda de volatilidad.\n"
                "- **Indicadores** explicados: RSI, MACD, Bollinger, volumen y volatilidad.\n"
                "- **Titulares** recientes.\n"
                "- **Prueba en vivo** del modelo y **metodología**, con sus límites.")

st.divider()
st.caption("LatixIA es una herramienta educativa. No constituye asesoría financiera. "
           "Investiga siempre por tu cuenta.")
