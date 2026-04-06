import streamlit as st
import pandas as pd
import pickle
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.settings import FEATURES, ACTIVOS, NOTICIAS_TERMINOS
from data.processors.feature_engineering import calcular_features
from data.collectors.news_collector import obtener_noticias, analizar_sentimiento

st.set_page_config(
    page_title="LatixIA — Señales de Inversión",
    page_icon="📈",
    layout="centered"
)

HORIZONTES = {
    "24 horas": 1,
    "1 semana": 7,
    "1 mes":    30,
}

def preparar_sistema():
    from config.settings import TICKER
    ticker_safe = TICKER.replace("-", "_")
    if not os.path.exists(f"data/raw/{ticker_safe}_precios.csv"):
        from data.collectors.price_collector import descargar_precios
        descargar_precios()
    if not os.path.exists(f"data/processed/{ticker_safe}_features.csv"):
        from data.processors.feature_engineering import procesar_datos
        procesar_datos()
    if not os.path.exists("models/modelo_lgbm.pkl"):
        from models.train import entrenar_modelo
        entrenar_modelo()

@st.cache_data(ttl=3600)
def verificar_activos():
    import yfinance as yf
    resultado = {}
    for mercado, activos in ACTIVOS.items():
        resultado[mercado] = {}
        for nombre, ticker in activos.items():
            try:
                datos = yf.download(
                    ticker, period="1mo", interval="1d",
                    auto_adjust=True, progress=False
                )
                resultado[mercado][nombre] = len(datos) >= 5
            except:
                resultado[mercado][nombre] = False
    return resultado

def guardar_historial(ticker, activo_nombre, prob_alcista,
                      prob_bajista, precio):
    historial_path = "data/signals_history.csv"
    nueva_fila = {
        "fecha": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
        "ticker": ticker,
        "activo": activo_nombre,
        "prob_alcista": round(prob_alcista, 4),
        "prob_bajista": round(prob_bajista, 4),
        "precio_entrada": round(precio, 2),
    }
    if os.path.exists(historial_path):
        historial = pd.read_csv(historial_path)
        historial = pd.concat([historial, pd.DataFrame([nueva_fila])],
                              ignore_index=True)
    else:
        historial = pd.DataFrame([nueva_fila])
    os.makedirs("data", exist_ok=True)
    historial.to_csv(historial_path, index=False)

