import pandas as pd
import pickle
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.settings import TICKER, FEATURES

def generar_señal():

    # Cargar modelo entrenado
    ruta_modelo = "models/modelo_lgbm.pkl"
    if not os.path.exists(ruta_modelo):
        print("Error: primero ejecuta models/train.py")
        return None

    with open(ruta_modelo, "rb") as f:
        modelo = pickle.load(f)

    # Cargar datos procesados
    ruta = f"data/processed/{TICKER.replace('-', '_')}_features.csv"
    if not os.path.exists(ruta):
        print("Error: primero ejecuta feature_engineering.py")
        return None

    df = pd.read_csv(ruta, index_col="Date", parse_dates=True)

    # Tomar la última fila — datos de hoy
    features_disponibles = [f for f in FEATURES if f in df.columns]
    ultima_fila = df[features_disponibles].iloc[-1:]

    # Generar predicción con probabilidad
    probabilidades = modelo.predict_proba(ultima_fila)[0]
    prob_bajista   = probabilidades[0]
    prob_alcista   = probabilidades[1]

    # Determinar señal
    if prob_alcista >= 0.60:
        señal = "ALCISTA"
        emoji = "▲"
    elif prob_bajista >= 0.60:
        señal = "BAJISTA"
        emoji = "▼"
    else:
        señal = "NEUTRAL"
        emoji = "◆"

    # Determinar confianza
    confianza_max = max(prob_alcista, prob_bajista)
    if confianza_max >= 0.70:
        confianza = "ALTA"
    elif confianza_max >= 0.60:
        confianza = "MEDIA"
    else:
        confianza = "BAJA"

    # Mostrar resultado
    fecha_hoy = df.index[-1].date()
    precio_actual = df["close"].iloc[-1]

    print("=" * 45)
    print(f"  SEÑAL DE INVERSIÓN — {TICKER}")
    print("=" * 45)
    print(f"  Fecha          : {fecha_hoy}")
    print(f"  Precio actual  : ${precio_actual:,.2f}")
    print(f"  Señal          : {emoji} {señal}")
    print(f"  Prob. alcista  : {prob_alcista:.1%}")
    print(f"  Prob. bajista  : {prob_bajista:.1%}")
    print(f"  Confianza      : {confianza}")
    print("=" * 45)
    print("  ⚠ Herramienta educativa, no asesoría financiera")
    print("=" * 45)

    return {
        "ticker": TICKER,
        "fecha": str(fecha_hoy),
        "precio": precio_actual,
        "señal": señal,
        "prob_alcista": round(prob_alcista, 4),
        "prob_bajista": round(prob_bajista, 4),
        "confianza": confianza
    }


if __name__ == "__main__":
    generar_señal()