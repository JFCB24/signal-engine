import pandas as pd
import pickle
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.settings import (
    TICKER, FEATURES, UMBRAL_SENAL, UMBRAL_CONFIANZA_ALTA, UMBRAL_CONFIANZA_MEDIA,
)
from models.train import RUTA_MODELO
from models.registro import registrar_senal


def generar_senal(ticker=TICKER, registrar=True):
    if not os.path.exists(RUTA_MODELO):
        print("Error: primero ejecuta models/train.py")
        return None

    with open(RUTA_MODELO, "rb") as f:
        modelo = pickle.load(f)

    ruta = f"data/processed/{ticker.replace('-', '_')}_features.csv"
    if not os.path.exists(ruta):
        print("Error: primero ejecuta feature_engineering.py")
        return None

    df = pd.read_csv(ruta, index_col="Date", parse_dates=True)

    # Última fila = último día con datos (su label es NaN y no se usa aquí)
    features_disponibles = [f for f in FEATURES if f in df.columns]
    ultima_fila = df[features_disponibles].iloc[-1:]

    probabilidades = modelo.predict_proba(ultima_fila)[0]
    prob_bajista = probabilidades[0]
    prob_alcista = probabilidades[1]

    if prob_alcista >= UMBRAL_SENAL:
        senal, emoji = "ALCISTA", "▲"
    elif prob_bajista >= UMBRAL_SENAL:
        senal, emoji = "BAJISTA", "▼"
    else:
        senal, emoji = "NEUTRAL", "◆"

    confianza_max = max(prob_alcista, prob_bajista)
    if confianza_max >= UMBRAL_CONFIANZA_ALTA:
        confianza = "ALTA"
    elif confianza_max >= UMBRAL_CONFIANZA_MEDIA:
        confianza = "MEDIA"
    else:
        confianza = "BAJA"

    fecha_hoy = df.index[-1].date()
    precio_actual = df["close"].iloc[-1]

    print("=" * 45)
    print(f"  SEÑAL DE INVERSIÓN — {ticker}")
    print("=" * 45)
    print(f"  Fecha          : {fecha_hoy}")
    print(f"  Precio actual  : ${precio_actual:,.2f}")
    print(f"  Señal          : {emoji} {senal}")
    print(f"  Prob. alcista  : {prob_alcista:.1%}")
    print(f"  Prob. bajista  : {prob_bajista:.1%}")
    print(f"  Confianza      : {confianza}")
    print("=" * 45)
    print("  ⚠ Herramienta educativa, no asesoría financiera")
    print("=" * 45)

    resultado = {
        "fecha": str(fecha_hoy),
        "ticker": ticker,
        "precio": float(precio_actual),
        "senal": senal,
        "prob_alcista": round(float(prob_alcista), 4),
        "prob_bajista": round(float(prob_bajista), 4),
        "confianza": confianza,
    }
    if registrar:
        registrar_senal(resultado)
    return resultado


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    generar_senal()