def analizar_activo(ticker, activo_nombre, perfil):
    with st.spinner("Descargando datos históricos..."):
        import yfinance as yf
        datos = yf.download(
            ticker, period="3y", interval="1d",
            auto_adjust=True, progress=False
        )
        if datos.empty or len(datos) < 50:
            st.warning(f"⚠️ **{activo_nombre}** no tiene suficientes datos.")
            st.info("Elige un activo marcado con ✓ en el selector.")
            return None
        datos.columns = ["open", "high", "low", "close", "volume"]
        datos.dropna(inplace=True)
        df = calcular_features(datos.copy())

    with st.spinner("Obteniendo noticias en tiempo real..."):
        titulares = obtener_noticias(ticker)
        score_sentimiento, etiqueta_sentimiento = analizar_sentimiento(titulares)

    ruta_modelo = "models/modelo_lgbm.pkl"
    if not os.path.exists(ruta_modelo):
        st.error("Modelo no encontrado.")
        return None

    with open(ruta_modelo, "rb") as f:
        modelo = pickle.load(f)

    features_disponibles = [f for f in FEATURES if f in df.columns]
    ultima_fila = df[features_disponibles].iloc[-1:]

    probabilidades = modelo.predict_proba(ultima_fila)[0]
    prob_bajista = probabilidades[0]
    prob_alcista = probabilidades[1]

    row = df.iloc[-1]

    guardar_historial(ticker, activo_nombre, prob_alcista,
                      prob_bajista, row["close"])

    señales = []
    if row["rsi"] < 35:     señales.append(1)
    elif row["rsi"] > 65:   señales.append(-1)
    else:                    señales.append(0)
    if row["macd"] > row["macd_signal"]: señales.append(1)
    else:                                 señales.append(-1)
    if row["bb_position"] < 0.2:   señales.append(1)
    elif row["bb_position"] > 0.8: señales.append(-1)
    else:                           señales.append(0)

    señal_dominante = 1 if prob_alcista > prob_bajista else -1
    consistencia = sum(1 for s in señales if s == señal_dominante) / len(señales)
    atr_norm = row["atr"] / row["close"]
    estabilidad = max(0, 1 - (atr_norm * 20))
    confianza_num = (max(prob_alcista, prob_bajista) * 0.5 +
                     consistencia * 0.3 +
                     estabilidad * 0.2)

    if confianza_num >= 0.65:   confianza = "Alta"
    elif confianza_num >= 0.55: confianza = "Media"
    else:                        confianza = "Baja"

    if atr_norm > 0.04:   riesgo = "Alto"
    elif atr_norm > 0.02: riesgo = "Medio"
    else:                  riesgo = "Bajo"

    if prob_alcista >= 0.58:   señal = "ALCISTA"
    elif prob_bajista >= 0.58: señal = "BAJISTA"
    else:                       señal = "NEUTRAL"

    umbrales = {"Conservador": 0.65, "Moderado": 0.58, "Agresivo": 0.53}
    umbral = umbrales[perfil]

    if señal == "ALCISTA" and prob_alcista >= umbral:
        recomendacion = "Condiciones favorables para entrar"
        rec_color = "success"
    elif señal == "BAJISTA" and prob_bajista >= umbral:
        recomendacion = "Considerar mantenerse fuera"
        rec_color = "error"
    else:
        recomendacion = "Esperar señal más clara"
        rec_color = "warning"

    return {
        "ticker":               ticker,
        "precio":               row["close"],
        "señal":                señal,
        "prob_alcista":         prob_alcista,
        "prob_bajista":         prob_bajista,
        "confianza":            confianza,
        "riesgo":               riesgo,
        "recomendacion":        recomendacion,
        "rec_color":            rec_color,
        "rsi":                  row["rsi"],
        "macd":                 row["macd"],
        "macd_signal":          row["macd_signal"],
        "bb_position":          row["bb_position"],
        "volume_ratio":         row["volume_ratio"],
        "fecha":                df.index[-1].date(),
        "sentimiento_score":    score_sentimiento,
        "sentimiento_etiqueta": etiqueta_sentimiento,
        "titulares":            titulares[:5],
    }


# ── Inicializar ──────────────────────────────────────────────
with st.spinner("Iniciando LatixIA..."):
    preparar_sistema()

# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding: 1.5rem 0 0.5rem;'>
    <div style='display:inline-block; background:#0D1B2A;
                border-radius:16px; padding:1.2rem 2.5rem;
                margin-bottom:1rem;'>
        <div style='display:flex; align-items:center;
                    justify-content:center; gap:16px;'>
            <svg width="48" height="48" viewBox="0 0 48 48">
                <rect x="4" y="20" width="6" height="16" rx="1.5" fill="#1A6FFF"/>
                <line x1="7" y1="14" x2="7" y2="20" stroke="#1A6FFF" stroke-width="1.5"/>
                <line x1="7" y1="36" x2="7" y2="42" stroke="#1A6FFF" stroke-width="1.5"/>
                <rect x="14" y="12" width="6" height="22" rx="1.5" fill="#00C896"/>
                <line x1="17" y1="6" x2="17" y2="12" stroke="#00C896" stroke-width="1.5"/>
                <line x1="17" y1="34" x2="17" y2="40" stroke="#00C896" stroke-width="1.5"/>
                <rect x="24" y="16" width="6" height="14" rx="1.5" fill="#1A6FFF"/>
                <line x1="27" y1="10" x2="27" y2="16" stroke="#1A6FFF" stroke-width="1.5"/>
                <line x1="27" y1="30" x2="27" y2="38" stroke="#1A6FFF" stroke-width="1.5"/>
                <rect x="34" y="8" width="6" height="24" rx="1.5" fill="#00C896"/>
                <line x1="37" y1="2" x2="37" y2="8" stroke="#00C896" stroke-width="1.5"/>
                <line x1="37" y1="32" x2="37" y2="40" stroke="#00C896" stroke-width="1.5"/>
            </svg>
            <div style='text-align:left;'>
                <div style='font-size:2rem; font-weight:700;
                            color:#FFFFFF; letter-spacing:2px;
                            line-height:1;'>LATIX</div>
                <div style='font-size:10px; color:#00C896;
                            letter-spacing:4px;'>INTELIGENCIA ARTIFICIAL</div>
            </div>
        </div>
        <div style='color:#FFFFFF; font-size:13px;
                    margin-top:10px; opacity:0.85;
                    font-style:italic;'>
            Invierte diferente. Invierte inteligente.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Verificar activos ────────────────────────────────────────
