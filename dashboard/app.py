import streamlit as st
import pandas as pd
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.settings import ACTIVOS, NOTICIAS_TERMINOS
from data.processors.feature_engineering import calcular_features
from data.collectors.news_collector import obtener_noticias, analizar_sentimiento

st.set_page_config(
    page_title="LatixIA — Análisis técnico",
    page_icon="📈",
    layout="centered"
)

RUTA_REGISTRO = "data/registro_senales.csv"
RUTA_EVALUACION = "reportes/walkforward.json"
TICKER_EXPERIMENTO = "BTC-USD"   # único activo con prueba en vivo


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


def analizar_activo(ticker, activo_nombre):
    import yfinance as yf
    with st.spinner("Descargando datos..."):
        datos = yf.download(ticker, period="2y", interval="1d",
                            auto_adjust=True, progress=False)
        if datos.empty or len(datos) < 260:
            st.warning(f"⚠️ **{activo_nombre}** no tiene suficientes datos.")
            return None
        datos.columns = ["open", "high", "low", "close", "volume"]
        datos.dropna(inplace=True)
        df = calcular_features(datos.copy())

    with st.spinner("Leyendo titulares..."):
        titulares = obtener_noticias(ticker)
        score, etiqueta = analizar_sentimiento(titulares)

    fila = df.iloc[-1]
    precio_ayer = datos["close"].iloc[-2]
    return {
        "ticker": ticker,
        "fecha": df.index[-1].date(),
        "precio": float(fila["close"]),
        "cambio_dia": float(fila["close"] / precio_ayer - 1),
        "rsi": float(fila["rsi"]),
        "macd": float(fila["macd"]),
        "macd_signal": float(fila["macd_signal"]),
        "bb_position": float(fila["bb_position"]),
        "volumen_relativo": float(fila["volume_ratio"]),
        "volatilidad_diaria": float(fila["atr"] / fila["close"]),
        "tendencia_alcista": bool(fila["tendencia"]),
        "sentimiento_score": score,
        "sentimiento_etiqueta": etiqueta,
        "titulares": titulares[:5],
        "historico": datos[["close"]].tail(90),
    }


def zona_rsi(valor):
    if valor >= 70:  return "🔴 Sobrecompra (≥ 70): el precio subió mucho y rápido"
    if valor <= 30:  return "🟢 Sobreventa (≤ 30): el precio cayó mucho y rápido"
    return "⚪ Zona neutral (30–70)"


def zona_bollinger(valor):
    if valor >= 0.8:  return "🔴 Cerca de la banda superior"
    if valor <= 0.2:  return "🟢 Cerca de la banda inferior"
    return "⚪ En el centro de las bandas"


def zona_volumen(valor):
    if valor >= 1.5:  return "🔵 Volumen alto frente al promedio de 20 días"
    if valor <= 0.8:  return "⚪ Volumen bajo frente al promedio"
    return "⚪ Volumen normal"


def mostrar_prueba_en_vivo():
    st.subheader("🧪 Prueba en vivo (BTC-USD)")
    st.caption("El modelo registra su señal cada día antes de conocer el resultado. "
               "Esta es la única medición de rendimiento real del proyecto.")
    if not os.path.exists(RUTA_REGISTRO):
        st.info("La prueba empieza con la primera ejecución diaria.")
        return
    registro = pd.read_csv(RUTA_REGISTRO, dtype={"fecha": str})
    registro = registro[registro["ticker"] == TICKER_EXPERIMENTO]
    calificadas = registro[registro["acierto"].isin(["True", "False"])]
    total = len(calificadas)
    aciertos = int((calificadas["acierto"] == "True").sum())
    c1, c2, c3 = st.columns(3)
    c1.metric("Señales registradas", len(registro))
    c2.metric("Calificadas", total)
    c3.metric("Accuracy hasta hoy",
              f"{aciertos / total:.1%}" if total else "sin datos")
    if total < 60:
        st.caption("Con menos de 60 señales calificadas, el resultado no es concluyente.")
    st.dataframe(
        registro.sort_values("fecha", ascending=False).head(10)[
            ["fecha", "senal", "prob_alcista", "prob_bajista", "precio",
             "resultado", "acierto"]],
        width="stretch", hide_index=True)


def mostrar_evaluacion():
    st.subheader("📊 Evaluación del modelo")
    if not os.path.exists(RUTA_EVALUACION):
        st.info("Aún no hay evaluación. Ejecuta `python -m models.evaluar`.")
        return
    with open(RUTA_EVALUACION, encoding="utf-8") as f:
        rep = json.load(f)
    r = rep["resumen"]
    c = rep["backtest"]["control_azar"]
    st.markdown(
        f"- Accuracy del modelo fuera de muestra: **{r['accuracy_modelo_media']:.1%}** "
        f"(± {r['accuracy_modelo_desv']:.1%}) frente a **{r['baseline_siempre_sube_media']:.1%}** "
        f"de «siempre sube».\n"
        f"- Control de azar: p-valor **{c['p_valor']:.3f}** con {c['repeticiones']} desplazamientos.\n"
        f"- Esta evaluación cubre un periodo concreto. Un buen resultado en un periodo "
        f"no garantiza nada en otro."
    )


# ── Encabezado ───────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding: 1.5rem 0 0.5rem;'>
    <div style='display:inline-block; background:#0D1B2A;
                border-radius:16px; padding:1.2rem 2.5rem; margin-bottom:1rem;'>
        <div style='font-size:2rem; font-weight:700; color:#FFFFFF;
                    letter-spacing:2px; line-height:1;'>LATIX</div>
        <div style='font-size:10px; color:#00C896; letter-spacing:4px;'>ANÁLISIS TÉCNICO</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.warning(
    "**Herramienta educativa.** Muestra indicadores técnicos y los explica. "
    "No es una recomendación de compra ni de venta, ni asesoría financiera."
)

st.divider()

with st.spinner("Verificando activos disponibles..."):
    disponibles = verificar_activos()

col1, col2 = st.columns(2)
with col1:
    mercado = st.selectbox("Mercado", list(ACTIVOS.keys()))
with col2:
    activos_con_estado = {
        f"{'✓' if disponibles[mercado].get(n, False) else '✗'} {n}": t
        for n, t in ACTIVOS[mercado].items()
    }
    seleccion = st.selectbox("Activo", list(activos_con_estado.keys()))
    activo_nombre = seleccion.replace("✓ ", "").replace("✗ ", "")

ticker_seleccionado = ACTIVOS[mercado][activo_nombre]
disponible = disponibles[mercado].get(activo_nombre, False)
st.caption(f"Ticker: `{ticker_seleccionado}` — "
           f"{'✓ Disponible' if disponible else '✗ Sin datos suficientes'}")

if st.button("🔍 Ver indicadores", width="stretch", disabled=not disponible):
    resultado = analizar_activo(ticker_seleccionado, activo_nombre)

    if resultado:
        st.markdown(f"#### {activo_nombre} · {resultado['fecha']}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Precio de cierre", f"${resultado['precio']:,.2f}",
                  delta=f"{resultado['cambio_dia']:+.2%} hoy")
        c2.metric("Tendencia", "Alcista" if resultado["tendencia_alcista"] else "Bajista",
                  help="SMA50 por encima de SMA200 = alcista")
        c3.metric("Volatilidad diaria", f"{resultado['volatilidad_diaria']:.1%}",
                  help="ATR de 14 días dividido por el precio")

        st.subheader("Precio últimos 3 meses")
        st.line_chart(resultado["historico"].rename(columns={"close": "Cierre"}))

        st.subheader("Indicadores")
        st.markdown(
            f"**RSI (14):** `{resultado['rsi']:.1f}` — {zona_rsi(resultado['rsi'])}  \n"
            "Mide la velocidad de los cambios recientes de precio."
        )
        macd_lectura = ("MACD por encima de su señal (impulso alcista)"
                        if resultado["macd"] > resultado["macd_signal"]
                        else "MACD por debajo de su señal (impulso bajista)")
        st.markdown(
            f"**MACD:** `{resultado['macd']:.2f}` vs señal `{resultado['macd_signal']:.2f}` — "
            f"{macd_lectura}  \n"
            "Compara dos promedios exponenciales del precio."
        )
        st.markdown(
            f"**Posición en Bandas de Bollinger:** `{resultado['bb_position']:.2f}` — "
            f"{zona_bollinger(resultado['bb_position'])}  \n"
            "0 = banda inferior, 1 = banda superior."
        )
        st.markdown(
            f"**Volumen relativo:** `{resultado['volumen_relativo']:.2f}×` — "
            f"{zona_volumen(resultado['volumen_relativo'])}  \n"
            "Compara el volumen de hoy con el promedio de 20 días."
        )

        st.subheader("Titulares recientes")
        for titular in resultado["titulares"]:
            st.markdown(f"- {titular}")
        st.caption(
            f"Tono de los titulares: {resultado['sentimiento_etiqueta']} "
            f"({resultado['sentimiento_score']:+.2f}). Se calcula contando palabras "
            "positivas y negativas; no es un modelo de lenguaje ni predice precios."
        )

        st.divider()
        mostrar_prueba_en_vivo()
        st.divider()
        mostrar_evaluacion()

        st.divider()
        st.warning(
            "LatixIA es una herramienta educativa y no constituye asesoría financiera. "
            "Investiga siempre por tu cuenta."
        )
else:
    if not disponible:
        st.warning(f"⚠️ **{activo_nombre}** no tiene datos suficientes. "
                   "Elige un activo marcado con ✓.")
    else:
        st.info("Elige un mercado y un activo, y presiona **Ver indicadores**.")
    st.divider()
    mostrar_prueba_en_vivo()
    st.divider()
    mostrar_evaluacion()