with st.spinner("Verificando activos disponibles..."):
    disponibles = verificar_activos()

# ── Selectores ───────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    mercado = st.selectbox("Mercado", list(ACTIVOS.keys()))
with col2:
    activos_con_estado = {
        f"{'✓' if disponibles[mercado].get(n, False) else '✗'} {n}": t
        for n, t in ACTIVOS[mercado].items()
    }
    seleccion = st.selectbox("Activo", list(activos_con_estado.keys()))
    activo_nombre = seleccion.replace("✓ ", "").replace("✗ ", "")
with col3:
    perfil = st.selectbox("Tu perfil", ["Conservador", "Moderado", "Agresivo"])

horizonte = st.selectbox("Horizonte de tiempo", list(HORIZONTES.keys()))
ticker_seleccionado = ACTIVOS[mercado][activo_nombre]
disponible = disponibles[mercado].get(activo_nombre, False)

st.caption(f"Ticker: `{ticker_seleccionado}` — "
           f"{'✓ Disponible' if disponible else '✗ Sin datos suficientes'}")
st.caption(f"Datos actualizados: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}")

st.divider()

# ── Botón ────────────────────────────────────────────────────
if st.button("🔍 Analizar ahora", use_container_width=True,
             disabled=not disponible):

    resultado = analizar_activo(ticker_seleccionado, activo_nombre, perfil)

    if resultado:
        if resultado["señal"] == "ALCISTA":
            color = "green"
            icono = "▲"
        elif resultado["señal"] == "BAJISTA":
            color = "red"
            icono = "▼"
        else:
            color = "gray"
            icono = "◆"

        st.markdown(f"""
        <div style='text-align:center; padding:1.5rem;
                    border-radius:12px; border:1.5px solid {color};
                    margin-bottom:1rem;'>
            <div style='font-size:13px; color:gray; margin-bottom:4px;'>
                {activo_nombre} · {horizonte} · Perfil {perfil}
            </div>
            <div style='font-size:2.5rem; font-weight:700; color:{color};'>
                {icono} {resultado["señal"]}
            </div>
            <div style='font-size:13px; color:gray; margin-top:4px;'>
                Fecha: {resultado["fecha"]} · Precio: ${resultado["precio"]:,.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Prob. alcista", f"{resultado['prob_alcista']:.1%}",
                      delta="vs 50% azar")
        with c2:
            st.metric("Confianza", resultado["confianza"])
        with c3:
            st.metric("Riesgo", resultado["riesgo"])
        with c4:
            st.metric("Sentimiento",
                      resultado["sentimiento_etiqueta"].capitalize(),
                      delta=f"{resultado['sentimiento_score']:+.2f}")

        st.divider()
        st.subheader("📊 Precio histórico — últimos 3 meses")

        import yfinance as yf
        precios = yf.download(
            ticker_seleccionado,
            period="3mo",
            interval="1d",
            auto_adjust=True,
            progress=False
        )

        if not precios.empty:
            precios.columns = ["open", "high", "low", "close", "volume"]
            precio_chart = precios[["close"]].copy()
            precio_chart.columns = ["Precio de cierre"]
            st.line_chart(precio_chart)

            cm1, cm2, cm3 = st.columns(3)
            with cm1:
                st.metric("Mínimo 3 meses",
                          f"${precios['close'].min():,.2f}")
            with cm2:
                st.metric("Máximo 3 meses",
                          f"${precios['close'].max():,.2f}")
            with cm3:
                cambio = ((precios['close'].iloc[-1] - precios['close'].iloc[0])
                          / precios['close'].iloc[0] * 100)
                st.metric("Variación 3 meses", f"{cambio:+.1f}%")

        st.divider()
        st.subheader("Factores de la señal")

        def mostrar_factor(nombre, valor, umbral_bajo, umbral_alto, desc):
            if valor <= umbral_bajo:
                badge = "🟢 Alcista"
            elif valor >= umbral_alto:
                badge = "🔴 Bajista"
            else:
                badge = "🟡 Neutral"
            st.markdown(f"**{nombre}** — {badge}  \n{desc} `{valor:.2f}`")

        mostrar_factor("RSI", resultado["rsi"], 35, 65,
                       "Sobrevendido < 35 / Sobrecomprado > 65 →")
        mostrar_factor("Posición Bollinger", resultado["bb_position"], 0.2, 0.8,
                       "Cerca del soporte < 0.2 / Resistencia > 0.8 →")
        mostrar_factor("Volumen relativo", resultado["volume_ratio"], 0.8, 1.5,
                       "Alto = mayor interés del mercado →")

        st.divider()
        st.subheader("📰 Noticias en tiempo real")
        for titular in resultado["titulares"]:
            st.markdown(f"- {titular}")

        st.divider()
        if resultado["rec_color"] == "success":
            st.success(f"✅ {resultado['recomendacion']}")
        elif resultado["rec_color"] == "error":
            st.error(f"🚫 {resultado['recomendacion']}")
        else:
            st.warning(f"⏳ {resultado['recomendacion']}")

        st.subheader("Probabilidades")
        prob_df = pd.DataFrame({
            "Dirección": ["Alcista ▲", "Bajista ▼"],
            "Probabilidad": [resultado["prob_alcista"],
                             resultado["prob_bajista"]]
        })
        st.bar_chart(prob_df.set_index("Dirección"))

        st.divider()
        st.subheader("📋 Historial de análisis")
        historial_path = "data/signals_history.csv"
        if os.path.exists(historial_path):
            hist_df = pd.read_csv(historial_path)
            hist_df = hist_df.sort_values("fecha",
                                          ascending=False).head(10)
            hist_df.columns = ["Fecha", "Ticker", "Activo",
                               "Prob. Alcista", "Prob. Bajista",
                               "Precio entrada"]
            st.dataframe(hist_df, use_container_width=True)
        else:
            st.info("El historial aparecerá aquí después del primer análisis.")

        st.divider()
        st.warning(
            "⚠️ LatixIA es una herramienta educativa y no constituye asesoría "
            "financiera. Las señales se basan en patrones históricos y no "
            "garantizan resultados futuros. Investiga siempre por tu cuenta."
        )

else:
    if not disponible:
        st.warning(f"⚠️ **{activo_nombre}** no tiene datos suficientes. "
                   "Elige un activo marcado con ✓.")
    else:
        st.markdown("""
        <div style='text-align:center; padding:1rem 0 2rem;'>
            <p style='font-size:16px; color:gray;'>
                Selecciona un mercado y un activo, luego presiona
                <strong>Analizar</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Activos cubiertos", "50+")
        with c2:
            st.metric("Mercados", "9")
        with c3:
            st.metric("Años de datos", "3")

        st.divider()
        st.markdown("#### ¿Cómo funciona?")

        col1, col2 = st.columns(2)
        with col1:
            st.success("📥 **Datos reales**\n\nDescarga precios históricos en tiempo real de Yahoo Finance")
            st.success("🧠 **Modelo IA**\n\nLightGBM entrenado con 3 años de datos históricos")
        with col2:
            st.info("📰 **Noticias en tiempo real**\n\nRSS de Yahoo Finance y Google News actualizado diariamente")
            st.info("🌎 **Mercados globales**\n\nUSA, China, Latam, criptos y materias primas")

        st.divider()
        st.markdown("#### Mercados disponibles")

        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.markdown("🪙 **Criptos**\nBTC, ETH, SOL, BNB, ADA")
        with m2:
            st.markdown("🇺🇸 **USA**\nApple, Tesla, NVIDIA, Google")
        with m3:
            st.markdown("🇨🇳 **China**\nAlibaba, Baidu, NIO, JD.com")
        with m4:
            st.markdown("🌎 **Latam**\nColombia, México, Brasil, Argentina")
        with m5:
            st.markdown("🌍 **Materias primas**\nOro, Plata, Petróleo, Trigo")

        st.divider()
        st.markdown("""
        <div style='text-align:center; padding:0.5rem 0;'>
            <p style='font-size:12px; color:gray;'>
                ⚠️ LatixIA es una herramienta educativa — no constituye
                asesoría financiera
            </p>
        </div>
        """, unsafe_allow_html=True